from apscheduler.schedulers.background import BackgroundScheduler
import signal
from utils.mylogging import setup_logging
from controllers import fee

logger = setup_logging()

scheduler = BackgroundScheduler()


def handle_signal(signum, frame):
    scheduler.shutdown()


def run():
    try:
        scheduler.add_job(fee.update_rate_base_volume, trigger='cron', hour='00', minute='10')
        scheduler.start()
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        signal.pause()
    except Exception as e:
        logger.error(f"An error ocurred:{e}")


if __name__ == "__main__":
    run()
