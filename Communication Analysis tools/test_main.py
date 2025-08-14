"""
Integration/Unit tests for the main.py CLI.

This module tests the overall flow of the command-line interface,
ensuring that user input correctly triggers the intended functions
from other modules. It uses mocking to simulate user input and
to prevent actual file operations or external module calls during tests.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from io import StringIO

import main

class TestMainCLI(unittest.TestCase):

    def setUp(self):
        self.mock_generate_report = patch('main.generate_report').start()
        self.mock_generate_custom_test_report = patch('main.generate_custom_test_report').start()
        self.mock_generate_report_from_custom_input = patch('main.generate_report_from_custom_input').start()
        
        self.mock_list_sample_files = patch('main.list_sample_files').start()
        self.mock_list_sample_files.return_value = [
            ("test_file_1.txt", "/path/to/test_file_1.txt"),
            ("test_file_2.txt", "/path/to/test_file_2.txt")
        ]

        self.held_stdout = sys.stdout
        sys.stdout = StringIO()

        self.addCleanup(patch.stopall)
        self.addCleanup(self._restore_stdout)

    def _restore_stdout(self):
        sys.stdout = self.held_stdout

    def _get_stdout(self):
        return sys.stdout.getvalue()

    @patch('builtins.input', side_effect=['1', '4'])
    def test_option_1_full_analysis(self, mock_input):
        main.main()
        self.mock_generate_report.assert_called_once_with("sample_emails")
        self.assertIn("Running full analysis on sample dataset", self._get_stdout())

    @patch('builtins.input', side_effect=['2', '1', '4'])
    @patch('main.os.path.exists', return_value=True)
    def test_option_2_analyze_sample_file(self, mock_exists, mock_input):
        main.main()
        self.mock_generate_custom_test_report.assert_called_once()
        self.assertEqual(self.mock_generate_custom_test_report.call_args[0][0], "/path/to/test_file_1.txt")
        self.assertIn("Listing available sample files", self._get_stdout())

    @patch('builtins.input', side_effect=['2', '0', '/custom/path/my_file.txt', '4'])
    @patch('main.os.path.exists', return_value=True)
    def test_option_2_analyze_custom_path(self, mock_exists, mock_input):
        main.main()
        self.mock_generate_custom_test_report.assert_called_once()
        self.assertEqual(self.mock_generate_custom_test_report.call_args[0][0], "/custom/path/my_file.txt")

    @patch('builtins.input', side_effect=['3', '1', 'Alice', 'convo1', 'Hello!', '', 'n', '4'])
    def test_option_3_whatsapp_message(self, mock_input):
        main.main()
        self.mock_generate_report_from_custom_input.assert_called_once_with(
            'Hello!', sender='Alice', conversation_id='convo1', message_type='WhatsApp'
        )
        self.assertIn("Analyzing Custom WhatsApp Message", self._get_stdout())

    @patch('builtins.input', side_effect=['3', '2', '', '', 'Subject: Test\n\nBody', '', 'n', '4'])
    def test_option_3_email_message(self, mock_input):
        main.main()
        self.mock_generate_report_from_custom_input.assert_called_once_with(
            'Subject: Test\n\nBody', sender=None, conversation_id=None, message_type='Email'
        )
        self.assertIn("Analyzing Custom Email Message", self._get_stdout())

    @patch('builtins.input', side_effect=['3', '1', 'back', '5', '4']) # Added '4'
    def test_option_3_back_from_sender(self, mock_input):
        main.main()
        self.mock_generate_report_from_custom_input.assert_not_called()
        self.assertIn("Going back to message type selection", self._get_stdout())
        self.assertIn("Select Message Type", self._get_stdout())

    @patch('builtins.input', side_effect=['3', '1', 'Alice', 'back', '5', '4']) # Added '4'
    def test_option_3_back_from_convo_id(self, mock_input):
        main.main()
        self.mock_generate_report_from_custom_input.assert_not_called()
        self.assertIn("Going back to message type selection", self._get_stdout())
        self.assertIn("Select Message Type", self._get_stdout())

    @patch('builtins.input', side_effect=['3', '1', 'Alice', 'convo1', 'message line 1', 'cancel', '5', '4']) # Added '4'
    def test_option_3_cancel_message_input(self, mock_input):
        main.main()
        self.mock_generate_report_from_custom_input.assert_not_called()
        self.assertIn("Message input cancelled", self._get_stdout())
        self.assertIn("Select Message Type", self._get_stdout())

    @patch('builtins.input', side_effect=['4'])
    def test_option_4_exit(self, mock_input):
        main.main()
        self.assertIn("Exiting CLI. Goodbye!", self._get_stdout())

    @patch('builtins.input', side_effect=['99', '4']) # Added '4'
    def test_invalid_main_menu_choice(self, mock_input):
        main.main()
        self.assertIn("Invalid option. Try again.", self._get_stdout())
        self.assertGreaterEqual(self._get_stdout().count("Communication Analysis CLI"), 2)

    @patch('builtins.input', side_effect=['3', '99', '5', '4']) # Added '4'
    def test_invalid_message_type_choice(self, mock_input):
        main.main()
        self.assertIn("Invalid message type option. Try again.", self._get_stdout())
        self.assertGreaterEqual(self._get_stdout().count("Select Message Type"), 2)


if __name__ == '__main__':
    unittest.main()
