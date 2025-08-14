"""
Unit tests for the SpamDetector module.

This module contains test cases to verify the correct functionality of:
- Message tokenization.
- Training process for ham and spam messages.
- Probability calculation for words.
- Prediction accuracy for classifying messages as spam or ham.
"""
import unittest
import os
from collections import defaultdict
from modules.spam_detector import SpamDetector

class TestSpamDetector(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_training_data"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "ham_messages.txt"), "w") as f:
            f.write("hello world\n")
            f.write("how are you\n")
        with open(os.path.join(self.test_dir, "spam_messages.txt"), "w") as f:
            f.write("buy now free money\n")
            f.write("win lottery prize\n")
        self.detector = SpamDetector(self.test_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_tokenize(self):
        text = "Hello, World! 123 Buy now. Free money!!!"
        expected = ["hello", "world", "buy", "now", "free", "money"]
        self.assertEqual(self.detector._tokenize(text), expected)

    def test_train_ham_message(self):
        initial_ham_count = self.detector.ham_messages_count
        initial_ham_words = dict(self.detector.ham_words)
        self.detector._train("test ham message", False)
        self.assertEqual(self.detector.ham_messages_count, initial_ham_count + 1)
        self.assertEqual(self.detector.ham_words["test"], 1)
        self.assertEqual(self.detector.ham_words["ham"], 1)
        self.assertEqual(self.detector.ham_words["message"], 1)

    def test_predict_ham(self):
        self.assertFalse(self.detector.predict("this is a normal email"))

    def test_predict_spam(self):
        self.assertTrue(self.detector.predict("urgent claim your prize now"))

    def test_predict_unknown_word(self):
        self.assertFalse(self.detector.predict("this is a completely new sentence"))

    def test_empty_message_prediction(self):
        self.assertFalse(self.detector.predict(""))

if __name__ == '__main__':
    unittest.main()
