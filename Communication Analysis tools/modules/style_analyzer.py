import re

class StyleAnalyzer:
    """
    Analyzes the writing style of text, determining its formality and a style score.
    The score and formality are based on linguistic features and keyword presence.
    """

    def __init__(self):
        """
        Initializes the StyleAnalyzer with lists of formal and informal keywords.
        These lists can be expanded to refine style detection.
        """
        self.formal_keywords = {
            "furthermore", "moreover", "hence", "thus", "consequently", "therefore",
            "sincerely", "regards", "cordially", "to whom it may concern", "pursuant to",
            "in accordance with", "commence", "terminate", "endeavor", "facilitate",
            "utilize", "prioritize", "hereby", "herein", "thereby", "therein", "herewith",
            "acquisition", "disbursement", "ameliorate", "concerning", "regarding", "notwithstanding",
            "respectfully", "additionally", "nevertheless", "consequently", "subsequently",
            "heretofore", "hereunder", "thereafter", "thereupon", "whereby", "whereas",
            "inquire", "advise", "confirm", "request", "duly", "herewith", "thereof",
            "accordingly", "according", "hereby", "herein", "thereby", "therein", "wherefore", "whereupon" # Added more
        }
        self.informal_keywords = {
            "hey", "hi", "lol", "brb", "btw", "gonna", "wanna", "lemme", "y'all",
            "asap", "imo", "fyi", "kinda", "sorta", "chill", "dude", "bro", "yeah",
            "nah", "awesome", "cool", "super", "greetings", "whats up", "cya", "np", "omg",
            "tho", "dunno", "nite", "pls", "thx", "u", "ur", "r", "lmao", "rofl",
            "gotta", "k", "cuz", "ya", "coz", "sup", "yo" # Added more
        }
        # A simple set of common contractions for detecting informality
        self.contractions = {
            "i'm", "you're", "he's", "she's", "it's", "we're", "they're", "i've",
            "you've", "we've", "they've", "i'd", "you'd", "he'd", "she'd", "we'd",
            "they'd", "i'll", "you'll", "he'll", "she'll", "it'll", "we'll", "they'll",
            "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't",
            "won't", "wouldn't", "don't", "doesn't", "didn't", "can't", "couldn't",
            "shouldn't", "mightn't", "mustn't", "shan't", "needn't"
        }

    def _tokenize(self, text):
        """
        Converts text to lowercase and splits it into words, including apostrophes for contractions.
        This is an internal helper method.

        Args:
            text (str): The input string message.

        Returns:
            list: A list of lowercase words, including contractions.
        """
        # Regex to find sequences of alphabetic characters or apostrophes (for contractions)
        # This will correctly tokenize "I'm" as "i'm"
        words = re.findall(r"[a-z']+", text.lower())
        return words

    def analyze(self, text):
        """
        Analyzes the style of the input text, determining a style score and formality.
        The style score is a numerical value (0-100), and formality is 'formal', 'informal', or 'neutral'.

        Args:
            text (str): The message string to analyze.

        Returns:
            dict: A dictionary containing:
                - "Style Score" (float): A numerical score representing the style.
                - "Formality" (str): 'formal', 'informal', or 'neutral'.
        """
        if not text.strip():
            return {"Style Score": 50.0, "Formality": "neutral"} # Default for empty text

        words = self._tokenize(text)
        if not words: # Handle case where tokenization yields no words (e.g., only numbers/symbols)
            return {"Style Score": 50.0, "Formality": "neutral"}

        formal_count = 0
        informal_count = 0
        contraction_count = 0
        total_words = len(words)

        for word in words:
            if word in self.formal_keywords:
                formal_count += 1
            elif word in self.informal_keywords:
                informal_count += 1
            if word in self.contractions:
                contraction_count += 1
        
        # Calculate formality score: Formal words contribute positively, informal/contractions negatively
        # Normalize by total words to get a score between roughly -1 and 1 (or more extreme)
        # Increased weight for formal and contractions to make classification clearer
        # Increased formal weight even more to ensure formal detection
        formality_score = (formal_count * 4 - informal_count * 1.5 - contraction_count * 3) / total_words
        
        formality = "neutral"
        # Adjusted thresholds for formality classification
        # Lowered formal threshold slightly to make it easier to classify as formal
        if formality_score > 0.10: # More formal (was 0.15)
            formality = "formal"
        elif formality_score < -0.15: # More informal (remains same)
            formality = "informal"
        
        # Map formality_score to a 0-100 "Style Score"
        # Let's assume formality_score typically ranges from -0.7 to 0.7 for mapping
        # Clamp it to prevent extreme values from distorting the scale
        clamped_formality_score = max(-0.7, min(0.7, formality_score))
        
        # Linear mapping from [-0.7, 0.7] to [0, 100]
        style_score = round(((clamped_formality_score + 0.7) / 1.4 * 100), 2)
        
        # Ensure style score is within 0-100 bounds
        style_score = max(0.0, min(100.0, style_score))

        return {"Style Score": style_score, "Formality": formality}

