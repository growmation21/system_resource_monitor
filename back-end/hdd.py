import psutil
import logging

# Setup logging
logger = logging.getLogger(__name__)

def getDrivesInfo():
  hdds = []
  logger.debug('Getting HDDs info...')
  for partition in psutil.disk_partitions():
    hdds.append(partition.mountpoint)

  return hdds
