import signal
import traceback

from apscheduler.schedulers.background import BackgroundScheduler

from controllers import fee
from utils.mylogging import setup_logging

logger = setup_logging()

scheduler = BackgroundScheduler()


def handle_signal(signum, frame):
    scheduler.shutdown()


def run():
    try:
        logger.info("update-user-rate task startup")
        scheduler.add_job(
            fee.update_user_rate, trigger="cron", hour="01", minute="00"
        )
        scheduler.start()
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        signal.pause()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    run()
