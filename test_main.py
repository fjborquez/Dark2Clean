import asyncio
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from fastapi import HTTPException
from pyngrok.ngrok import NgrokTunnel

from main import start_tor, close, start_ngrok, get, try_to_install_tor, set_privacy, run_server


class TestMain(unittest.TestCase):
    def test_start_tor_windows(self) -> None:
        """Test start_tor"""
        self.start_tor_base('windows')

    def test_start_tor_linux(self) -> None:
        """Test start_tor"""
        self.start_tor_base('linux')

    def test_start_tor_mac(self) -> None:
        """Test start_tor"""
        self.start_tor_base('darwin')

    def test_start_tor_other(self) -> None:
        """Test start_tor"""
        out, error = StringIO(), StringIO()
        os = 'android'

        with patch('subprocess.run'), patch.multiple(sys, stdout=out, stderr=error, platform=os), \
                self.assertRaises(SystemExit):
            start_tor()

    def test_close(self) -> None:
        """Test close"""
        with patch('main.ngrok.disconnect') as mock, patch('main._connection', return_value=NgrokTunnel):
            close()
            mock.assert_called()

    def test_start_ngrok_when_protocol_is_http(self) -> None:
        """Test start_ngrok with http"""
        protocol = "1"
        self.start_ngrok_base(protocol)

    def test_start_ngrok_when_protocol_is_tcp(self) -> None:
        """Test start_ngrok with tcp"""
        protocol = "1"
        self.start_ngrok_base(protocol)

    def test_get(self) -> None:
        """Test get"""
        url = ""
        with patch('requests.get') as mock:
            asyncio.run(get(url))
            mock.assert_called()

    def test_get_raise_exception(self) -> None:
        """Test get"""
        url = ""
        with self.assertRaises(HTTPException):
            asyncio.run(get(url))

    def start_tor_base(self, os: str) -> None:
        """Test start_ngrok"""
        out, error = StringIO(), StringIO()
        needle = "Tor service restarted successfully"

        with patch('subprocess.run'), patch.multiple(sys, stdout=out, stderr=error, platform=os):
            start_tor()

        result = needle in out.getvalue()
        self.assertTrue(result)

    def start_ngrok_base(self, protocol: str) -> None:
        """Test start_ngrok"""
        out, error = StringIO(), StringIO()
        needle = "Ngrok Public URL"
        connection = NgrokTunnel
        connection.public_url = ""
        with patch.multiple(sys, stdout=out, stderr=error), patch('main.ngrok.connect', return_value=connection):
            start_ngrok("", protocol)
            self.assertTrue(needle in out.getvalue())

    def test_try_to_install_tor_when_tor_is_installed(self) -> None:
        """Test try_to_install_tor"""
        out, error = StringIO(), StringIO()
        needle = "Installed Tor"

        with patch('Tor_install.check_tor_installed', True), patch('main.install_tor'), \
                patch.multiple(sys, stdout=out, stderr=error):
            try_to_install_tor()
            self.assertTrue(needle in out.getvalue())

    def test_try_to_install_tor_when_tor_is_not_installed(self) -> None:
        """Test try_to_install_tor"""
        out, error = StringIO(), StringIO()

        with patch('Tor_install.check_tor_installed', False), patch.multiple(sys, stdout=out, stderr=error), \
                self.assertRaises(SystemExit):
            try_to_install_tor()

    def test_try_to_install_tor_when_raises_an_exception(self) -> None:
        """Test try_to_install_tor"""
        out, error = StringIO(), StringIO()

        with patch('Tor_install.check_tor_installed', return_value=True), \
                patch('main.install_tor', side_effect=Exception), \
                patch.multiple(sys, stdout=out, stderr=error), self.assertRaises(SystemExit):
            try_to_install_tor()

    def test_set_privacy_when_input_is_1(self) -> None:
        """Test set_privacy"""
        with patch('main.input', return_value="1") as mock, patch('main.start_ngrok'):
            set_privacy()
            mock.assert_called()

    def test_set_privacy_when_input_is_not_1(self) -> None:
        """Test set_privacy"""
        out, error = StringIO(), StringIO()
        needle = "Private URL : http://localhost:8088"
        with patch.multiple(sys, stdout=out, stderr=error), patch('main.input', return_value="2"), \
                patch('main.start_ngrok'):
            set_privacy()
            self.assertTrue(needle in out.getvalue())

    def test_run_server(self):
        """Test run_server"""
        with patch('uvicorn.run') as mock:
            run_server()
            mock.assert_called()


if __name__ == '__main__':
    unittest.main()
