"""
Configs for the LightRAG API.
"""

import os
import argparse
import logging
from dotenv import load_dotenv
from lightrag.utils import get_env_value
from lightrag.llm.binding_options import (
    GeminiEmbeddingOptions,
    GeminiLLMOptions,
    OllamaEmbeddingOptions,
    OllamaLLMOptions,
    OpenAILLMOptions,
)
from lightrag.base import OllamaServerInfos
import sys

from lightrag.constants import (
    DEFAULT_WOKERS,
    DEFAULT_TIMEOUT,
    DEFAULT_TOP_K,
    DEFAULT_CHUNK_TOP_K,
    DEFAULT_HISTORY_TURNS,
    DEFAULT_MAX_ENTITY_TOKENS,
    DEFAULT_MAX_RELATION_TOKENS,
    DEFAULT_MAX_TOTAL_TOKENS,
    DEFAULT_COSINE_THRESHOLD,
    DEFAULT_RELATED_CHUNK_NUMBER,
    DEFAULT_MIN_RERANK_SCORE,
    DEFAULT_FORCE_LLM_SUMMARY_ON_MERGE,
    DEFAULT_MAX_ASYNC,
    DEFAULT_SUMMARY_MAX_TOKENS,
    DEFAULT_SUMMARY_LENGTH_RECOMMENDED,
    DEFAULT_SUMMARY_CONTEXT_SIZE,
    DEFAULT_SUMMARY_LANGUAGE,
    DEFAULT_EMBEDDING_FUNC_MAX_ASYNC,
    DEFAULT_EMBEDDING_BATCH_NUM,
    DEFAULT_OLLAMA_MODEL_NAME,
    DEFAULT_OLLAMA_MODEL_TAG,
    DEFAULT_RERANK_BINDING,
    DEFAULT_ENTITY_TYPES,
)

# use the .env that is inside the current folder
# allows to use different .env file for each lightrag instance
# the OS environment variables take precedence over the .env file
load_dotenv(dotenv_path=".env", override=False)

logger = logging.getLogger(__name__)


def get_env_value_with_fallback(
    new_key: str,
    old_key: str,
    default: any,
    value_type: type = str,
    special_none: bool = False,
) -> any:
    """
    Get value with fallback priority: LIGHTRAG_* prefix > old key > default

    Provides backward compatibility for environment variables while migrating
    to the new LIGHTRAG_* prefix naming convention.

    Args:
        new_key: New environment variable key (with LIGHTRAG_ prefix)
        old_key: Old environment variable key (without prefix)
        default: Default value if neither env variable is set
        value_type: Type to convert the value to
        special_none: If True, return None when value is "None" string

    Returns:
        Value from environment or default

    Examples:
        # Try LIGHTRAG_LLM_MODEL first, fall back to LLM_MODEL
        model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_MODEL", "LLM_MODEL", "mistral-nemo:latest"
        )
    """
    # Try new key first (LIGHTRAG_* prefix) - preferred
    value = os.getenv(new_key)
    if value is not None:
        logger.debug(f"Using {new_key}={value}")
    else:
        # Fallback to old key (backward compatibility)
        value = os.getenv(old_key)
        if value is not None:
            logger.debug(
                f"Using {old_key}={value} (fallback from {new_key}, "
                f"consider migrating to LIGHTRAG_* prefix)"
            )

    if value is None:
        return default

    # Handle special case for "None" string
    if special_none and value == "None":
        return None

    if value_type is bool:
        return value.lower() in ("true", "1", "yes", "t", "on")

    if value_type is list:
        try:
            import json

            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value.split(",") if value else []

    try:
        return value_type(value)
    except (ValueError, TypeError):
        logger.warning(
            f"Failed to convert {new_key}/{old_key}={value} to {value_type}, "
            f"using default={default}"
        )
        return default


ollama_server_infos = OllamaServerInfos()


class DefaultRAGStorageConfig:
    KV_STORAGE = "JsonKVStorage"
    VECTOR_STORAGE = "NanoVectorDBStorage"
    GRAPH_STORAGE = "NetworkXStorage"
    DOC_STATUS_STORAGE = "JsonDocStatusStorage"


