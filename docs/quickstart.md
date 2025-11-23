# LightRAG Quickstart Guide

Get LightRAG running in 5 minutes with this step-by-step guide.

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** - Check with `python --version`
- **uv package manager** - Install: `pip install uv`
- **Ollama** (recommended for local setup) - Download from [ollama.ai](https://ollama.ai)
  - Or **OpenAI API key** for cloud LLM

## Choose Your Mode

LightRAG supports two entity extraction modes:

| Feature | Fast Mode (Trilingual) | Standard Mode (LLM-only) |
|---------|------------------------|--------------------------|
| **Speed** | 8-15x faster | Baseline |
| **Entity names** | Original text (zh/en/sv) | May translate to English |
| **Extra dependencies** | ~500MB models | None |
| **Supported languages** | Chinese, English, Swedish | All languages |
| **Best for** | Production, bulk processing | Testing, multi-language |

**Recommendation**: Use **Fast Mode** for production Chinese/English/Swedish documents.

---

## Path A: Fast Mode (Recommended)

### Step 1: Install dependencies

```bash
cd /path/to/lightrag
uv sync --extra fast
```

This installs all required components:
- **FastAPI server** - Web API for document processing
- **LLM support** - Ollama/OpenAI/Azure/etc for entity extraction
- **HanLP** - Chinese entity extraction (F1 95%)
- **spaCy** - English/Swedish entity extraction (F1 90% & 85%)

**Note**: You can switch between LLM and HanLP/spaCy extraction via config.

### Step 2: Generate configuration

```bash
./scripts/setup.sh
```

This generates `config/local.yaml` and `.env` files.

**Optional**: Enable fast extraction (8-15x faster) by editing `config/local.yaml`:

```yaml
lightrag:
  entity_extraction:
    use_trilingual: true          # Enable HanLP/spaCy (default: false, uses LLM)
    auto_detect_language: true    # Auto-detect document language
    fallback_to_llm: true         # Use LLM for unsupported languages
    default_language: zh          # Default language: zh/en/sv
```

Then re-run `./scripts/setup.sh` to update `.env`.

### Step 3: Download language models (if using fast extraction)

**Only needed if you set `use_trilingual: true` in Step 2.**

```bash
# Option 1: Use the installation script (recommended)
./scripts/install_fast_models.sh

# Option 2: Manual installation
uv run python -m spacy download en_core_web_trf  # English
uv run python -m spacy download sv_core_news_lg   # Swedish (optional)
```

**Note**: HanLP Chinese model (~500MB) downloads automatically on first use.

### Step 4: Configure LLM and Embedding

Edit `config/local.yaml` to set your LLM provider:

**Option 1: Ollama (Local, Recommended)**

```yaml
lightrag:
  llm:
    provider: ollama
    ollama:
      model: qwen3:4b-instruct
      host: http://localhost:11434
      max_tokens: 4096
      num_ctx: 32768

  embedding:
    provider: ollama
    ollama:
      model: jeffh/intfloat-multilingual-e5-large:f16
      host: http://localhost:11434
      dimension: 1024
```

**Option 2: OpenAI (Cloud)**

```yaml
lightrag:
  llm:
    provider: openai
    openai:
      model: gpt-4o-mini
      base_url: ""                # Leave empty for OpenAI
      max_tokens: 4096

  embedding:
    provider: openai
    openai:
      model: text-embedding-3-small
      dimension: 1536
```

After editing, run:

```bash
./scripts/setup.sh
```

If using OpenAI, you'll be prompted to enter your API key.

### Step 6: Start the server

```bash
uv run lightrag-server
```

**Verify trilingual is active** - Look for these log messages:

```
INFO: Initializing trilingual extractor (lazy loading enabled)
INFO: HanLP model loaded: CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH
```

Access the WebUI at: **http://localhost:9621**

---

## Path B: Standard Mode (Minimal Dependencies)

Use this mode for quick testing or unsupported languages.

### Step 1: Install dependencies

```bash
cd /path/to/lightrag
uv sync --extra api --extra offline-llm
```

This installs minimal components:
- **FastAPI server** (`api` extra)
- **Ollama/OpenAI SDK** (`offline-llm` extra)
- **No trilingual NER models** (faster install, smaller footprint)

### Step 2: Disable trilingual extraction

Edit `config/local.yaml`:

```yaml
lightrag:
  entity_extraction:
    use_trilingual: false         # Use LLM-only extraction
```

### Step 3: Generate environment variables

```bash
./scripts/setup.sh
```

### Step 4: Configure LLM and Embedding

Follow the same LLM configuration as Fast Mode (Step 5 above), then run:

```bash
./scripts/setup.sh
```

### Step 5: Start the server

```bash
uv run lightrag-server
```

**Verify LLM-only mode is active** - Look for these log messages:

```
INFO:  == LLM cache == saving: default:extract:...
WARNING: chunk-xxx: LLM output format error; found 5/4 feilds on ENTITY...
```

Access the WebUI at: **http://localhost:9621**

---

## Verify It Works

### 1. Upload a test document

**Via WebUI**: Navigate to http://localhost:9621 and upload a file

**Via API**:
```bash
curl -X POST http://localhost:9621/documents/upload \
  -F "file=@test.txt"
```

### 2. Check entity extraction mode

**Fast Mode** - Entities should be in original language:
```
萧瑟、雪落客栈、金棺、红露镇 (Chinese original)
```

**Standard Mode** - Entities may be translated:
```
Xiao Se, The Inn at Xue Luo, The Golden Coffin, Hong Lu Town (English translation)
```

### 3. Query your documents

**Via WebUI**: Use the query interface

**Via API**:
```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "mode": "hybrid"
  }'
```

Query modes:
- `naive`: Vector search only
- `local`: Context-focused
- `global`: Knowledge graph-focused
- `hybrid`: Combined local + global (recommended)

---

## Configuration Workflow

⚠️ **IMPORTANT**: Always follow this workflow when changing configuration:

```
1. Edit config/local.yaml
         ↓
2. Run ./scripts/setup.sh
         ↓
3. Restart lightrag-server
```

**DO NOT** edit `.env` directly - it will be overwritten by `setup.sh`.

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'hanlp'`

**Cause**: Fast mode enabled but dependencies not installed

**Fix**:
```bash
uv sync --extra fast
```

---

### Error: `No module named 'spacy'` or `Can't find model 'en_core_web_trf'`

**Cause**: spaCy models not downloaded

**Fix**:
```bash
uv run python -m spacy download en_core_web_trf
uv run python -m spacy download sv_core_news_lg  # If using Swedish
```

---

### Issue: Entities are translated to English (Chinese documents)

**Cause**: Trilingual not enabled or failed to initialize

**Check configuration**:
```bash
grep -A 3 "entity_extraction:" config/local.yaml
```

Should show:
```yaml
entity_extraction:
  use_trilingual: true
```

**Check logs for initialization errors**:
```bash
# Look for trilingual initialization message
grep "trilingual" lightrag.log
```

---

### Issue: Configuration changes not taking effect

**Cause**: Forgot to run `setup.sh` after editing `local.yaml`

**Fix**:
```bash
./scripts/setup.sh
# Restart server
uv run lightrag-server
```

---

### Error: Port 9621 already in use

**Fix**: Change port in `config/local.yaml`:

```yaml
lightrag:
  api:
    port: 9622
```

Then run:
```bash
./scripts/setup.sh
uv run lightrag-server
```

---

### Error: `model "xxx" not found` (Ollama)

**Cause**: Ollama model not pulled

**Fix**:
```bash
# Pull LLM model
ollama pull qwen3:4b-instruct

# Pull embedding model
ollama pull jeffh/intfloat-multilingual-e5-large:f16
```

**Verify models**:
```bash
ollama list
```

---

### Error: Ollama connection refused

**Cause**: Ollama service not running

**Fix**:
```bash
# Start Ollama service (macOS/Linux)
ollama serve

# Or on macOS, check if Ollama app is running
```

---

### Issue: Slow performance in Fast Mode

**Check 1**: Verify trilingual is actually being used

```bash
# Look for HanLP initialization in logs
grep "HanLP" lightrag.log
```

**Check 2**: GPU acceleration (optional)

Edit `config/local.yaml`:
```yaml
trilingual:
  performance:
    enable_gpu: true              # If CUDA available
    num_threads: 8                # Increase for more CPU cores
```

Run `./scripts/setup.sh` and restart.

---

### Error: Frontend not built

**Symptom**: Log shows "ERROR: Frontend Not Built"

**Fix**:
```bash
cd lightrag_webui

# Install Bun (if not installed)
curl -fsSL https://bun.sh/install | bash

# Build frontend
bun install --frozen-lockfile
bun run build

# Return to root
cd ..

# Restart server
uv run lightrag-server
```

---

## Advanced: Custom Configuration

### Using multiple workspaces (data isolation)

Run multiple instances with separate data:

```bash
# Instance 1
lightrag-server --workspace project-a --port 9621

# Instance 2
lightrag-server --workspace project-b --port 9622
```

Each workspace has its own storage directory.

### Switching embedding models

⚠️ **WARNING**: Changing embedding models requires clearing data:

```bash
# Stop server
# Keep LLM cache (optional)
cp rag_storage/kv_store_llm_response_cache.json ./backup.json

# Clear vector storage
rm -rf rag_storage/*

# Restore LLM cache (optional)
mv ./backup.json rag_storage/kv_store_llm_response_cache.json

# Update config/local.yaml with new embedding model
# Run setup.sh
./scripts/setup.sh

# Restart server
uv run lightrag-server
```

### Performance tuning

Edit `config/local.yaml`:

```yaml
lightrag:
  performance:
    max_async: 8                  # More concurrent LLM requests (default: 4)
    max_parallel_insert: 4        # More parallel document processing (default: 2)
```

Run `./scripts/setup.sh` and restart.

**Note**: Higher values = faster processing but more memory/CPU usage.

---

## Next Steps

- **📖 Full Documentation**: [README.md](../README.md)
- **🔌 API Reference**: [API Documentation](../lightrag/api/README.md)
- **⚙️ Configuration Schema**: [config.schema.yaml](../config/config.schema.yaml)
- **🐳 Docker Deployment**: [DockerDeployment.md](./DockerDeployment.md)
- **🔒 Offline Deployment**: [OfflineDeployment.md](./OfflineDeployment.md)
- **📊 Visualization**: [Graph Visualizer](../lightrag/tools/lightrag_visualizer/README.md)

---

## Summary: Quick Command Reference

### Fast Mode Setup
```bash
uv sync --extra offline
# Edit config/local.yaml: use_trilingual: true
./scripts/setup.sh
uv run python -m spacy download en_core_web_trf
uv run lightrag-server
```

### Standard Mode Setup
```bash
uv sync --extra api --extra offline-llm
# Edit config/local.yaml: use_trilingual: false
./scripts/setup.sh
uv run lightrag-server
```

### Configuration Update
```bash
# Edit config/local.yaml
./scripts/setup.sh
# Restart server
```

### Test Ollama Models
```bash
ollama list
ollama pull qwen3:4b-instruct
ollama pull jeffh/intfloat-multilingual-e5-large:f16
```

---

**Need help?** Check the [full documentation](../README.md) or open an issue on GitHub.
