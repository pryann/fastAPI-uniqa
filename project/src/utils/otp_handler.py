import pyotp


class OTPHandler:
    async def create_otp_secret(self) -> str:
        otp_secret = pyotp.random_base32()
        return otp_secret

    def generate_otp_code(self, otp_secret: str) -> str:
        totp = pyotp.TOTP(otp_secret)
        return totp.now()

    def verify_otp_code(self, otp_code: str, otp_secret: str) -> bool:
        totp = pyotp.TOTP(otp_secret)
        return totp.verify(otp_code, valid_window=1)
