import getpass
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from sys import platform

logfile_name = "nrg-parser.log"
try:
    username = getpass.getuser()

    if platform == "win32":
        home_dir = Path(f"C:/Users/{username}")
    else:
        home_dir = Path(f"/home/{username}")

    log_dir = home_dir / ".nrgpy"
    log_dir.mkdir(exist_ok=True)
    logfile = log_dir / logfile_name
except FileNotFoundError:
    logfile = logfile_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

f_handler = RotatingFileHandler(logfile, maxBytes=1024 * 1000, backupCount=4)
c_handler = logging.StreamHandler()

f_handler.setLevel(logging.DEBUG)
c_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(module)s:%(lineno)d] | %(message)s"
)

f_handler.setFormatter(formatter)
c_handler.setFormatter(formatter)

logger.addHandler(f_handler)
logger.addHandler(c_handler)
