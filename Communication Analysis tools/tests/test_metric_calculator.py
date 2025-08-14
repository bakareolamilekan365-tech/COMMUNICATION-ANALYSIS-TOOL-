"""
Unit tests for the metrics_calculator module.

This module verifies the correct calculation of:
- Summary content metrics (total messages, spam/ham counts, sentiment breakdown, avg style, formality).
- Behavioral insights (top senders, average response delay, suggestions).
"""
import unittest
from datetime import datetime, timedelta
from modules.metrics_calculator import (
    calculate_content_metrics,
    calculate_engagement_metrics
)

class TestMetricsCalculator(unittest.TestCase):
    """
    Test suite for the metrics_calculator functions.

    Covers various scenarios for calculating content and engagement metrics
    from lists of analyzed message data.
    """

    def test_calculate_content_metrics_basic(self):
        """
        Tests calculate_content_metrics with a basic set of messages,
        verifying total counts, spam, sentiment, and formality breakdowns.
        """
        results = [
            {"Spam": "HAM", "Sentiment": "positive", "Style Score": 70.0, "Formality": "formal"},
            {"Spam": "SPAM", "Sentiment": "negative", "Style Score": 30.0, "Formality": "informal"},
            {"Spam": "HAM", "Sentiment": "neutral", "Style Score": 60.0, "Formality": "neutral"}, # Added neutral formality
        ]
        metrics = calculate_content_metrics(results)
        self.assertEqual(metrics["Total Messages"], 3)
        self.assertEqual(metrics["Spam Counts"], {"SPAM": 1, "HAM": 2})
        self.assertEqual(metrics["Sentiment Counts"], {"positive": 1, "neutral": 1, "negative": 1})
        # FIX: Use places for floating point comparison
        self.assertAlmostEqual(metrics["Average Style Score"], (70.0+30.0+60.0)/3, places=2)
        # FIX: Expect neutral in formality counts
        self.assertEqual(metrics["Formality Counts"], {"formal": 1, "informal": 1, "neutral": 1})

    def test_calculate_content_metrics_empty(self):
        """
        Tests calculate_content_metrics with an empty list of results,
        ensuring all counts and averages are zero or default.
        """
        metrics = calculate_content_metrics([])
        self.assertEqual(metrics["Total Messages"], 0)
        self.assertEqual(metrics["Spam Counts"], {"SPAM": 0, "HAM": 0})
        self.assertEqual(metrics["Sentiment Counts"], {"positive": 0, "neutral": 0, "negative": 0})
        self.assertEqual(metrics["Average Style Score"], 0.0)
        # FIX: Expect neutral in formality counts
        self.assertEqual(metrics["Formality Counts"], {"formal": 0, "informal": 0, "neutral": 0})

    def test_calculate_engagement_metrics_response_time(self):
        """
        Tests calculate_engagement_metrics with messages from a single conversation,
        verifying the average response time calculation.
        """
        t1 = datetime(2025, 7, 26, 10, 0, 0)
        t2 = datetime(2025, 7, 26, 10, 5, 0) # 5 minutes = 300 seconds
        t3 = datetime(2025, 7, 26, 10, 10, 0) # 5 minutes = 300 seconds
        
        results = [
            {"Sender": "Alice", "Conversation ID": "convo1", "Timestamp": t1, "Style Score": 50, "Formality": "informal"},
            {"Sender": "Bob", "Conversation ID": "convo1", "Timestamp": t2, "Style Score": 50, "Formality": "informal"},
            {"Sender": "Alice", "Conversation ID": "convo1", "Timestamp": t3, "Style Score": 50, "Formality": "informal"},
        ]
        engagement = calculate_engagement_metrics(results)
        self.assertAlmostEqual(engagement["Average Response time (sec)"], 300.0, places=2)
        self.assertEqual(engagement["Top Senders"], {"Alice": 2, "Bob": 1})

    def test_calculate_engagement_metrics_multiple_conversations(self):
        """
        Tests calculate_engagement_metrics with messages from multiple conversations,
        ensuring response times are calculated per conversation and averaged correctly.
        """
        t1_a = datetime(2025, 7, 26, 9, 0, 0)
        t1_b = datetime(2025, 7, 26, 9, 10, 0) # 600 sec
        t2_a = datetime(2025, 7, 26, 11, 0, 0)
        t2_b = datetime(2025, 7, 26, 11, 5, 0) # 300 sec

        results = [
            {"Sender": "UserA", "Conversation ID": "chatX", "Timestamp": t1_a, "Style Score": 50, "Formality": "informal"},
            {"Sender": "UserB", "Conversation ID": "chatX", "Timestamp": t1_b, "Style Score": 50, "Formality": "informal"},
            {"Sender": "UserC", "Conversation ID": "chatY", "Timestamp": t2_a, "Style Score": 50, "Formality": "informal"},
            {"Sender": "UserD", "Conversation ID": "chatY", "Timestamp": t2_b, "Style Score": 50, "Formality": "informal"},
        ]
        engagement = calculate_engagement_metrics(results)
        self.assertAlmostEqual(engagement["Average Response time (sec)"], (600 + 300) / 2, places=2)
        self.assertEqual(engagement["Top Senders"], {"UserA": 1, "UserB": 1, "UserC": 1, "UserD": 1})

    def test_calculate_engagement_metrics_no_response_data(self):
        """
        Tests calculate_engagement_metrics when there's insufficient data for response time calculation
        (e.g., only single messages in conversations).
        """
        results = [
            {"Sender": "Alice", "Conversation ID": "convo1", "Timestamp": datetime(2025, 7, 26, 10, 0, 0), "Style Score": 50, "Formality": "informal"},
            {"Sender": "Bob", "Conversation ID": "convo2", "Timestamp": datetime(2025, 7, 26, 10, 10, 0), "Style Score": 50, "Formality": "informal"},
        ]
        engagement = calculate_engagement_metrics(results)
        self.assertIsNone(engagement["Average Response time (sec)"])
        self.assertEqual(engagement["Top Senders"], {"Alice": 1, "Bob": 1})

    def test_suggestions_generation_high_response_time(self):
        """
        Tests that "Respond promptly" suggestion is generated when response time is high.
        """
        # 1 day and 1 hour delay (86400 + 3600 = 90000 seconds)
        t_start = datetime(2025, 1, 1, 10, 0, 0)
        t_end = datetime(2025, 1, 2, 11, 0, 0) 
        results_high_delay = [
            {"Sender": "A", "Conversation ID": "c1", "Timestamp": t_start, "Style Score": 50, "Formality": "neutral"},
            {"Sender": "B", "Conversation ID": "c1", "Timestamp": t_end, "Style Score": 50, "Formality": "neutral"},
        ]
        engagement_high_delay = calculate_engagement_metrics(results_high_delay)
        # FIX: Ensure the string matches exactly what the module produces
        self.assertIn("Respond to messages more promptly to improve conversation engagement.", engagement_high_delay["Suggestions"])

    def test_suggestions_generation_low_style_score(self):
        """
        Tests that "Improve clarity" suggestion is generated when average style score is low.
        """
        results_low_style = [
            {"Sender": "A", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 0), "Style Score": 30, "Formality": "informal"},
            {"Sender": "B", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 5), "Style Score": 35, "Formality": "informal"},
        ]
        engagement_low_style = calculate_engagement_metrics(results_low_style)
        self.assertIn("Improve clarity and structure in messages.", engagement_low_style["Suggestions"])

    def test_suggestions_generation_informal_formality(self):
        """
        Tests that "Use more formal phrasing" suggestion is generated when formality is predominantly informal.
        """
        results_informal = [
            {"Sender": "A", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 0), "Style Score": 30, "Formality": "informal"},
            {"Sender": "B", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 5), "Style Score": 35, "Formality": "informal"},
            {"Sender": "C", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 10), "Style Score": 80, "Formality": "formal"}, # One formal
        ]
        engagement_informal = calculate_engagement_metrics(results_informal)
        self.assertIn("Consider using more formal phrasing for professional contexts.", engagement_informal["Suggestions"])

    def test_suggestions_generation_no_suggestions(self):
        """
        Tests that no suggestions are generated when all criteria are met (good style, prompt response, balanced formality).
        """
        results_good = [
            {"Sender": "A", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 0), "Style Score": 80, "Formality": "formal"},
            {"Sender": "B", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 10), "Style Score": 80, "Formality": "formal"}, # 10 min delay
            {"Sender": "C", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 20), "Style Score": 50, "Formality": "neutral"},
            {"Sender": "D", "Conversation ID": "c1", "Timestamp": datetime(2025, 1, 1, 10, 30), "Style Score": 30, "Formality": "informal"}, # Some informal, but not dominant
        ]
        engagement_good = calculate_engagement_metrics(results_good)
        self.assertListEqual(engagement_good["Suggestions"], [])


if __name__ == '__main__':
    unittest.main()
