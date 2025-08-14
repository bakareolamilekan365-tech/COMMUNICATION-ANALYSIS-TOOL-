import re

class SentimentAnalyzer:
    """
    A lexicon-based sentiment analyzer that determines the emotional tone of text.
    It counts positive and negative words to classify sentiment.
    """

    def __init__(self):
        """
        Initializes the SentimentAnalyzer with predefined sets of positive and negative words.
        These lexicons can be customized.
        """
        self.positive_words = {
            "good", "great", "excellent", "wonderful", "amazing", "happy", "joy",
            "love", "fantastic", "awesome", "brilliant", "positive", "super",
            "success", "benefit", "pleasure", "like", "best", "perfect", "nice",
            "beautiful", "friendly", "kind", "optimistic", "glad", "delight", "cheer",
            "agree", "fine", "ok", "okay", "cool", "yeah" # Added for broader positive/neutral detection
        }
        self.negative_words = {
            "bad", "terrible", "horrible", "awful", "sad", "unhappy", "hate",
            "poor", "negative", "fail", "problem", "issue", "worry", "stress",
            "difficult", "worst", "ugly", "dislike", "error", "compromise", "urgent",
            "spam", "scam", "fraud", "danger", "risk", "threat", "warning", "suspicious",
            "not", "no", "never", "can't", "don't" # Added for more robust negative detection
        }

    def _tokenize(self, text):
        """
        Converts text to lowercase and splits it into words, filtering out non-alphabetic tokens.
        This is an internal helper method.

        Args:
            text (str): The input string message.

        Returns:
            list: A list of lowercase, alphabetic words.
        """
        # Use regex to find all sequences of alphabetic characters
        # This will correctly handle "great!" as "great" and "123" as ignored.
        words = re.findall(r'[a-z]+', text.lower())
        return words

    def analyze(self, text):
        """
        Analyzes the sentiment of the input text.
        Counts positive and negative words and classifies the sentiment.

        Args:
            text (str): The message string to analyze.

        Returns:
            str: The sentiment classification: 'positive', 'negative', or 'neutral'.
        """
        if not text.strip():
            return "neutral" # Empty or whitespace-only messages are neutral

        words = self._tokenize(text)
        
        positive_count = 0
        negative_count = 0

        for word in words:
            if word in self.positive_words:
                positive_count += 1
            elif word in self.negative_words:
                negative_count += 1
        
        # Simple comparison:
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else: # positive_count == negative_count or both are 0
            return "neutral"
