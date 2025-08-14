import os
from collections import defaultdict
import re

class SpamDetector:
    """
    A simple Bayesian spam detector that classifies messages as spam or ham.

    It trains on provided ham and spam messages to learn word probabilities
    and then predicts whether a new message is spam or ham.
    """

    def __init__(self, training_data_path):
        """
        Initializes the SpamDetector and trains it using data from the specified path.

        Args:
            training_data_path (str): The path to the directory containing
                                      'ham_messages.txt' and 'spam_messages.txt'
                                      for training.
        """
        self.ham_words = defaultdict(int)
        self.spam_words = defaultdict(int)
        self.ham_messages_count = 0
        self.spam_messages_count = 0
        self.all_words = set() # Vocabulary of all words seen

        self._load_and_train(training_data_path)

    def _tokenize(self, text):
        """
        Converts text to lowercase and splits it into words, filtering out non-alphabetic tokens.
        This is an internal helper method.

        Args:
            text (str): The input string message.

        Returns:
            list: A list of lowercase, alphabetic words.
        """
        # Use regex to find all sequences of alphabetic characters (a-z)
        # re.findall returns a list of all non-overlapping matches
        words = re.findall(r'[a-z]+', text.lower())
        return words

    def _train(self, message, is_spam):
        """
        Trains the detector with a single message. Updates word counts and message counts.
        This is an internal helper method.

        Args:
            message (str): The message string to train on.
            is_spam (bool): True if the message is spam, False if it's ham.
        """
        words = self._tokenize(message)
        for word in words:
            self.all_words.add(word) # Add word to overall vocabulary
            if is_spam:
                self.spam_words[word] += 1
            else:
                self.ham_words[word] += 1
        
        if is_spam:
            self.spam_messages_count += 1
        else:
            self.ham_messages_count += 1

    def _load_and_train(self, training_data_path):
        """
        Loads training data from files and trains the detector.
        This is an internal method called during initialization.
        """
        ham_file = os.path.join(training_data_path, "ham_messages.txt")
        spam_file = os.path.join(training_data_path, "spam_messages.txt")

        # Check if training data files exist
        ham_exists = os.path.exists(ham_file)
        spam_exists = os.path.exists(spam_file)

        if not ham_exists and not spam_exists:
            print(f"[!] Warning: No training data files found in {training_data_path}. Using minimal default training.")
            self._train("hello how are you", False) # Default ham
            self._train("buy now free money", True) # Default spam
            return
        
        try:
            if ham_exists:
                with open(ham_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        self._train(line.strip(), False)
            if spam_exists:
                with open(spam_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        self._train(line.strip(), True)
        except Exception as e:
            print(f"[X] Error loading training data: {e}. Falling back to minimal default training.")
            # Clear any partial training and load minimal defaults
            self.ham_words = defaultdict(int)
            self.spam_words = defaultdict(int)
            self.ham_messages_count = 0
            self.spam_messages_count = 0
            self.all_words = set()
            self._train("hello how are you", False)
            self._train("buy now free money", True)


    def _calculate_word_probability(self, word, category_word_counts, category_message_count):
        """
        Calculates the probability of a word appearing in a given category (ham or spam).
        Uses Laplace smoothing (add-1 smoothing) to handle unseen words.
        This is an internal helper method.

        Args:
            word (str): The word for which to calculate the probability.
            category_word_counts (collections.defaultdict): Word counts for the specific category.
            category_message_count (int): Total message count for the specific category.

        Returns:
            float: The calculated probability.
        """
        # Ensure vocabulary size is at least 1 to prevent division by zero if all_words is empty
        vocab_size = len(self.all_words) if len(self.all_words) > 0 else 1

        # Total number of words in this category (sum of all word counts)
        total_words_in_category = sum(category_word_counts.values())

        return (category_word_counts[word] + 1) / \
               (total_words_in_category + vocab_size)

    def predict(self, message):
        """
        Predicts whether a given message is spam or ham using a Naive Bayes approach.

        Args:
            message (str): The message string to classify.

        Returns:
            bool: True if the message is predicted as spam, False (ham) otherwise.
        """
        if not message.strip():
            return False # Empty or whitespace-only messages are classified as ham

        words = self._tokenize(message)
        
        # If no words in message or no training data, default to ham
        if not words or (self.ham_messages_count == 0 and self.spam_messages_count == 0):
            return False

        # Calculate prior probabilities (P(Ham) and P(Spam))
        total_messages = self.ham_messages_count + self.spam_messages_count
        if total_messages == 0: # Should be caught by earlier check, but for safety
            return False
        
        prior_ham = self.ham_messages_count / total_messages
        prior_spam = self.spam_messages_count / total_messages

        # Calculate likelihoods (P(Message|Ham) and P(Message|Spam))
        ham_likelihood = 1.0
        spam_likelihood = 1.0

        for word in words:
            ham_likelihood *= self._calculate_word_probability(word, self.ham_words, self.ham_messages_count)
            spam_likelihood *= self._calculate_word_probability(word, self.spam_words, self.spam_messages_count)

        # Calculate posterior probabilities (P(Ham|Message) and P(Spam|Message))
        # We compare these values directly, so normalization constant is not needed.
        posterior_ham = ham_likelihood * prior_ham
        posterior_spam = spam_likelihood * prior_spam
        
        # If both posteriors are zero (e.g., very short message with only completely unknown words
        # and very small vocabulary size), default to ham.
        if posterior_ham == 0 and posterior_spam == 0:
            return False

        return posterior_spam > posterior_ham

