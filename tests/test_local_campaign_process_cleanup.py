"""Exercise real nested processes without starting a mathematical search."""
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / 'scripts/run_local_verification.py'
spec = importlib.util.spec_from_file_location('campaign', MODULE)
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)

CHILD = """
import os, signal, sys, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
Path(sys.argv[1]).write_text(str(os.getpid()))
time.sleep(60)
"""
PARENT = """
import subprocess, sys, time
subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2]])
time.sleep(60)
"""


def await_pid(path):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if path.exists() and path.read_text().strip():
            return int(path.read_text())
        time.sleep(0.01)
    raise AssertionError('child did not become ready')


def is_running(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='],
                            capture_output=True, text=True)
    # Reparented zombie processes are terminated and consume no resources.
    return result.returncode == 0 and not result.stdout.strip().startswith('Z')


class ProcessCleanupTests(unittest.TestCase):
    def test_child_is_killed_after_leader_exits_on_sigterm(self):
        with tempfile.TemporaryDirectory() as tmp:
            ready = Path(tmp) / 'child.pid'
            process = subprocess.Popen([sys.executable, '-c', PARENT, CHILD, str(ready)],
                                       start_new_session=True)
            try:
                child = await_pid(ready)
                campaign.terminate_job(process)
                deadline = time.monotonic() + 2
                while is_running(child) and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertIsNotNone(process.poll())
                self.assertFalse(is_running(child))
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()

    def test_followup_interrupt_leaves_no_native_child_or_fake_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            ready = run / 'child.pid'
            task = {'name': 'fake_native',
                    'command': [sys.executable, '-c', PARENT, CHILD, str(ready)]}
            child = None

            def interrupt(_run):
                nonlocal child
                child = await_pid(ready)
                raise KeyboardInterrupt()

            try:
                with patch.object(campaign, 'guard', interrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        campaign.run_followup(task, run, dict(os.environ), {})
                deadline = time.monotonic() + 2
                while is_running(child) and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertFalse(is_running(child))
                self.assertFalse((run / 'fake_native.status').exists())
            finally:
                if child and is_running(child):
                    os.kill(child, signal.SIGKILL)


if __name__ == '__main__':
    unittest.main()
