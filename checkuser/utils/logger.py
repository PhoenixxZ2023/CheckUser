import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S',
)
