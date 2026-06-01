# Open-Source Model Testing — Setup & Execution Guide

## Overview
This document describes how to test open-source LLMs (e.g., LLaMA, Mistral, Falcon) as a baseline comparison to the paid models (OpenAI, Anthropic, Google).

## Supported Open-Source Models

Via LiteLLM proxy, the following open-source models are accessible:

### 1. **Ollama (Local)**
- **Model:** `ollama/llama2`, `ollama/llama2-uncensored`, `ollama/mistral`
- **Setup:** 
  - Download & install [Ollama](https://ollama.ai)
  - Run: `ollama serve`
  - Models auto-downloaded on first use
- **Advantages:** Runs locally, no API key needed, faster iteration
- **Disadvantages:** Requires GPU/CPU resources, slower than API models

### 2. **Hugging Face (via Replicate API)**
- **Model:** `replicate/meta/llama-2-7b-chat` (and others)
- **Setup:** 
  - Create Replicate account: https://replicate.com
  - Generate API token
  - Set: `export REPLICATE_API_TOKEN=<your_token>`
- **Advantages:** Easy setup, no local GPU needed
- **Disadvantages:** Requires API token (paid after free tier)

### 3. **Hugging Face (via together.ai)**
- **Model:** `together_ai/meta-llama/Llama-2-7b-chat-hf` (and others)
- **Setup:**
  - Create together.ai account: https://www.together.ai
  - Generate API token
  - Set: `export TOGETHER_API_KEY=<your_token>`
- **Advantages:** Fast inference, competitive pricing
- **Disadvantages:** Requires API token (paid)

### 4. **Groq (Fast Inference)**
- **Model:** `groq/llama2-70b-4096`
- **Setup:**
  - Create Groq account: https://console.groq.com
  - Generate API key
  - Set: `export GROQ_API_KEY=<your_api_key>`
- **Advantages:** Extremely fast inference, free tier available
- **Disadvantages:** Limited model selection

---

## Setup for PAHS Study

### Option 1: Ollama (Recommended for local testing)

#### Installation
```bash
# macOS (using Homebrew)
brew install ollama

# Linux / Manual download
# Visit: https://ollama.ai/download
```

#### Start Ollama Server
```bash
# Start in background
ollama serve &

# Or in a separate terminal
ollama serve
```

#### Download Model
```bash
# LLaMA 2 (7B model, ~4 GB)
ollama pull llama2

# Mistral (7B, faster)
ollama pull mistral

# Verify
ollama list
```

#### Test Ollama Connection
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Why is the sky blue?"
}'
```

---

### Option 2: Groq (Fastest, free tier)

#### Setup
```bash
# 1. Create account & get API key: https://console.groq.com
# 2. Set environment variable
export GROQ_API_KEY=your_key_here

# 3. Test
python -c "from litellm import completion; r = completion(model='groq/llama2-70b-4096', messages=[{'role': 'user', 'content': 'Hi'}]); print(r.choices[0].message.content)"
```

---

## Running Open-Source Model Tests

### Command Syntax

```bash
# Set the open-source model to test
export PAHS_OPENSOURCE_MODEL=ollama/llama2
# OR
export PAHS_OPENSOURCE_MODEL=groq/llama2-70b-4096

# Run the pilot
python pilot.py --provider opensource --vignettes-count 300

# Alternative: test just this model (independent run)
python pilot.py --model ollama/llama2 --vignettes-count 300 --independent-model-runs
```

### Example Workflows

#### 1. Pilot Test (Small batch, local Ollama)
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run 2-vignette pilot
export PAHS_OPENSOURCE_MODEL=ollama/llama2
python pilot.py --provider opensource  # Default: 2 vignettes

# Inspect pilot output
cat 04_results/raw_json/PILOT_2026_RESULTS_ollama_llama2.json
```

#### 2. Full Study (Groq, faster)
```bash
export GROQ_API_KEY=gsk_your_key_here
export PAHS_OPENSOURCE_MODEL=groq/llama2-70b-4096

python pilot.py --provider opensource --vignettes-count 300

# Check results
ls -lh 04_results/raw_json/PAHS_STUDY_RESULTS_2026_groq*.json
```

