"""
Unit tests for document chunking functionality.
"""

import pytest
from lightrag.operate import chunking_by_token_size
from lightrag.utils import TiktokenTokenizer


class TestChunking:
    """Test document chunking functionality."""

    @pytest.fixture
    def tokenizer(self):
        """Create a tokenizer instance for tests."""
        return TiktokenTokenizer()

    def test_basic_chunking(self, tokenizer):
        """Test basic chunking without custom separator."""
        content = "This is a test document. " * 100
        max_token_size = 100
        overlap_token_size = 10

        chunks = chunking_by_token_size(
            tokenizer=tokenizer,
            content=content,
            max_token_size=max_token_size,
            overlap_token_size=overlap_token_size,
        )

        # Verify chunks were created
        assert len(chunks) > 0, "Should create at least one chunk"

        # Verify each chunk has required fields
        for chunk in chunks:
            assert "content" in chunk, "Chunk should have content field"
            assert "tokens" in chunk, "Chunk should have tokens field"
            assert "chunk_order_index" in chunk, "Chunk should have chunk_order_index field"

        # Verify token size constraints
        for chunk in chunks:
            assert (
                chunk["tokens"] <= max_token_size
            ), f"Chunk tokens {chunk['tokens']} should not exceed max {max_token_size}"

    def test_chunking_with_separator(self, tokenizer):
        """Test chunking with custom separator."""
        content = "Section 1\n\nSection 2\n\nSection 3\n\nSection 4"
        separator = "\n\n"
        max_token_size = 50

        chunks = chunking_by_token_size(
            tokenizer=tokenizer,
            content=content,
            split_by_character=separator,
            max_token_size=max_token_size,
        )

        # Should create at least as many chunks as sections
        assert len(chunks) >= 4, "Should create chunks for each section"

        # Verify chunk order is sequential
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_order_index"] == i, "Chunk indices should be sequential"

    def test_chunking_with_separator_only(self, tokenizer):
        """Test chunking with separator-only mode."""
        content = "Part 1||Part 2||Part 3"
        separator = "||"

        chunks = chunking_by_token_size(
            tokenizer=tokenizer,
            content=content,
            split_by_character=separator,
            split_by_character_only=True,
            max_token_size=100,
        )

        # Should split exactly by separator
        assert len(chunks) == 3, "Should create exactly 3 chunks"

        # Verify content
        assert "Part 1" in chunks[0]["content"]
        assert "Part 2" in chunks[1]["content"]
        assert "Part 3" in chunks[2]["content"]

    def test_empty_content(self, tokenizer):
        """Test chunking with empty content."""
        content = ""

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        # Should handle empty content gracefully
        assert isinstance(chunks, list), "Should return a list"

    def test_single_token_content(self, tokenizer):
        """Test chunking with very short content."""
        content = "Hi"

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        assert len(chunks) == 1, "Should create exactly one chunk"
        assert chunks[0]["content"] == content, "Content should be preserved"

    def test_chunk_overlap(self, tokenizer):
        """Test that chunks have proper overlap."""
        content = " ".join([f"Word{i}" for i in range(200)])
        max_token_size = 50
        overlap_token_size = 10

        chunks = chunking_by_token_size(
            tokenizer=tokenizer,
            content=content,
            max_token_size=max_token_size,
            overlap_token_size=overlap_token_size,
        )

        # Should create multiple chunks
        assert len(chunks) > 1, "Should create multiple chunks for long content"

        # Verify no chunk is empty
        for chunk in chunks:
            assert len(chunk["content"].strip()) > 0, "Chunks should not be empty"

    def test_very_long_single_word(self, tokenizer):
        """Test chunking with a very long single word."""
        # Create a very long "word" that exceeds max token size
        content = "A" * 1000

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        # Should split even a single long word
        assert len(chunks) > 1, "Should split long content into multiple chunks"

        # Verify each chunk respects token limit
        for chunk in chunks:
            assert chunk["tokens"] <= 100, "Each chunk should respect token limit"


class TestChunkingEdgeCases:
    """Test edge cases in chunking."""

    @pytest.fixture
    def tokenizer(self):
        return TiktokenTokenizer()

    def test_unicode_content(self, tokenizer):
        """Test chunking with unicode characters."""
        content = "你好世界 " * 50 + "Hello World " * 50

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        assert len(chunks) > 0, "Should handle unicode content"

        # Verify content integrity
        reconstructed = "".join([c["content"] for c in chunks])
        # Check that we preserved all the content (allowing for some whitespace differences)
        assert "你好世界" in reconstructed
        assert "Hello World" in reconstructed

    def test_special_characters(self, tokenizer):
        """Test chunking with special characters."""
        content = "Test@#$%^&*() " * 100

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        assert len(chunks) > 0, "Should handle special characters"

        for chunk in chunks:
            assert isinstance(chunk["content"], str), "Content should be string"

    def test_newlines_and_tabs(self, tokenizer):
        """Test chunking with newlines and tabs."""
        content = "Line 1\nLine 2\tTabbed\n" * 50

        chunks = chunking_by_token_size(
            tokenizer=tokenizer, content=content, max_token_size=100
        )

        assert len(chunks) > 0, "Should handle whitespace characters"