def get_default_host(binding_type: str) -> str:
    default_hosts = {
        "ollama": os.getenv("LLM_BINDING_HOST", "http://localhost:11434"),
        "lollms": os.getenv("LLM_BINDING_HOST", "http://localhost:9600"),
        "azure_openai": os.getenv("AZURE_OPENAI_ENDPOINT", "https://api.openai.com/v1"),
        "openai": os.getenv("LLM_BINDING_HOST", "https://api.openai.com/v1"),
        "gemini": os.getenv(
            "LLM_BINDING_HOST", "https://generativelanguage.googleapis.com"
        ),
    }
    return default_hosts.get(
        binding_type, os.getenv("LLM_BINDING_HOST", "http://localhost:11434")
    )  # fallback to ollama if unknown


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments with environment variable fallback

    Args:
        is_uvicorn_mode: Whether running under uvicorn mode

    Returns:
        argparse.Namespace: Parsed arguments
    """

    parser = argparse.ArgumentParser(description="LightRAG API Server")

    # Server configuration
    parser.add_argument(
        "--host",
        default=get_env_value("HOST", "0.0.0.0"),
        help="Server host (default: from env or 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=get_env_value("PORT", 9621, int),
        help="Server port (default: from env or 9621)",
    )

    # Directory configuration
    parser.add_argument(
        "--working-dir",
        default=get_env_value("WORKING_DIR", "./rag_storage"),
        help="Working directory for RAG storage (default: from env or ./rag_storage)",
    )
    parser.add_argument(
        "--input-dir",
        default=get_env_value("INPUT_DIR", "./inputs"),
        help="Directory containing input documents (default: from env or ./inputs)",
    )

    parser.add_argument(
        "--timeout",
        default=get_env_value("TIMEOUT", DEFAULT_TIMEOUT, int, special_none=True),
        type=int,
        help="Timeout in seconds (useful when using slow AI). Use None for infinite timeout",
    )

    # RAG configuration
    parser.add_argument(
        "--max-async",
        type=int,
        default=get_env_value("MAX_ASYNC", DEFAULT_MAX_ASYNC, int),
        help=f"Maximum async operations (default: from env or {DEFAULT_MAX_ASYNC})",
    )
    parser.add_argument(
        "--summary-max-tokens",
        type=int,
        default=get_env_value("SUMMARY_MAX_TOKENS", DEFAULT_SUMMARY_MAX_TOKENS, int),
        help=f"Maximum token size for entity/relation summary(default: from env or {DEFAULT_SUMMARY_MAX_TOKENS})",
    )
    parser.add_argument(
        "--summary-context-size",
        type=int,
        default=get_env_value(
            "SUMMARY_CONTEXT_SIZE", DEFAULT_SUMMARY_CONTEXT_SIZE, int
        ),
        help=f"LLM Summary Context size (default: from env or {DEFAULT_SUMMARY_CONTEXT_SIZE})",
    )
    parser.add_argument(
        "--summary-length-recommended",
        type=int,
        default=get_env_value(
            "SUMMARY_LENGTH_RECOMMENDED", DEFAULT_SUMMARY_LENGTH_RECOMMENDED, int
        ),
        help=f"LLM Summary Context size (default: from env or {DEFAULT_SUMMARY_LENGTH_RECOMMENDED})",
    )

    # Logging configuration
    parser.add_argument(
        "--log-level",
        default=get_env_value("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: from env or INFO)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=get_env_value("VERBOSE", False, bool),
        help="Enable verbose debug output(only valid for DEBUG log-level)",
    )

    parser.add_argument(
        "--key",
        type=str,
        default=get_env_value("LIGHTRAG_API_KEY", None),
        help="API key for authentication. This protects lightrag server against unauthorized access",
    )

    # Optional https parameters
    parser.add_argument(
        "--ssl",
        action="store_true",
        default=get_env_value("SSL", False, bool),
        help="Enable HTTPS (default: from env or False)",
    )
    parser.add_argument(
        "--ssl-certfile",
        default=get_env_value("SSL_CERTFILE", None),
        help="Path to SSL certificate file (required if --ssl is enabled)",
    )
    parser.add_argument(
        "--ssl-keyfile",
        default=get_env_value("SSL_KEYFILE", None),
        help="Path to SSL private key file (required if --ssl is enabled)",
    )

    # Ollama model configuration
    parser.add_argument(
        "--simulated-model-name",
        type=str,
        default=get_env_value("OLLAMA_EMULATING_MODEL_NAME", DEFAULT_OLLAMA_MODEL_NAME),
        help="Name for the simulated Ollama model (default: from env or lightrag)",
    )

    parser.add_argument(
        "--simulated-model-tag",
        type=str,
        default=get_env_value("OLLAMA_EMULATING_MODEL_TAG", DEFAULT_OLLAMA_MODEL_TAG),
        help="Tag for the simulated Ollama model (default: from env or latest)",
    )

    # Namespace
    parser.add_argument(
        "--workspace",
        type=str,
        default=get_env_value("WORKSPACE", ""),
        help="Default workspace for all storage",
    )

    # Server workers configuration
    parser.add_argument(
        "--workers",
        type=int,
        default=get_env_value("WORKERS", DEFAULT_WOKERS, int),
        help="Number of worker processes (default: from env or 1)",
    )

    # LLM and embedding bindings
    parser.add_argument(
        "--llm-binding",
        type=str,
        default=get_env_value_with_fallback(
            "LIGHTRAG_LLM_PROVIDER", "LLM_BINDING", "ollama"
        ),
        choices=[
            "lollms",
            "ollama",
            "openai",
            "openai-ollama",
            "azure_openai",
            "aws_bedrock",
            "gemini",
        ],
        help="LLM binding type (default: from env or ollama)",
    )
    parser.add_argument(
        "--embedding-binding",
        type=str,
        default=get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_PROVIDER", "EMBEDDING_BINDING", "ollama"
        ),
        choices=[
            "lollms",
            "ollama",
            "openai",
            "azure_openai",
            "aws_bedrock",
            "jina",
            "gemini",
        ],
        help="Embedding binding type (default: from env or ollama)",
    )
    parser.add_argument(
        "--rerank-binding",
        type=str,
        default=get_env_value_with_fallback(
            "LIGHTRAG_RERANK_PROVIDER", "RERANK_BINDING", DEFAULT_RERANK_BINDING
        ),
        choices=["null", "cohere", "jina", "aliyun"],
        help=f"Rerank binding type (default: from env or {DEFAULT_RERANK_BINDING})",
    )

    # Document loading engine configuration
    parser.add_argument(
        "--docling",
        action="store_true",
        default=False,
        help="Enable DOCLING document loading engine (default: from env or DEFAULT)",
    )

    # Conditionally add binding options defined in binding_options module
    # This will add command line arguments for all binding options (e.g., --ollama-embedding-num_ctx)
    # and corresponding environment variables (e.g., OLLAMA_EMBEDDING_NUM_CTX)
    if "--llm-binding" in sys.argv:
        try:
            idx = sys.argv.index("--llm-binding")
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "ollama":
                OllamaLLMOptions.add_args(parser)
        except IndexError:
            pass
    elif os.environ.get("LLM_BINDING") == "ollama":
        OllamaLLMOptions.add_args(parser)

    if "--embedding-binding" in sys.argv:
        try:
            idx = sys.argv.index("--embedding-binding")
            if idx + 1 < len(sys.argv):
                if sys.argv[idx + 1] == "ollama":
                    OllamaEmbeddingOptions.add_args(parser)
                elif sys.argv[idx + 1] == "gemini":
                    GeminiEmbeddingOptions.add_args(parser)
        except IndexError:
            pass
    else:
        env_embedding_binding = os.environ.get("EMBEDDING_BINDING")
        if env_embedding_binding == "ollama":
            OllamaEmbeddingOptions.add_args(parser)
        elif env_embedding_binding == "gemini":
            GeminiEmbeddingOptions.add_args(parser)

    # Add OpenAI LLM options when llm-binding is openai or azure_openai
    if "--llm-binding" in sys.argv:
        try:
            idx = sys.argv.index("--llm-binding")
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1] in [
                "openai",
                "azure_openai",
            ]:
                OpenAILLMOptions.add_args(parser)
        except IndexError:
            pass
    elif os.environ.get("LLM_BINDING") in ["openai", "azure_openai"]:
        OpenAILLMOptions.add_args(parser)

    if "--llm-binding" in sys.argv:
        try:
            idx = sys.argv.index("--llm-binding")
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "gemini":
                GeminiLLMOptions.add_args(parser)
        except IndexError:
            pass
    elif os.environ.get("LLM_BINDING") == "gemini":
        GeminiLLMOptions.add_args(parser)

    args = parser.parse_args()

    # convert relative path to absolute path
    args.working_dir = os.path.abspath(args.working_dir)
    args.input_dir = os.path.abspath(args.input_dir)

    # Inject storage configuration from environment variables
    args.kv_storage = get_env_value_with_fallback(
        "LIGHTRAG_STORAGE_KV_STORAGE",
        "LIGHTRAG_KV_STORAGE",
        DefaultRAGStorageConfig.KV_STORAGE,
    )
    args.doc_status_storage = get_env_value_with_fallback(
        "LIGHTRAG_STORAGE_DOC_STATUS_STORAGE",
        "LIGHTRAG_DOC_STATUS_STORAGE",
        DefaultRAGStorageConfig.DOC_STATUS_STORAGE,
    )
    args.graph_storage = get_env_value_with_fallback(
        "LIGHTRAG_STORAGE_GRAPH_STORAGE",
        "LIGHTRAG_GRAPH_STORAGE",
        DefaultRAGStorageConfig.GRAPH_STORAGE,
    )
    args.vector_storage = get_env_value_with_fallback(
        "LIGHTRAG_STORAGE_VECTOR_STORAGE",
        "LIGHTRAG_VECTOR_STORAGE",
        DefaultRAGStorageConfig.VECTOR_STORAGE,
    )

    # Get MAX_PARALLEL_INSERT from environment
    args.max_parallel_insert = get_env_value_with_fallback(
        "LIGHTRAG_PERFORMANCE_MAX_PARALLEL_INSERT", "MAX_PARALLEL_INSERT", 2, int
    )

    # Get MAX_GRAPH_NODES from environment
    args.max_graph_nodes = get_env_value_with_fallback(
        "LIGHTRAG_PERFORMANCE_MAX_GRAPH_NODES", "MAX_GRAPH_NODES", 1000, int
    )

    # Get ENTITY_EXTRACT_MAX_GLEANING from environment
    args.entity_extract_max_gleaning = get_env_value_with_fallback(
        "LIGHTRAG_ENTITY_EXTRACTION_MAX_GLEANING", "MAX_GLEANING", 1, int
    )

    # Handle openai-ollama special case
    if args.llm_binding == "openai-ollama":
        args.llm_binding = "openai"
        args.embedding_binding = "ollama"

    # Load provider-specific LLM configuration based on selected provider
    llm_provider = args.llm_binding
    if llm_provider == "ollama":
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OLLAMA_MODEL", "LLM_MODEL", "mistral-nemo:latest"
        )
        args.llm_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OLLAMA_HOST", "LLM_BINDING_HOST", "http://localhost:11434"
        )
        args.ollama_num_ctx = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OLLAMA_NUM_CTX", "OLLAMA_NUM_CTX", 32768, int
        )
        args.llm_binding_api_key = None  # Ollama doesn't need API key
    elif llm_provider == "openai":
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OPENAI_MODEL", "LLM_MODEL", "gpt-4o-mini"
        )
        args.llm_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OPENAI_API_KEY",
            "LLM_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.llm_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_LLM_OPENAI_BASE_URL",
            "LLM_BINDING_HOST",
            "https://api.openai.com/v1",
        )
    elif llm_provider == "azure_openai":
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_AZURE_OPENAI_MODEL", "LLM_MODEL", "gpt-4"
        )
        args.llm_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_LLM_AZURE_OPENAI_API_KEY",
            "LLM_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.llm_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_LLM_AZURE_OPENAI_ENDPOINT", "LLM_BINDING_HOST", ""
        )
        args.azure_deployment = get_env_value(
            "LIGHTRAG_LLM_AZURE_OPENAI_DEPLOYMENT", ""
        )
    elif llm_provider == "anthropic":
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_ANTHROPIC_MODEL", "LLM_MODEL", "claude-3-sonnet-20240229"
        )
        args.llm_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_LLM_ANTHROPIC_API_KEY",
            "LLM_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.llm_binding_host = "https://api.anthropic.com"
    elif llm_provider == "gemini":
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_GEMINI_MODEL", "LLM_MODEL", "gemini-pro"
        )
        args.llm_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_LLM_GEMINI_API_KEY",
            "LLM_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.llm_binding_host = "https://generativelanguage.googleapis.com"
    else:
        # Fallback for unknown providers
        args.llm_model = get_env_value_with_fallback(
            "LIGHTRAG_LLM_MODEL", "LLM_MODEL", "mistral-nemo:latest"
        )
        args.llm_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_LLM_BASE_URL", "LLM_BINDING_HOST", get_default_host(llm_provider)
        )
        args.llm_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_LLM_API_KEY", "LLM_BINDING_API_KEY", None, special_none=True
        )

    # Load provider-specific Embedding configuration
    embedding_provider = args.embedding_binding
    if embedding_provider == "ollama":
        args.embedding_model = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OLLAMA_MODEL", "EMBEDDING_MODEL", "bge-m3:latest"
        )
        args.embedding_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OLLAMA_HOST",
            "EMBEDDING_BINDING_HOST",
            "http://localhost:11434",
        )
        args.embedding_dim = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OLLAMA_DIMENSION", "EMBEDDING_DIM", 1024, int
        )
        args.embedding_binding_api_key = ""  # Ollama doesn't need API key
    elif embedding_provider == "openai":
        args.embedding_model = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OPENAI_MODEL",
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
        args.embedding_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OPENAI_API_KEY", "EMBEDDING_BINDING_API_KEY", ""
        )
        args.embedding_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OPENAI_BASE_URL",
            "EMBEDDING_BINDING_HOST",
            "https://api.openai.com/v1",
        )
        args.embedding_dim = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_OPENAI_DIMENSION", "EMBEDDING_DIM", 1536, int
        )
    elif embedding_provider == "jina":
        args.embedding_model = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_JINA_MODEL",
            "EMBEDDING_MODEL",
            "jina-embeddings-v2-base-en",
        )
        args.embedding_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_JINA_API_KEY", "EMBEDDING_BINDING_API_KEY", ""
        )
        args.embedding_binding_host = "https://api.jina.ai"
        args.embedding_dim = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_JINA_DIMENSION", "EMBEDDING_DIM", 768, int
        )
    else:
        # Fallback for unknown providers
        args.embedding_model = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_MODEL", "EMBEDDING_MODEL", "bge-m3:latest"
        )
        args.embedding_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_BASE_URL",
            "EMBEDDING_BINDING_HOST",
            get_default_host(embedding_provider),
        )
        args.embedding_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_API_KEY", "EMBEDDING_BINDING_API_KEY", ""
        )
        args.embedding_dim = get_env_value_with_fallback(
            "LIGHTRAG_EMBEDDING_DIMENSION", "EMBEDDING_DIM", 1024, int
        )

    args.embedding_send_dim = get_env_value_with_fallback(
        "LIGHTRAG_EMBEDDING_SEND_DIM", "EMBEDDING_SEND_DIM", False, bool
    )

    # Inject chunk configuration
    args.chunk_size = get_env_value_with_fallback(
        "LIGHTRAG_CHUNKING_CHUNK_SIZE", "CHUNK_SIZE", 1200, int
    )
    args.chunk_overlap_size = get_env_value_with_fallback(
        "LIGHTRAG_CHUNKING_CHUNK_OVERLAP_SIZE", "CHUNK_OVERLAP_SIZE", 100, int
    )

    # Inject LLM cache configuration
    args.enable_llm_cache_for_extract = get_env_value_with_fallback(
        "LIGHTRAG_CACHE_ENABLE_LLM_CACHE_FOR_EXTRACT",
        "ENABLE_LLM_CACHE_FOR_EXTRACT",
        True,
        bool,
    )
    args.enable_llm_cache = get_env_value_with_fallback(
        "LIGHTRAG_CACHE_ENABLE_LLM_CACHE", "ENABLE_LLM_CACHE", True, bool
    )

    # Set document_loading_engine from --docling flag
    if args.docling:
        args.document_loading_engine = "DOCLING"
    else:
        args.document_loading_engine = get_env_value(
            "DOCUMENT_LOADING_ENGINE", "DEFAULT"
        )

    # PDF decryption password
    args.pdf_decrypt_password = get_env_value("PDF_DECRYPT_PASSWORD", None)

    # Add environment variables that were previously read directly
    args.cors_origins = get_env_value("CORS_ORIGINS", "*")
    args.summary_language = get_env_value_with_fallback(
        "LIGHTRAG_SUMMARY_LANGUAGE",
        "SUMMARY_LANGUAGE",
        DEFAULT_SUMMARY_LANGUAGE,
    )
    args.entity_types = get_env_value("ENTITY_TYPES", DEFAULT_ENTITY_TYPES, list)
    args.whitelist_paths = get_env_value("WHITELIST_PATHS", "/health,/api/*")

    # Trilingual entity extractor configuration
    args.use_trilingual_extractor = get_env_value_with_fallback(
        "LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL",
        "USE_TRILINGUAL_EXTRACTOR",
        False,
        bool,
    )
    args.trilingual_auto_detect_language = get_env_value_with_fallback(
        "LIGHTRAG_ENTITY_EXTRACTION_AUTO_DETECT_LANGUAGE",
        "TRILINGUAL_AUTO_DETECT_LANGUAGE",
        True,
        bool,
    )
    args.trilingual_fallback_to_llm = get_env_value_with_fallback(
        "LIGHTRAG_ENTITY_EXTRACTION_FALLBACK_TO_LLM",
        "TRILINGUAL_FALLBACK_TO_LLM",
        True,
        bool,
    )
    args.trilingual_default_language = get_env_value_with_fallback(
        "LIGHTRAG_ENTITY_EXTRACTION_DEFAULT_LANGUAGE",
        "TRILINGUAL_DEFAULT_LANGUAGE",
        "en",
    )
    args.trilingual_chinese_model = get_env_value(
        "TRILINGUAL_CHINESE_MODEL", "CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH"
    )
    args.trilingual_english_model = get_env_value(
        "TRILINGUAL_ENGLISH_MODEL", "en_core_web_trf"
    )
    args.trilingual_swedish_model = get_env_value(
        "TRILINGUAL_SWEDISH_MODEL", "sv_core_news_lg"
    )

    # For JWT Auth
    args.auth_accounts = get_env_value("AUTH_ACCOUNTS", "")
    args.token_secret = get_env_value("TOKEN_SECRET", "lightrag-jwt-default-secret")
    args.token_expire_hours = get_env_value("TOKEN_EXPIRE_HOURS", 48, int)
    args.guest_token_expire_hours = get_env_value("GUEST_TOKEN_EXPIRE_HOURS", 24, int)
    args.jwt_algorithm = get_env_value("JWT_ALGORITHM", "HS256")

    # Load provider-specific Rerank configuration
    rerank_provider = args.rerank_binding
    if rerank_provider == "cohere":
        args.rerank_model = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_COHERE_MODEL", "RERANK_MODEL", "rerank-english-v2.0"
        )
        args.rerank_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_COHERE_API_KEY",
            "RERANK_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.rerank_binding_host = "https://api.cohere.ai"
    elif rerank_provider == "jina":
        args.rerank_model = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_JINA_MODEL", "RERANK_MODEL", "jina-reranker-v1-base-en"
        )
        args.rerank_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_JINA_API_KEY",
            "RERANK_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.rerank_binding_host = "https://api.jina.ai"
    elif rerank_provider == "aliyun":
        args.rerank_model = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_ALIYUN_MODEL", "RERANK_MODEL", "gte-rerank"
        )
        args.rerank_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_ALIYUN_API_KEY",
            "RERANK_BINDING_API_KEY",
            None,
            special_none=True,
        )
        args.rerank_binding_host = "https://dashscope.aliyuncs.com"
    else:  # null or unknown provider
        args.rerank_model = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_MODEL", "RERANK_MODEL", None, special_none=True
        )
        args.rerank_binding_host = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_BASE_URL", "RERANK_BINDING_HOST", None, special_none=True
        )
        args.rerank_binding_api_key = get_env_value_with_fallback(
            "LIGHTRAG_RERANK_API_KEY", "RERANK_BINDING_API_KEY", None, special_none=True
        )

    # Min rerank score configuration
    args.min_rerank_score = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_MIN_RERANK_SCORE",
        "MIN_RERANK_SCORE",
        DEFAULT_MIN_RERANK_SCORE,
        float,
    )

    # Query configuration
    args.history_turns = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_HISTORY_TURNS", "HISTORY_TURNS", DEFAULT_HISTORY_TURNS, int
    )
    args.top_k = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_TOP_K", "TOP_K", DEFAULT_TOP_K, int
    )
    args.chunk_top_k = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_CHUNK_TOP_K", "CHUNK_TOP_K", DEFAULT_CHUNK_TOP_K, int
    )
    args.max_entity_tokens = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_MAX_ENTITY_TOKENS",
        "MAX_ENTITY_TOKENS",
        DEFAULT_MAX_ENTITY_TOKENS,
        int,
    )
    args.max_relation_tokens = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_MAX_RELATION_TOKENS",
        "MAX_RELATION_TOKENS",
        DEFAULT_MAX_RELATION_TOKENS,
        int,
    )
    args.max_total_tokens = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_MAX_TOTAL_TOKENS",
        "MAX_TOTAL_TOKENS",
        DEFAULT_MAX_TOTAL_TOKENS,
        int,
    )
    args.cosine_threshold = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_COSINE_THRESHOLD",
        "COSINE_THRESHOLD",
        DEFAULT_COSINE_THRESHOLD,
        float,
    )
    args.related_chunk_number = get_env_value_with_fallback(
        "LIGHTRAG_QUERY_RELATED_CHUNK_NUMBER",
        "RELATED_CHUNK_NUMBER",
        DEFAULT_RELATED_CHUNK_NUMBER,
        int,
    )

    # Add missing environment variables for health endpoint
    args.force_llm_summary_on_merge = get_env_value_with_fallback(
        "LIGHTRAG_PERFORMANCE_FORCE_LLM_SUMMARY_ON_MERGE",
        "FORCE_LLM_SUMMARY_ON_MERGE",
        DEFAULT_FORCE_LLM_SUMMARY_ON_MERGE,
        int,
    )
    args.embedding_func_max_async = get_env_value_with_fallback(
        "LIGHTRAG_PERFORMANCE_EMBEDDING_FUNC_MAX_ASYNC",
        "EMBEDDING_FUNC_MAX_ASYNC",
        DEFAULT_EMBEDDING_FUNC_MAX_ASYNC,
        int,
    )
    args.embedding_batch_num = get_env_value_with_fallback(
        "LIGHTRAG_PERFORMANCE_EMBEDDING_BATCH_NUM",
        "EMBEDDING_BATCH_NUM",
        DEFAULT_EMBEDDING_BATCH_NUM,
        int,
    )

    # Embedding token limit configuration
    args.embedding_token_limit = get_env_value(
        "EMBEDDING_TOKEN_LIMIT", None, int, special_none=True
    )

    ollama_server_infos.LIGHTRAG_NAME = args.simulated_model_name
    ollama_server_infos.LIGHTRAG_TAG = args.simulated_model_tag

    return args


def update_uvicorn_mode_config():
    # If in uvicorn mode and workers > 1, force it to 1 and log warning
    if global_args.workers > 1:
        original_workers = global_args.workers
        global_args.workers = 1
        # Log warning directly here
        logging.warning(
            f">> Forcing workers=1 in uvicorn mode(Ignoring workers={original_workers})"
        )


# Global configuration with lazy initialization
_global_args = None
_initialized = False


def initialize_config(args=None, force=False):
    """Initialize global configuration

    This function allows explicit initialization of the configuration,
    which is useful for programmatic usage, testing, or embedding LightRAG
    in other applications.

    Args:
        args: Pre-parsed argparse.Namespace or None to parse from sys.argv
        force: Force re-initialization even if already initialized

    Returns:
        argparse.Namespace: The configured arguments

    Example:
        # Use parsed command line arguments (default)
        initialize_config()

        # Use custom configuration programmatically
        custom_args = argparse.Namespace(
            host='localhost',
            port=8080,
            working_dir='./custom_rag',
            # ... other config
        )
        initialize_config(custom_args)
    """
    global _global_args, _initialized

    if _initialized and not force:
        return _global_args

    _global_args = args if args is not None else parse_args()
    _initialized = True
    return _global_args


def get_config():
    """Get global configuration, auto-initializing if needed

    Returns:
        argparse.Namespace: The configured arguments
    """
    if not _initialized:
        initialize_config()
    return _global_args


class _GlobalArgsProxy:
    """Proxy object that auto-initializes configuration on first access

    This maintains backward compatibility with existing code while
    allowing programmatic control over initialization timing.
    """

    def __getattr__(self, name):
        if not _initialized:
            initialize_config()
        return getattr(_global_args, name)

    def __setattr__(self, name, value):
        if not _initialized:
            initialize_config()
        setattr(_global_args, name, value)

    def __repr__(self):
        if not _initialized:
            return "<GlobalArgsProxy: Not initialized>"
        return repr(_global_args)


# Create proxy instance for backward compatibility
# Existing code like `from config import global_args` continues to work
# The proxy will auto-initialize on first attribute access
global_args = _GlobalArgsProxy()
