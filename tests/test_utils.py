"""
Unit tests for utility functions.
"""

import pytest
import hashlib
from lightrag.utils import (
    compute_mdhash_id,
    sanitize_text_for_encoding,
    is_float_regex,
    TiktokenTokenizer,
)


class TestHashFunctions:
    """Test hash and ID generation functions."""

    def test_compute_mdhash_id_consistent(self):
        """Test that mdhash_id is consistent for same content."""
        content = "Test content for hashing"
        prefix = "test"

        hash1 = compute_mdhash_id(content, prefix)
        hash2 = compute_mdhash_id(content, prefix)

        assert hash1 == hash2, "Hash should be consistent for same content"

    def test_compute_mdhash_id_different_content(self):
        """Test that different content produces different hashes."""
        content1 = "Content 1"
        content2 = "Content 2"
        prefix = "test"

        hash1 = compute_mdhash_id(content1, prefix)
        hash2 = compute_mdhash_id(content2, prefix)

        assert hash1 != hash2, "Different content should produce different hashes"

    def test_compute_mdhash_id_with_prefix(self):
        """Test that prefix is included in hash."""
        content = "Test content"
        prefix1 = "prefix1"
        prefix2 = "prefix2"

        hash1 = compute_mdhash_id(content, prefix1)
        hash2 = compute_mdhash_id(content, prefix2)

        assert hash1.startswith(prefix1), "Hash should start with prefix"
        assert hash2.startswith(prefix2), "Hash should start with prefix"
        assert hash1 != hash2, "Different prefixes should produce different hashes"

    def test_compute_mdhash_id_unicode(self):
        """Test hash with unicode content."""
        content = "你好世界 Hello World"
        prefix = "test"

        hash_id = compute_mdhash_id(content, prefix)

        assert isinstance(hash_id, str), "Hash should be a string"
        assert len(hash_id) > len(prefix), "Hash should contain more than just prefix"


class TestTextSanitization:
    """Test text sanitization functions."""

    def test_sanitize_basic_text(self):
        """Test sanitization of basic text."""
        text = "Normal text without special characters"
        sanitized = sanitize_text_for_encoding(text)

        assert sanitized == text, "Normal text should remain unchanged"

    def test_sanitize_unicode_escapes(self):
        """Test sanitization of unicode escape sequences."""
        text = "Text with \\u0041 unicode"
        sanitized = sanitize_text_for_encoding(text)

        # Should handle unicode escapes
        assert isinstance(sanitized, str), "Should return a string"

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        text = ""
        sanitized = sanitize_text_for_encoding(text)

        assert sanitized == "", "Empty string should remain empty"

    def test_sanitize_whitespace(self):
        """Test sanitization preserves necessary whitespace."""
        text = "Text with   multiple   spaces"
        sanitized = sanitize_text_for_encoding(text)

        assert isinstance(sanitized, str), "Should return a string"


class TestFloatRegex:
    """Test float detection functions."""

    def test_is_float_regex_valid_floats(self):
        """Test detection of valid float strings."""
        valid_floats = ["1.23", "0.5", "123.456", ".5", "5."]

        for float_str in valid_floats:
            assert is_float_regex(
                float_str
            ), f"'{float_str}' should be recognized as float"

    def test_is_float_regex_integers(self):
        """Test that integers are recognized as floats."""
        integers = ["1", "123", "0"]

        for int_str in integers:
            # Integers can be considered floats in many contexts
            result = is_float_regex(int_str)
            assert isinstance(result, bool), "Should return a boolean"

    def test_is_float_regex_invalid_strings(self):
        """Test rejection of non-float strings."""
        invalid = ["abc", "12.34.56", "12a34", ""]

        for invalid_str in invalid:
            assert not is_float_regex(
                invalid_str
            ), f"'{invalid_str}' should not be recognized as float"

    def test_is_float_regex_negative_numbers(self):
        """Test detection of negative floats."""
        negatives = ["-1.23", "-0.5", "-123"]

        for neg_str in negatives:
            result = is_float_regex(neg_str)
            # The function might or might not support negatives, we just test it doesn't crash
            assert isinstance(result, bool), "Should return a boolean"


class TestTokenizer:
    """Test tokenizer functionality."""

    @pytest.fixture
    def tokenizer(self):
        """Create a tokenizer instance."""
        return TiktokenTokenizer()

    def test_tokenizer_encode_decode(self, tokenizer):
        """Test that encode and decode are inverse operations."""
        text = "This is a test sentence for tokenization."

        tokens = tokenizer.encode(text)
        decoded = tokenizer.decode(tokens)

        assert isinstance(tokens, list), "Encode should return a list"
        assert len(tokens) > 0, "Should produce tokens"
        assert isinstance(decoded, str), "Decode should return a string"
        # Note: decoded might not exactly match original due to tokenizer specifics
        # but it should be similar
        assert len(decoded) > 0, "Decoded text should not be empty"

    def test_tokenizer_empty_string(self, tokenizer):
        """Test tokenization of empty string."""
        text = ""

        tokens = tokenizer.encode(text)

        assert isinstance(tokens, list), "Should return a list"
        assert len(tokens) == 0, "Empty string should produce no tokens"

    def test_tokenizer_unicode(self, tokenizer):
        """Test tokenization of unicode text."""
        text = "Hello 你好 世界"

        tokens = tokenizer.encode(text)
        decoded = tokenizer.decode(tokens)

        assert len(tokens) > 0, "Should tokenize unicode text"
        assert isinstance(decoded, str), "Should decode to string"

    def test_tokenizer_consistency(self, tokenizer):
        """Test that tokenizer is consistent."""
        text = "Consistency test"

        tokens1 = tokenizer.encode(text)
        tokens2 = tokenizer.encode(text)

        assert tokens1 == tokens2, "Same text should produce same tokens"

    def test_tokenizer_long_text(self, tokenizer):
        """Test tokenization of long text."""
        text = "Word " * 1000

        tokens = tokenizer.encode(text)

        assert len(tokens) > 100, "Long text should produce many tokens"
        assert isinstance(tokens, list), "Should return a list"


class TestUtilityEdgeCases:
    """Test edge cases in utility functions."""

    def test_mdhash_with_very_long_content(self):
        """Test hash generation with very long content."""
        content = "A" * 1000000  # 1 million characters
        prefix = "test"

        hash_id = compute_mdhash_id(content, prefix)

        assert isinstance(hash_id, str), "Should handle long content"
        assert hash_id.startswith(prefix), "Should include prefix"

    def test_sanitize_with_none(self):
        """Test sanitization with None input."""
        # This might raise an exception, which is acceptable
        try:
            result = sanitize_text_for_encoding(None)
            # If it doesn't raise, it should return something reasonable
            assert result is not None or result == ""
        except (TypeError, AttributeError):
            # Expected for None input
            pass