#### 3. Multi-Model Sequential Runs
```bash
# Run all 4 models independently (one per file)
python pilot.py --independent-model-runs --vignettes-count 300

# Results saved as:
# - PILOT_2026_RESULTS_openai_gpt-5.4-mini.json
# - PILOT_2026_RESULTS_anthropic_claude-haiku-4-5.json
# - PILOT_2026_RESULTS_gemini_gemini-3.1-flash-lite.json
# - PILOT_2026_RESULTS_ollama_llama2.json (if PAHS_OPENSOURCE_MODEL set)
```

---

## Expected Runtime & Cost

### Ollama (Local)
- **Runtime:** ~10–30 sec per vignette (GPU-dependent)
- **Cost:** $0 (runs locally)
- **Total (300 × 3 conditions × 2 lengths):** ~6–18 hours
- **Recommendation:** Run overnight or in background

### Groq
- **Runtime:** ~1–3 sec per vignette (API latency)
- **Cost:** Free tier: 100 calls/min (~$0.50 after); pay-as-you-go
- **Total (300 × 3 × 2 = 1,800 trials):** <2 hours, ~$1–5
- **Recommendation:** Fast option for full study

### Replicate
- **Runtime:** ~5–15 sec per vignette
- **Cost:** Free tier 100 calls/month; $0.001–0.01 per prediction
- **Total cost estimate:** ~$5–20

---

## Analysis: Comparing Open-Source to Paid Models

After collecting open-source results, run the pooled analysis:

```bash
python 03_src/evaluation/pool_hallucination_analysis.py
```

This will automatically include the open-source model in:
- `04_results/analysis_ready/pooled/hallucination_summary_by_model.csv`
- `04_results/analysis_ready/pooled/hallucination_by_model_condition.csv`
- Updated dashboard with 4-model leaderboard

### Analysis Questions
1. **Does open-source LLM hallucinate more than paid models?**
2. **Does the open-source model benefit from SAFETY_INSTRUCTION condition?**
3. **Are hallucinations consistent across vignette lengths?**
4. **Can smaller open-source models match larger paid models' performance?**

---

## Troubleshooting

### Error: "Model not found"
```
litellm.exceptions.AuthenticationError: Failed to authenticate
```
**Solution:** Ensure API key is set correctly
```bash
export GROQ_API_KEY=...
# Verify
env | grep GROQ
```

### Error: "Connection refused (Ollama)"
```
ConnectionError: Failed to connect to localhost:11434
```
**Solution:** Start Ollama server
```bash
ollama serve &
# Or in new terminal: ollama serve
```

### Error: "Model too slow"
- **Ollama:** Use smaller model or GPU acceleration
  ```bash
  ollama pull mistral  # Faster than llama2
  ```
- **Groq:** Already fastest; consider larger batch to amortize latency

### Error: "Out of memory"
- **Ollama:** Reduce model size (use `mistral` or `neural-chat` instead of `llama2`)
- **API-based:** Not an issue; server-side

---

## Recommended Next Steps

### Phase 1: Validate Setup (1 day)
1. Choose provider (suggest: **Groq** for speed OR **Ollama** for local control)
2. Set up account/keys/installation
3. Run 2-vignette pilot: `python pilot.py --provider opensource`

### Phase 2: Full Study (2–5 days)
1. Run full 300-vignette study: `python pilot.py --provider opensource --vignettes-count 300`
2. Monitor progress and logs
3. Save results to `04_results/`

### Phase 3: Analysis (1 day)
1. Run pooled analysis: `python 03_src/evaluation/pool_hallucination_analysis.py`
2. Generate comparison tables (open-source vs. paid)
3. Update proposal alignment doc with 4-model results

### Phase 4: Documentation (1 day)
1. Write results section comparing hallucination rates
2. Update methods section to document open-source model choice
3. Prepare publication-ready figures

---

## Final Note

**Open-source baseline is critical** for:
- Establishing whether hallucinations are inherent to LLMs or provider-specific
- Demonstrating that safety improvements are not limited to commercial tools
- Reducing study cost (if using local Ollama or free-tier Groq)
- Validating reproducibility (open-source models are downloadable)

**Estimated total study time:** 3–7 days (depending on provider & compute resources)

