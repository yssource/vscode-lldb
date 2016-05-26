import sys
PY2 = sys.version_info[0] == 2 # type: bool
from .main import run_stdio_session, run_tcp_server
