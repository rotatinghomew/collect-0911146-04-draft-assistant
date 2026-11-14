import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import URLError

from local_http import request


class StartupTests(unittest.TestCase):
    def test_service_uses_configured_port_and_stops_cleanly(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen(
            [sys.executable, 'portal.py', '--host', '127.0.0.1', '--port', str(port)],
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, 'PORT': '0'},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        base = 'http://127.0.0.1:' + str(port)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    response = request(base)
                    break
                except URLError:
                    if process.poll() is not None:
                        self.fail(process.stdout.read())
                    time.sleep(0.05)
            else:
                self.fail('服务未在指定端口启动')
            self.assertEqual(response.status, 200)
            self.assertIn(b'/draft.js', response.body)
            self.assertEqual(request(base + '/session').status, 200)
            self.assertEqual(request(base + '/state').status, 401)
        finally:
            process.terminate()
            try:
                output = process.communicate(timeout=5)[0]
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                self.fail('服务未在终止信号后正常退出')
        self.assertEqual(process.returncode, 0, output)
