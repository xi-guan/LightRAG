"""
Shared pytest fixtures and configuration for LightRAG tests.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def temp_working_dir():
    """Create a temporary working directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="lightrag_test_")
    yield temp_dir
    # Cleanup after all tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def clean_working_dir(temp_working_dir):
    """Provide a clean working directory for each test."""
    test_dir = os.path.join(temp_working_dir, f"test_{os.getpid()}")
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir
    # Cleanup after each test
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return """
    This is a sample document for testing.
    It contains multiple paragraphs and sentences.

    The purpose of this text is to provide realistic content
    for testing document processing functionality.

    It includes various elements like punctuation, newlines,
    and different sentence structures.
    """


@pytest.fixture
def sample_markdown():
    """Provide sample markdown text for testing."""
    return """
# Main Title

This is a paragraph with **bold** and *italic* text.

## Section 1

- List item 1
- List item 2
- List item 3

## Section 2

```python
def hello():
    print("Hello, World!")
```

This is a [link](https://example.com).
    """


@pytest.fixture
def sample_documents():
    """Provide multiple sample documents for testing."""
    return [
        {
            "id": "doc1",
            "title": "Introduction to AI",
            "content": "Artificial Intelligence is the simulation of human intelligence by machines.",
        },
        {
            "id": "doc2",
            "title": "Machine Learning Basics",
            "content": "Machine Learning is a subset of AI that enables systems to learn from data.",
        },
        {
            "id": "doc3",
            "title": "Deep Learning Overview",
            "content": "Deep Learning uses neural networks with multiple layers to process data.",
        },
    ]


@pytest.fixture
def mock_llm_response():
    """Provide mock LLM response for testing."""
    return {
        "entities": [
            {"name": "AI", "type": "Concept", "description": "Artificial Intelligence"},
            {
                "name": "Machine Learning",
                "type": "Concept",
                "description": "A subset of AI",
            },
        ],
        "relationships": [
            {
                "source": "Machine Learning",
                "target": "AI",
                "type": "IS_PART_OF",
                "description": "Machine Learning is a subset of AI",
            }
        ],
    }


@pytest.fixture
def mock_embedding():
    """Provide mock embedding vector for testing."""
    import numpy as np

    return np.random.rand(1024).tolist()


@pytest.fixture(autouse=True)
def reset_env_vars():
    """Reset environment variables before each test."""
    # Store original values
    original_env = os.environ.copy()

    # Set test defaults
    os.environ["LIGHTRAG_TEST_MODE"] = "true"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_config():
    """Provide mock configuration for testing."""
    return {
        "working_dir": "./test_storage",
        "llm_model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "chunk_size": 1200,
        "chunk_overlap": 100,
        "top_k": 20,
        "max_async": 4,
    }


# Markers for skipping tests based on conditions
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "requires_llm: mark test as requiring LLM API")
    config.addinivalue_line(
        "markers", "requires_embedding: mark test as requiring embedding API"
    )
    config.addinivalue_line(
        "markers", "requires_storage: mark test as requiring storage backend"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to all tests in test_utils.py and test_chunking.py
        if "test_utils" in str(item.fspath) or "test_chunking" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add 'asyncio' marker to async tests
        if "async" in item.name or "aquery" in item.name:
            item.add_marker(pytest.mark.asyncio)


# Helper function for tests
@pytest.fixture
def assert_valid_chunk():
    """Provide a helper function to validate chunk structure."""

    def _assert_valid_chunk(chunk):
        assert isinstance(chunk, dict), "Chunk should be a dictionary"
        assert "content" in chunk, "Chunk should have 'content' field"
        assert "tokens" in chunk, "Chunk should have 'tokens' field"
        assert "chunk_order_index" in chunk, "Chunk should have 'chunk_order_index' field"
        assert isinstance(chunk["content"], str), "Content should be a string"
        assert isinstance(chunk["tokens"], int), "Tokens should be an integer"
        assert isinstance(
            chunk["chunk_order_index"], int
        ), "Chunk order index should be an integer"
        assert chunk["tokens"] > 0, "Tokens should be positive"
        assert chunk["chunk_order_index"] >= 0, "Chunk order index should be non-negative"

    return _assert_valid_chunk


@pytest.fixture
def capture_logs():
    """Capture log messages during test execution."""
    import logging
    from io import StringIO

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    # Add handler to lightrag logger
    logger = logging.getLogger("lightrag")
    logger.addHandler(handler)

    yield log_capture

    # Remove handler after test
    logger.removeHandler(handler)
