import logging
import sys

logger = logging.getLogger('pyredis')

logger.setLevel(logging.DEBUG)

stdoutHandler = logging.StreamHandler(sys.stdout)
stderrHandler = logging.StreamHandler(sys.stderr)

# handler = logging.FileHandler('./pyredis.log')

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# handler.setFormatter(formatter)

logger.addHandler(stdoutHandler)
logger.addHandler(stderrHandler)