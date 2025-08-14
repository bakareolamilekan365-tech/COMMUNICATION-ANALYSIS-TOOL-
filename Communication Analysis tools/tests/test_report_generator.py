"""
Unit tests for the report_generator module.

This module verifies the parsing capabilities for different message formats
(single email, multi-email, WhatsApp), and the overall report generation process.
It uses mocking to isolate the report_generator from external dependencies
like SpamDetector, SentimentAnalyzer, and MetricsCalculator.
"""

import unittest
import os
import shutil
from unittest.mock import Mock, patch
from datetime import datetime

from modules.report_generator import (
    generate_report,
    generate_custom_test_report,
    generate_report_from_custom_input,
    _parse_single_email_block,
    _parse_multi_email_file,
    _parse_whatsapp_content,
    _is_whatsapp_format,
    _has_email_boundary,
    EMAIL_BOUNDARY_SEPARATOR
)

TEST_EMAIL_SINGLE = """Subject: Test Email
From: test@example.com
Date: 2025-01-01 12:00:00
Conversation-ID: email_test_001

This is a test email body.
"""

TEST_EMAIL_MULTI = f"""Subject: First Email
From: multi1@example.com
Date: 2025-01-01 10:00:00
Conversation-ID: multi_test_001

Body of first email.

{EMAIL_BOUNDARY_SEPARATOR}

Subject: Second Email
From: multi2@example.com
Date: 2025-01-01 10:05:00
Conversation-ID: multi_test_001

Body of second email.
"""

TEST_WHATSAPP = """1/1/25, 10:00 AM - Alice: Hey Bob!
1/1/25, 10:05 AM - Bob: Hi Alice! How are you?
1/1/25, 10:10 AM - Alice: I'm great, thanks!
"""

