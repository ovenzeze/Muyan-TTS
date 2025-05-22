import unittest
import sys
import os
from io import BytesIO

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the pure Python utility functions that don't require external dependencies
from sovits.utils import (
    clean_and_split_text,
    should_skip_period,
    fix_spaced_caps,
    merge_sentences_minimum_n,
    count_audio_tokens,
    HParams,
    only_punc,
    clean_path
)


class TestUtils(unittest.TestCase):
    
    def test_should_skip_period(self):
        # Test with single letter abbreviation
        self.assertTrue(should_skip_period("This is a test with A.", 21))
        
        # Test with known abbreviations
        self.assertTrue(should_skip_period("This is Mr. Smith", 9))
        self.assertTrue(should_skip_period("This is Dr. Smith", 9))
        self.assertTrue(should_skip_period("This is Mrs. Smith", 10))
        self.assertTrue(should_skip_period("This is St. Mary", 9))
        
        # Test with non-abbreviation
        self.assertFalse(should_skip_period("This is a sentence.", 18))
        
        # Test with no space before period
        self.assertTrue(should_skip_period("A.", 1))
    
    def test_fix_spaced_caps(self):
        # Test with spaced capital letters
        self.assertEqual(fix_spaced_caps("U S A"), "USA")
        self.assertEqual(fix_spaced_caps("N Y C"), "NYC")
        
        # Test with mixed case
        self.assertEqual(fix_spaced_caps("U S A is a country"), "USA is a country")
        
        # Test with possessive
        self.assertEqual(fix_spaced_caps("U S A's flag"), "USA's flag")
        
        # Test with no spaced caps
        self.assertEqual(fix_spaced_caps("This is a test"), "This is a test")
    
    def test_clean_and_split_text(self):
        # Test with simple sentence
        text = "This is a test."
        result = clean_and_split_text(text)
        self.assertEqual(result, ["This is a test."])
        
        # Test with multiple sentences
        text = "This is sentence one. This is sentence two! This is sentence three?"
        result = clean_and_split_text(text)
        self.assertEqual(result, ["This is sentence one.", "This is sentence two!", "This is sentence three?"])
        
        # Test with abbreviations
        text = "This is Mr. Smith. He is a Dr. in medicine."
        result = clean_and_split_text(text)
        self.assertEqual(result, ["This is Mr. Smith.", "He is a Dr. in medicine."])
        
        # Test with spaced caps
        text = "I live in the U S A. It's a nice country."
        result = clean_and_split_text(text)
        self.assertEqual(result, ["I live in the USA.", "It's a nice country."])
    
    def test_merge_sentences_minimum_n(self):
        # Test with sentences that should be merged
        sentences = ["This is short.", "This too.", "Another one."]
        result = merge_sentences_minimum_n(sentences, 5)
        self.assertEqual(result, ["This is short. This too.", "Another one."])
        
        # Test with sentences that are already long enough
        sentences = ["This is a longer sentence with many words.", "This is another long sentence."]
        result = merge_sentences_minimum_n(sentences, 5)
        self.assertEqual(result, ["This is a longer sentence with many words.", "This is another long sentence."])
        
        # Test with empty list
        self.assertEqual(merge_sentences_minimum_n([], 5), [])
    
    def test_count_audio_tokens(self):
        # Test with strings containing audio tokens
        strings = [
            "<|audio_token_1|><|audio_token_2|>",
            "<|audio_token_3|>",
            "No tokens here"
        ]
        result = count_audio_tokens(strings)
        self.assertEqual(result, [2, 1, 0])
    
    def test_only_punc(self):
        # Test with only punctuation
        self.assertTrue(only_punc(".,!?"))
        
        # Test with mixed content
        self.assertFalse(only_punc("Hello!"))
        
        # Test with alphanumeric
        self.assertFalse(only_punc("123"))
        
        # Test with empty string
        self.assertTrue(only_punc(""))
    
    def test_clean_path(self):
        # Test with trailing slashes
        self.assertEqual(clean_path("/path/to/file/"), "/path/to/file")
        self.assertEqual(clean_path("C:\\path\\to\\file\\"), "C:\\path\\to\\file")
        
        # Test with quotes
        self.assertEqual(clean_path("'/path/to/file'"), "/path/to/file")
        self.assertEqual(clean_path('"/path/to/file"'), "/path/to/file")
        
        # Test with whitespace
        self.assertEqual(clean_path(" /path/to/file "), "/path/to/file")
    
    def test_hparams(self):
        # Test initialization
        params = HParams(a=1, b="test", c={"d": 2})
        self.assertEqual(params.a, 1)
        self.assertEqual(params.b, "test")
        self.assertEqual(params.c.d, 2)
        
        # Test dictionary-like access
        self.assertEqual(params["a"], 1)
        
        # Test setting values
        params["e"] = 3
        self.assertEqual(params.e, 3)
        
        # Test contains
        self.assertTrue("a" in params)
        self.assertFalse("z" in params)
        
        # Test length
        self.assertEqual(len(params), 4)  # a, b, c, e


if __name__ == "__main__":
    unittest.main()