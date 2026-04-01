from dotenv import load_dotenv
import os

load_dotenv(override=False)
OTP_EXPIRY_MIN = int(os.environ["OTP_EXPIRY_MIN"])
CHECKIN_INTERVAL_MINUTES = int(os.environ["CHECKIN_INTERVAL_MINUTES"])
GRACE_PERIOD_MINUTES = int(os.environ["GRACE_PERIOD_MINUTES"])