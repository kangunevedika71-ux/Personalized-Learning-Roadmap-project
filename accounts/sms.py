"""
Pluggable SMS sending for OTPs.

Pick a backend with OTP_SMS_BACKEND in settings (or the env var of the same name):
  * accounts.sms.ConsoleBackend  - prints the OTP in the server terminal (default, for development)
  * accounts.sms.Fast2SMSBackend - Fast2SMS OTP API for India (needs API key and OTP template ID)
  * accounts.sms.Fast2SMSQuickBackend - Fast2SMS Quick SMS route for free-text SMS
  * accounts.sms.TwilioBackend   - real SMS through Twilio (needs TWILIO_* settings)

To add another provider (MSG91, ...), subclass BaseBackend and implement send().
"""
import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.utils.module_loading import import_string


class SMSError(Exception):
    pass


class BaseBackend:
    def send(self, number, message, code):
        raise NotImplementedError


class ConsoleBackend(BaseBackend):
    def send(self, number, message, code):
        print(f"\n[PathGen SMS to {number}] {message}\n", flush=True)


class TwilioBackend(BaseBackend):
    """Uses Twilio's REST API directly (no extra package needed)."""

    def send(self, number, message, code):
        sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        sender = getattr(settings, 'TWILIO_FROM_NUMBER', '')
        if not (sid and token and sender):
            raise SMSError("Twilio is not configured.")
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = urllib.parse.urlencode({'To': number, 'From': sender, 'Body': message}).encode()
        req = urllib.request.Request(url, data=data)
        auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
        req.add_header('Authorization', f'Basic {auth}')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                json.loads(resp.read().decode())
        except Exception as exc:  # network / auth / invalid number
            raise SMSError(str(exc)) from exc


class Fast2SMSBackend(BaseBackend):
    """
    Fast2SMS OTP API (India only). The account must have an OTP template registered
    with Fast2SMS/DLT. The app generates the code and Fast2SMS delivers that same code.
    """

    def send(self, number, message, code):
        api_key = getattr(settings, 'FAST2SMS_API_KEY', '')
        template_id = getattr(settings, 'FAST2SMS_OTP_TEMPLATE_ID', '')
        if not api_key or not template_id:
            raise SMSError("Fast2SMS requires FAST2SMS_API_KEY and FAST2SMS_OTP_TEMPLATE_ID.")
        if not number.startswith('+91') or len(number) != 13:
            raise SMSError("Fast2SMS OTP route only supports Indian (+91) numbers.")
        expiry_minutes = max(1, (getattr(settings, 'OTP_EXPIRY_SECONDS', 300) + 59) // 60)
        payload = json.dumps({
            'mobile': number[3:],
            'otp_id': template_id,
            'otp_expiry': expiry_minutes,
            'otp_length': len(code),
            'otp': code,
        }).encode()
        req = urllib.request.Request(
            'https://www.fast2sms.com/dev/otp/send', data=payload, method='POST'
        )
        req.add_header('Authorization', api_key)
        req.add_header('accept', 'application/json')
        req.add_header('content-type', 'application/json')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors='ignore')
            raise SMSError(f"Fast2SMS HTTP {exc.code}: {detail}") from exc
        except Exception as exc:
            raise SMSError(str(exc)) from exc
        if body.get('return') is False or body.get('status') in ('failed', 'error'):
            raise SMSError(f"Fast2SMS rejected the request: {body}")


class Fast2SMSQuickBackend(BaseBackend):
    """
    Fast2SMS "Quick SMS" route (route=q): free-text message, no DLT registration needed.
    India only. Fast2SMS charges a flat Rs 5 per message on this route, so it suits testing
    and small projects rather than many users.
    """

    def send(self, number, message, code):
        api_key = getattr(settings, 'FAST2SMS_API_KEY', '')
        if not api_key:
            raise SMSError("FAST2SMS_API_KEY is not set.")
        if not number.startswith('+91') or len(number) != 13:
            raise SMSError("Fast2SMS Quick SMS only supports Indian (+91) numbers.")
        params = urllib.parse.urlencode({
            'authorization': api_key,
            'route': 'q',
            'message': message,
            'numbers': number[3:],
            'flash': 0,
        })
        req = urllib.request.Request(f"https://www.fast2sms.com/dev/bulkV2?{params}")
        req.add_header('cache-control', 'no-cache')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors='ignore')
            raise SMSError(f"Fast2SMS HTTP {exc.code}: {detail}") from exc
        except Exception as exc:
            raise SMSError(str(exc)) from exc
        if not body.get('return'):
            raise SMSError(f"Fast2SMS rejected the request: {body}")


def send_otp_sms(number, code):
    backend = import_string(getattr(settings, 'OTP_SMS_BACKEND', 'accounts.sms.ConsoleBackend'))()
    minutes = getattr(settings, 'OTP_EXPIRY_SECONDS', 300) // 60
    backend.send(number, f"{code} is your PathGen verification code. It expires in {minutes} minutes. Do not share it with anyone.", code)
