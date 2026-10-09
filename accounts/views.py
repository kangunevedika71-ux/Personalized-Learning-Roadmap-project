from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from roadmap.models import UserProfile
from .forms import LoginPhoneForm, OTPForm, SignUpPhoneForm
from .models import PhoneNumber, PhoneOTP
from .phone import mask_phone
from .sms import SMSError, send_otp_sms

SESSION_KEY = 'pending_auth'


def _cooldown():
    return getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 30)


def _send_limit():
    return getattr(settings, 'OTP_MAX_SENDS_PER_HOUR', 5)


def _send_otp(request, number, purpose):
    """Issue + send an OTP, enforcing resend cooldown and hourly cap. Returns (ok, error)."""
    now = timezone.now()
    recent = PhoneOTP.objects.filter(number=number, created_at__gte=now - timedelta(hours=1))
    if recent.count() >= _send_limit():
        return False, "Too many OTP requests for this number. Please try again in an hour."
    last = recent.first()
    if last and (now - last.created_at).total_seconds() < _cooldown():
        wait = int(_cooldown() - (now - last.created_at).total_seconds()) + 1
        return False, f"Please wait {wait} seconds before requesting another OTP."

    otp, code = PhoneOTP.issue(number, purpose)
    try:
        send_otp_sms(number, code)
    except SMSError as exc:
        print(f"\n[SMS ERROR] {exc}\n", flush=True)
        otp.delete()   # a failed send must not trigger the resend cooldown or hourly cap
        return False, "We couldn't send the SMS right now. Please try again in a moment."

    # Development convenience only: show the code on screen when no real SMS provider is set.
    if settings.DEBUG and getattr(settings, 'OTP_SHOW_CODE_IN_DEBUG', True) \
            and settings.OTP_SMS_BACKEND.endswith('ConsoleBackend'):
        messages.info(request, f"Development mode: your OTP is {code}")
    return True, ''


def _start(request, form_cls, purpose, template):
    if request.user.is_authenticated:
        return redirect('post-login')

    if request.method == 'POST':
        form = form_cls(request.POST)
        if form.is_valid():
            number = form.cleaned_data['phone']
            ok, error = _send_otp(request, number, purpose)
            if not ok:
                form.add_error('phone', error)
            else:
                request.session[SESSION_KEY] = {
                    'number': number,
                    'purpose': purpose,
                    'name': form.cleaned_data.get('name', ''),
                    'sent_at': timezone.now().timestamp(),
                }
                return redirect('verify-otp')
    else:
        form = form_cls()
    return render(request, template, {'form': form})


def signup_view(request):
    return _start(request, SignUpPhoneForm, PhoneOTP.PURPOSE_SIGNUP, 'signup.html')


def login_view(request):
    return _start(request, LoginPhoneForm, PhoneOTP.PURPOSE_LOGIN, 'login.html')


def _complete_login(request, pending):
    number, purpose = pending['number'], pending['purpose']
    if purpose == PhoneOTP.PURPOSE_SIGNUP:
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=number, first_name=pending.get('name', '')[:30]
                )
                user.set_unusable_password()
                user.save()
                PhoneNumber.objects.create(user=user, number=number)
                UserProfile.objects.get_or_create(user=user)
        except IntegrityError:
            # Someone registered this number between OTP send and verify.
            user = PhoneNumber.objects.get(number=number).user
        messages.success(request, "Phone verified! Let's set up your learning path.")
    else:
        user = PhoneNumber.objects.get(number=number).user
    login(request, user)


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect('post-login')
    pending = request.session.get(SESSION_KEY)
    if not pending:
        return redirect('login')

    number, purpose = pending['number'], pending['purpose']
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = PhoneOTP.objects.filter(number=number, purpose=purpose, is_used=False).first()
            if not otp:
                form.add_error('code', "This OTP is no longer valid. Please request a new one.")
            else:
                ok, error = otp.verify(form.cleaned_data['code'])
                if ok:
                    request.session.pop(SESSION_KEY, None)
                    _complete_login(request, pending)
                    return redirect('post-login')
                form.add_error('code', error)
    else:
        form = OTPForm()

    last = PhoneOTP.objects.filter(number=number).first()
    wait = 0
    if last:
        wait = max(0, int(_cooldown() - (timezone.now() - last.created_at).total_seconds()) + 1)
    return render(request, 'verify_otp.html', {
        'form': form, 'masked_number': mask_phone(number), 'purpose': purpose,
        'resend_wait': wait, 'ttl_minutes': getattr(settings, 'OTP_EXPIRY_SECONDS', 300) // 60,
    })


@require_POST
def resend_otp_view(request):
    pending = request.session.get(SESSION_KEY)
    if not pending:
        return redirect('login')
    ok, error = _send_otp(request, pending['number'], pending['purpose'])
    if ok:
        messages.success(request, "A new OTP has been sent.")
    else:
        messages.error(request, error)
    return redirect('verify-otp')


def change_number_view(request):
    request.session.pop(SESSION_KEY, None)
    return redirect('login')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
