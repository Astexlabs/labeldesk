import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["LABELDESK_HOME"] = tempfile.mkdtemp(prefix="labeldesk-test-")
