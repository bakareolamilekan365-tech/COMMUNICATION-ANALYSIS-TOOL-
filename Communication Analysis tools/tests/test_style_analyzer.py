import unittest
from modules.style_analyzer import StyleAnalyzer

class TestStyleAnalyzer(unittest.TestCase):
    """
    Test suite for the StyleAnalyzer class.

    Covers style score calculation and formality classification for various
    text inputs, including formal, informal, and mixed styles.
    """

    def setUp(self):
        """
        Set up common resources for tests.
        Initializes a new StyleAnalyzer instance before each test.
        """
        self.analyzer = StyleAnalyzer()

    def test_formal_style(self):
        """
        Tests the analyze method with a message expected to be classified as formal.
        Verifies that it's not informal and the style score is high.
        """
        formal_text_1 = "Furthermore, we endeavor to facilitate the optimal utilization of resources."
        result_1 = self.analyzer.analyze(formal_text_1)
        self.assertNotEqual(result_1["Formality"], "informal") # Should not be informal
        self.assertGreaterEqual(result_1["Style Score"], 50) # Should be at least neutral or higher

        formal_text_2 = "Pursuant to our previous correspondence, please find the attached document."
        result_2 = self.analyzer.analyze(formal_text_2)
        self.assertNotEqual(result_2["Formality"], "informal")
        self.assertGreaterEqual(result_2["Style Score"], 50)

        formal_text_3 = "Respectfully, we wish to inquire concerning this matter."
        result_3 = self.analyzer.analyze(formal_text_3)
        self.assertNotEqual(result_3["Formality"], "informal")
        self.assertGreaterEqual(result_3["Style Score"], 50)

    def test_informal_style(self):
        """
        Tests the analyze method with a message expected to be classified as informal.
        Verifies both the 'Formality' tag and the 'Style Score' range.
        """
        informal_text_1 = "Hey dude, what's up? Wanna grab a coffee asap?"
        result_1 = self.analyzer.analyze(informal_text_1)
        self.assertEqual(result_1["Formality"], "informal")
        self.assertLessEqual(result_1["Style Score"], 40) # Expect lower score for informal

        informal_text_2 = "Lol, I'm gonna chill this weekend, btw."
        result_2 = self.analyzer.analyze(informal_text_2)
        self.assertEqual(result_2["Formality"], "informal")
        self.assertLessEqual(result_2["Style Score"], 40)

        informal_text_3 = "Thx for the info, cya!"
        result_3 = self.analyzer.analyze(informal_text_3)
        self.assertEqual(result_3["Formality"], "informal")
        self.assertLessEqual(result_3["Style Score"], 40)

    def test_empty_message(self):
        """
        Tests the analyze method with an empty string.
        Should return a default neutral style and a score of 50.0.
        """
        result = self.analyzer.analyze("")
        self.assertEqual(result["Formality"], "neutral")
        self.assertEqual(result["Style Score"], 50.0)
        result_whitespace = self.analyzer.analyze("   \t\n")
        self.assertEqual(result_whitespace["Formality"], "neutral")
        self.assertEqual(result_whitespace["Style Score"], 50.0)

    def test_mixed_style(self):
        """
        Tests the analyze method with a message containing a mix of formal and informal elements,
        expecting a classification that is not informal and leans towards neutral/formal.
        """
        # This message has both informal (Hi team, I'm) and formal (confirm, Furthermore, prioritize)
        mixed_text = "Hi team, I'm writing to confirm our meeting. Furthermore, let's prioritize the next steps."
        result = self.analyzer.analyze(mixed_text)
        # Should not be informal, and should lean towards neutral or formal
        self.assertNotEqual(result["Formality"], "informal")
        self.assertGreaterEqual(result["Style Score"], 50) # Should be at least neutral or higher

    def test_contractions_impact(self):
        """
        Tests if the presence of contractions correctly influences the formality towards informal.
        """
        text_with_contractions = "I'm sure you'll agree it's a good idea. We're gonna make it."
        result = self.analyzer.analyze(text_with_contractions)
        self.assertEqual(result["Formality"], "informal")
        self.assertLessEqual(result["Style Score"], 40) # Should be informal score

    def test_neutral_style(self):
        """
        Tests messages that should be classified as neutral formality.
        """
        neutral_text = "The cat sat on the mat. The dog barked at the moon."
        result = self.analyzer.analyze(neutral_text)
        self.assertEqual(result["Formality"], "neutral")
        self.assertAlmostEqual(result["Style Score"], 50.0, places=2) # Use assertAlmostEqual for floats

        neutral_text_2 = "This is a simple sentence."
        result_2 = self.analyzer.analyze(neutral_text_2)
        self.assertEqual(result_2["Formality"], "neutral")
        self.assertAlmostEqual(result_2["Style Score"], 50.0, places=2)

if __name__ == '__main__':
    unittest.main()
