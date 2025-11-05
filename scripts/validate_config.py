#!/usr/bin/env python
"""
Configuration validation script for LightRAG.

This script validates the .env configuration file and reports any issues.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import re


class ConfigValidator:
    """Validates LightRAG configuration."""

    # Required environment variables
    REQUIRED_VARS = [
        "LLM_BINDING",
        "LLM_MODEL",
        "EMBEDDING_BINDING",
        "EMBEDDING_MODEL",
        "EMBEDDING_DIM",
    ]

    # Optional but recommended variables
    RECOMMENDED_VARS = [
        "WORKING_DIR",
        "INPUT_DIR",
        "MAX_ASYNC",
        "LOG_LEVEL",
    ]

    # Variables that need API keys
    API_KEY_VARS = {
        "openai": ["LLM_BINDING_API_KEY"],
        "azure_openai": ["LLM_BINDING_API_KEY"],
        "jina": ["EMBEDDING_BINDING_API_KEY"],
    }

    # Valid values for specific variables
    VALID_VALUES = {
        "LLM_BINDING": ["openai", "ollama", "azure_openai", "aws_bedrock", "lollms"],
        "EMBEDDING_BINDING": [
            "openai",
            "ollama",
            "azure_openai",
            "aws_bedrock",
            "jina",
            "lollms",
        ],
        "LOG_LEVEL": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    }

    def __init__(self, env_file: str = ".env"):
        """Initialize the validator.

        Args:
            env_file: Path to the .env file to validate
        """
        self.env_file = Path(env_file)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate(self) -> bool:
        """Run all validation checks.

        Returns:
            True if validation passes (no errors), False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        self.info.clear()

        # Check if .env file exists
        if not self.env_file.exists():
            self.errors.append(f"Configuration file not found: {self.env_file}")
            return False

        # Load environment variables from .env
        self._load_env_file()

        # Run validation checks
        self._check_required_vars()
        self._check_recommended_vars()
        self._check_valid_values()
        self._check_api_keys()
        self._check_storage_config()
        self._check_numeric_values()
        self._check_path_variables()

        return len(self.errors) == 0

    def _load_env_file(self):
        """Load environment variables from .env file."""
        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse key=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

            self.info.append(f"Loaded configuration from {self.env_file}")
        except Exception as e:
            self.errors.append(f"Error reading .env file: {e}")

    def _check_required_vars(self):
        """Check that all required variables are set."""
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                self.errors.append(f"Required variable not set: {var}")
            elif value == "your_api_key" or value == "your_password":
                self.errors.append(
                    f"Variable {var} has placeholder value, please set actual value"
                )

    def _check_recommended_vars(self):
        """Check recommended variables."""
        for var in self.RECOMMENDED_VARS:
            if not os.getenv(var):
                self.warnings.append(
                    f"Recommended variable not set: {var} (using default)"
                )

    def _check_valid_values(self):
        """Check that variables have valid values."""
        for var, valid_values in self.VALID_VALUES.items():
            value = os.getenv(var)
            if value and value not in valid_values:
                self.errors.append(
                    f"Invalid value for {var}: '{value}'. Valid values: {', '.join(valid_values)}"
                )

    def _check_api_keys(self):
        """Check that required API keys are set based on bindings."""
        llm_binding = os.getenv("LLM_BINDING")
        embedding_binding = os.getenv("EMBEDDING_BINDING")

        # Check LLM API key
        if llm_binding in self.API_KEY_VARS:
            for key_var in self.API_KEY_VARS[llm_binding]:
                value = os.getenv(key_var)
                if not value or value == "your_api_key":
                    self.errors.append(
                        f"API key required for {llm_binding}: {key_var} not set or has placeholder value"
                    )

        # Check Embedding API key
        if embedding_binding in self.API_KEY_VARS:
            for key_var in self.API_KEY_VARS[embedding_binding]:
                value = os.getenv(key_var)
                if not value or value == "your_api_key":
                    self.errors.append(
                        f"API key required for {embedding_binding}: {key_var} not set or has placeholder value"
                    )

    def _check_storage_config(self):
        """Check storage configuration."""
        storage_types = [
            "LIGHTRAG_KV_STORAGE",
            "LIGHTRAG_VECTOR_STORAGE",
            "LIGHTRAG_GRAPH_STORAGE",
            "LIGHTRAG_DOC_STATUS_STORAGE",
        ]

        for storage_type in storage_types:
            value = os.getenv(storage_type)
            if value:
                self.info.append(f"{storage_type}: {value}")

                # Check for required connection variables
                if "Postgres" in value or "PG" in value:
                    self._check_postgres_config()
                elif "Neo4J" in value:
                    self._check_neo4j_config()
                elif "Mongo" in value:
                    self._check_mongo_config()
                elif "Redis" in value:
                    self._check_redis_config()

    def _check_postgres_config(self):
        """Check PostgreSQL configuration."""
        required = [
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DATABASE",
        ]
        for var in required:
            if not os.getenv(var):
                self.warnings.append(
                    f"PostgreSQL storage selected but {var} not set"
                )

    def _check_neo4j_config(self):
        """Check Neo4j configuration."""
        required = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
        for var in required:
            if not os.getenv(var):
                self.warnings.append(f"Neo4j storage selected but {var} not set")

    def _check_mongo_config(self):
        """Check MongoDB configuration."""
        if not os.getenv("MONGO_URI"):
            self.warnings.append("MongoDB storage selected but MONGO_URI not set")

    def _check_redis_config(self):
        """Check Redis configuration."""
        if not os.getenv("REDIS_URI"):
            self.warnings.append("Redis storage selected but REDIS_URI not set")

    def _check_numeric_values(self):
        """Check that numeric values are valid."""
        numeric_vars = {
            "PORT": (1, 65535),
            "MAX_ASYNC": (1, 100),
            "EMBEDDING_DIM": (1, 10000),
            "CHUNK_SIZE": (100, 10000),
            "TOP_K": (1, 1000),
        }

        for var, (min_val, max_val) in numeric_vars.items():
            value = os.getenv(var)
            if value:
                try:
                    num_value = int(value)
                    if num_value < min_val or num_value > max_val:
                        self.warnings.append(
                            f"{var}={num_value} is outside recommended range [{min_val}, {max_val}]"
                        )
                except ValueError:
                    self.errors.append(f"{var} should be a number, got: {value}")

    def _check_path_variables(self):
        """Check path variables."""
        path_vars = ["WORKING_DIR", "INPUT_DIR", "LOG_DIR"]

        for var in path_vars:
            value = os.getenv(var)
            if value:
                path = Path(value)
                # Check if it's an absolute path (recommended)
                if not path.is_absolute():
                    self.warnings.append(
                        f"{var} is a relative path: {value} (absolute path recommended)"
                    )

    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("LightRAG Configuration Validation Report")
        print("=" * 70 + "\n")

        # Print info messages
        if self.info:
            print("ℹ️  Information:")
            for msg in self.info:
                print(f"   {msg}")
            print()

        # Print warnings
        if self.warnings:
            print("⚠️  Warnings:")
            for msg in self.warnings:
                print(f"   {msg}")
            print()

        # Print errors
        if self.errors:
            print("❌ Errors:")
            for msg in self.errors:
                print(f"   {msg}")
            print()

        # Summary
        print("-" * 70)
        if not self.errors:
            print("✅ Configuration validation passed!")
            if self.warnings:
                print(f"   ({len(self.warnings)} warnings - please review)")
        else:
            print(f"❌ Configuration validation failed with {len(self.errors)} errors")
            print("   Please fix the errors above before starting LightRAG")

        print("=" * 70 + "\n")

        return len(self.errors) == 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate LightRAG configuration file"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    args = parser.parse_args()

    validator = ConfigValidator(args.env_file)
    is_valid = validator.validate()
    validator.print_report()

    # Exit with appropriate code
    if not is_valid:
        sys.exit(1)
    elif args.strict and validator.warnings:
        print("❌ Strict mode: Warnings treated as errors")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
