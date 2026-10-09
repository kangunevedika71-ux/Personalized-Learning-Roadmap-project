import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PhoneNumber(models.Model):
    """A verified phone number that belongs to exactly one user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='phone')
    number = models.CharField(max_length=16, unique=True, help_text="E.164 format, e.g. +919876543210")
    verified_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.number


class PhoneOTP(models.Model):
    """
    One-time password sent to a phone number. Only a keyed hash of the code is stored,
    so a database leak does not reveal valid codes.
    """
    PURPOSE_LOGIN = 'LOGIN'
    PURPOSE_SIGNUP = 'SIGNUP'
    PURPOSE_CHOICES = [(PURPOSE_LOGIN, 'Login'), (PURPOSE_SIGNUP, 'Sign up')]

    number = models.CharField(max_length=16, db_index=True)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number} ({self.purpose}) @ {self.created_at:%Y-%m-%d %H:%M}"

    # ---- helpers ----
    @staticmethod
    def _hash(number, code):
        msg = f"{number}:{code}".encode()
        return hmac.new(settings.SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()

    @classmethod
    def issue(cls, number, purpose):
        """Create a fresh OTP, invalidating older unused ones. Returns (otp, plain_code)."""
        cls.objects.filter(number=number, is_used=False).update(is_used=True)
        length = getattr(settings, 'OTP_LENGTH', 6)
        code = ''.join(secrets.choice('0123456789') for _ in range(length))
        ttl = getattr(settings, 'OTP_EXPIRY_SECONDS', 300)
        otp = cls.objects.create(
            number=number, purpose=purpose, code_hash=cls._hash(number, code),
            expires_at=timezone.now() + timedelta(seconds=ttl),
        )
        return otp, code

    def verify(self, code):
        """
        Returns (ok, error_message). Counts every wrong guess; locks the OTP after
        OTP_MAX_ATTEMPTS so a 6-digit code cannot be brute-forced.
        """
        max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        if self.is_used:
            return False, "This OTP is no longer valid. Please request a new one."
        if timezone.now() > self.expires_at:
            return False, "This OTP has expired. Please request a new one."
        if self.attempts >= max_attempts:
            return False, "Too many wrong attempts. Please request a new OTP."

        self.attempts += 1
        if hmac.compare_digest(self.code_hash, self._hash(self.number, code)):
            self.is_used = True
            self.save(update_fields=['attempts', 'is_used'])
            return True, ''
        self.save(update_fields=['attempts'])
        left = max_attempts - self.attempts
        if left <= 0:
            return False, "Too many wrong attempts. Please request a new OTP."
        return False, f"Incorrect OTP. {left} attempt{'s' if left != 1 else ''} left."
