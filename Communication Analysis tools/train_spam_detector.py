"""
train_spam_detector.py

Trains the SpamDetector using sample messages from digitallogs.
Stores word frequencies in ham_word_counts.json and spam_word_counts.json.
"""

from modules.spam_detector import SpamDetector
import os

# File paths to training examples
spam_file = "digitallogssample/spam_messages.txt"
ham_file = "digitallogssample/ham_messages.txt"

# Create detector with correct data path
detector = SpamDetector(data_path="data/training_data")

def train_from_file(filepath, is_spam):
    # Check file exists
    if not os.path.exists(filepath):
        print(f" File not found: {filepath}")
        return

    # Feed each line into training model
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            message = line.strip()
            if message:
                detector.train(message, is_spam)

# Train using your labeled files
train_from_file(spam_file, is_spam=True)
train_from_file(ham_file, is_spam=False)

# Save learned word frequencies
detector._save_model()
print(" Training complete. Word counts saved to training data folder.")