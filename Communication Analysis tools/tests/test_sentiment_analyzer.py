"""
Unit tests for the SentimentAnalyzer module.

This module verifies the sentiment classification logic, ensuring messages
are correctly categorized as positive, negative, or neutral based on lexicons.
"""

import unittest
from modules.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_positive_sentiment(self):
        self.assertEqual(self.analyzer.analyze("This is a truly wonderful and amazing experience!"), "positive")
        self.assertEqual(self.analyzer.analyze("I love this great idea."), "positive")

    def test_negative_sentiment(self):
        self.assertEqual(self.analyzer.analyze("This is a terrible and awful problem."), "negative")
        self.assertEqual(self.analyzer.analyze("I hate this bad issue."), "negative")

    def test_neutral_sentiment_no_keywords(self):
        self.assertEqual(self.analyzer.analyze("The quick brown fox jumps over the lazy dog."), "neutral")
        self.assertEqual(self.analyzer.analyze("A cat sat on the mat."), "neutral")

    def test_neutral_sentiment_balanced_keywords(self):
        self.assertEqual(self.analyzer.analyze("It was a good idea but had a terrible implementation."), "neutral")
        self.assertEqual(self.analyzer.analyze("I like the concept, but the execution was bad."), "neutral")

    def test_empty_message(self):
        self.assertEqual(self.analyzer.analyze(""), "neutral")

    def test_message_with_punctuation_and_numbers(self):
        self.assertEqual(self.analyzer.analyze("This is great! (123)"), "positive")
        self.assertEqual(self.analyzer.analyze("What a terrible-problem!"), "negative")

if __name__ == '__main__':
    unittest.main()