class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = "test_data_reports"
        self.test_sample_emails_dir = os.path.join(self.test_data_dir, "sample_emails")
        self.test_reports_dir = os.path.join(self.test_data_dir, "reports")
        os.makedirs(self.test_sample_emails_dir, exist_ok=True)
        os.makedirs(self.test_reports_dir, exist_ok=True)

        with open(os.path.join(self.test_sample_emails_dir, "single_email.txt"), "w") as f:
            f.write(TEST_EMAIL_SINGLE)
        with open(os.path.join(self.test_sample_emails_dir, "multi_email.txt"), "w") as f:
            f.write(TEST_EMAIL_MULTI)
        with open(os.path.join(self.test_sample_emails_dir, "whatsapp_chat.txt"), "w") as f:
            f.write(TEST_WHATSAPP)

        self.mock_spam_detector = Mock()
        self.mock_spam_detector.predict.return_value = False
        self.mock_sentiment_analyzer = Mock()
        self.mock_sentiment_analyzer.analyze.return_value = "neutral"
        self.mock_style_analyzer = Mock()
        self.mock_style_analyzer.analyze.return_value = {"Style Score": 50, "Formality": "informal"}
        self.mock_metrics_calculator_content = Mock(return_value={
            "Total Messages": 1, "Spam Counts": {"SPAM": 0, "HAM": 1},
            "Sentiment Counts": {"positive": 0, "neutral": 1, "negative": 0},
            "Average Style Score": 50.0, "Formality Counts": {"formal": 0, "informal": 1}
        })
        self.mock_metrics_calculator_engagement = Mock(return_value={
            "Top Senders": {"TestSender": 1}, "Average Response time (sec)": None,
            "Suggestions": ["No behavioral recommendations found."]
        })

        patcher_sd = patch('modules.report_generator.SpamDetector', return_value=self.mock_spam_detector)
        patcher_sa = patch('modules.report_generator.SentimentAnalyzer', return_value=self.mock_sentiment_analyzer)
        patcher_st = patch('modules.report_generator.StyleAnalyzer', return_value=self.mock_style_analyzer)
        patcher_cm = patch('modules.report_generator.calculate_content_metrics', new=self.mock_metrics_calculator_content)
        patcher_em = patch('modules.report_generator.calculate_engagement_metrics', new=self.mock_metrics_calculator_engagement)

        self.mock_spam_detector_start = patcher_sd.start()
        self.mock_sentiment_analyzer_start = patcher_sa.start()
        self.mock_style_analyzer_start = patcher_st.start()
        self.mock_metrics_calculator_content_start = patcher_cm.start()
        self.mock_metrics_calculator_engagement_start = patcher_em.start()

        self.addCleanup(patcher_sd.stop)
        self.addCleanup(patcher_sa.stop)
        self.addCleanup(patcher_st.stop)
        self.addCleanup(patcher_cm.stop)
        self.addCleanup(patcher_em.stop)
        self.addCleanup(lambda: shutil.rmtree(self.test_data_dir))


    def test_parse_single_email_block(self):
        headers, body = _parse_single_email_block(TEST_EMAIL_SINGLE)
        self.assertEqual(headers["Subject"], "Test Email")
        self.assertEqual(headers["Sender"], "test@example.com")
        self.assertIn("test email body", body)

    def test_parse_multi_email_file(self):
        parsed_messages = _parse_multi_email_file(TEST_EMAIL_MULTI, "multi_email.txt")
        self.assertEqual(len(parsed_messages), 2)
        self.assertEqual(parsed_messages[0]["Subject"], "First Email")
        self.assertEqual(parsed_messages[1]["Sender"], "multi2@example.com")
        self.assertEqual(parsed_messages[0]["Conversation ID"], "multi_test_001")
        self.assertEqual(parsed_messages[1]["Conversation ID"], "multi_test_001")


    def test_parse_whatsapp_content(self):
        parsed_messages = _parse_whatsapp_content(TEST_WHATSAPP, "whatsapp_chat.txt")
        self.assertEqual(len(parsed_messages), 3)
        self.assertEqual(parsed_messages[0]["Sender"], "Alice")
        self.assertEqual(parsed_messages[1]["Message"], "Hi Alice! How are you?")
        self.assertIsNotNone(parsed_messages[0]["Timestamp"])
        self.assertEqual(parsed_messages[0]["Conversation ID"], "whatsapp_chat_whatsapp_chat_txt")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=TEST_EMAIL_SINGLE)
    @patch('modules.report_generator.os.path.exists', return_value=True)
    def test_generate_custom_test_report_single_email(self, mock_exists, mock_open):
        test_file_path = os.path.join(self.test_sample_emails_dir, "single_email.txt")
        generate_custom_test_report(test_file_path, output_path=os.path.join(self.test_reports_dir, "custom_report.txt"))

        mock_open.assert_called_with(unittest.mock.ANY, 'w', encoding='utf-8')
        self.mock_sentiment_analyzer.analyze.assert_called_once()
        self.mock_metrics_calculator_content.assert_called_once()

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=TEST_WHATSAPP)
    @patch('modules.report_generator.os.path.exists', return_value=True)
    def test_generate_custom_test_report_whatsapp(self, mock_exists, mock_open):
        test_file_path = os.path.join(self.test_sample_emails_dir, "whatsapp_chat.txt")
        generate_custom_test_report(test_file_path, output_path=os.path.join(self.test_reports_dir, "whatsapp_report.txt"))

        expected_calls = len(TEST_WHATSAPP.strip().split('\n'))
        self.assertGreaterEqual(self.mock_sentiment_analyzer.analyze.call_count, 2)
        self.mock_metrics_calculator_content.assert_called_once()
        self.mock_metrics_calculator_engagement.assert_called_once()

    @patch('modules.report_generator._print_summary_to_cli')
    def test_cli_summary_called(self, mock_print_summary):
        test_file_path = os.path.join(self.test_sample_emails_dir, "single_email.txt")
        generate_custom_test_report(test_file_path)
        mock_print_summary.assert_called_once()

    def test_generate_report_from_custom_input_whatsapp_format(self):
        message = "2/14/25, 4:26 PM - Bobola 🤖✨: Ohhh okay"
        generate_report_from_custom_input(message, message_type="WhatsApp")
        args, kwargs = self.mock_sentiment_analyzer.analyze.call_args
        self.assertEqual(args[0], "Ohhh okay")
        
        content_metrics_call_args = self.mock_metrics_calculator_content.call_args[0][0]
        self.assertEqual(content_metrics_call_args[0]["Sender"], "Bobola 🤖✨")
        self.assertIn("whatsapp_chat_typed_whatsapp_msg_txt", content_metrics_call_args[0]["Conversation ID"])
        self.assertIn("2025-02-14 16:26:00", content_metrics_call_args[0]["Timestamp"])

    def test_generate_report_from_custom_input_email_format(self):
        message = """Subject: Test Email Input
From: typed@example.com
Date: 2025-07-26 15:00:00
Conversation-ID: typed_email_001

This is the body of the typed email."""
        generate_report_from_custom_input(message, message_type="Email")

        content_metrics_call_args = self.mock_metrics_calculator_content.call_args[0][0]
        self.assertEqual(content_metrics_call_args[0]["Sender"], "typed@example.com")
        self.assertEqual(content_metrics_call_args[0]["Subject"], "Test Email Input")
        self.assertEqual(content_metrics_call_args[0]["Conversation ID"], "typed_email_001")
        self.assertIn("2025-07-26 15:00:00", content_metrics_call_args[0]["Timestamp"])
        self.assertEqual(content_metrics_call_args[0]["Message"], "This is the body of the typed email.")


if __name__ == '__main__':
    unittest.main()

