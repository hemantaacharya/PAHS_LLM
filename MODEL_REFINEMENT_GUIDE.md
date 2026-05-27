# Model Refinement Guide — Upgrading to Higher-Performance Variants

## Current Low-Cost Baseline

You're currently testing with:

| Provider | Current Model | Tier | Speed | Cost (per M tokens) | Use Case |
|----------|--------------|------|-------|-------------------|----------|
| **OpenAI** | `openai/gpt-5.4-mini` | Budget | Fast | $0.15 in / $0.60 out | Quick, basic responses |
| **Anthropic** | `anthropic/claude-haiku-4-5` | Budget | Fast | $0.80 in / $2.40 out | Fast, economical |
| **Google** | `gemini/gemini-3.1-flash-lite` | Budget | Fast | $0.075 in / $0.30 out | Cheapest, lightweight |

---

## Available Higher-Performance Variants

### 1. OpenAI Upgrades

#### Option A: `openai/gpt-5.4` (Standard Performance)
- **Performance:** +40% more accurate reasoning vs. mini
- **Speed:** Moderate (2–3x slower than mini)
- **Cost:** ~$0.50 in / $2.00 out per M tokens (~3x mini cost)
- **Best for:** Better medical reasoning, hallucination detection
- **Recommendation:** ✅ **Worth testing** for medical sensitivity

#### Option B: `openai/gpt-5-turbo` (High Performance, Older)
- **Performance:** Excellent (legacy model, still strong)
- **Speed:** Fast
- **Cost:** ~$0.50 in / $1.50 out (~2–3x mini)
- **Note:** Being phased out; use gpt-5.4 instead

#### Option C: `openai/gpt-5` (Latest, Reasoning)
- **Performance:** Best in class (~50% better vs. gpt-5.4)
- **Speed:** Slowest (deep reasoning)
- **Cost:** ~$15 per M tokens (~100x mini) + usage caps
- **Caveats:** Expensive, overkill for this study, reasoning takes 10–60 sec per call
- **Not recommended** unless budget unlimited

---

### 2. Anthropic Upgrades

#### Option A: `anthropic/claude-3-sonnet` (Balanced)
- **Performance:** 2–3x better than Haiku
- **Speed:** 2x slower
- **Cost:** $3 in / $15 out per M tokens (~4x Haiku)
- **Best for:** Better hallucination resistance, nuanced reasoning
- **Recommendation:** ✅ **Strongly recommended** (best value upgrade)

#### Option B: `anthropic/claude-3-opus` (Premium)
- **Performance:** Best in class, excellent medical reasoning
- **Speed:** 3–4x slower
- **Cost:** $15 in / $75 out per M tokens (~10x Haiku)
- **Best for:** High-stakes clinical decisions
- **Caveat:** Expensive; consider only for full study re-run if needed

#### Option C: `anthropic/claude-3.5-sonnet` (Latest)
- **Performance:** Better than 3-sonnet, slight edge
- **Speed:** Similar to 3-sonnet
- **Cost:** Similar to 3-sonnet
- **Status:** New (May 2026); newer models may have different hallucination patterns
- **Note:** Good for comparing evolution of hallucination patterns

---

### 3. Google Gemini Upgrades

#### Option A: `google/gemini-2.0-flash` (Standard Performance)
- **Performance:** +30% accuracy vs. Flash Lite
- **Speed:** Similar to Lite (still fast)
- **Cost:** ~$0.10 in / $0.40 out (~1.3x Lite)
- **Best for:** Balanced cost/performance
- **Recommendation:** ✅ **Good upgrade path**

#### Option B: `google/gemini-2.0-pro` (Premium)
- **Performance:** 2x better reasoning than Flash
- **Speed:** Moderate (5–10x slower than Flash)
- **Cost:** ~$1.50 in / $6.00 out (~20x Lite)
- **Best for:** Complex clinical reasoning
- **Caveat:** Expensive; may need sampling strategy

#### Option C: `google/gemini-pro` (Older, Slower)
- **Not recommended** (being replaced by 2.0 series)

---

## Recommended Upgrade Strategy

### Fast Path (1–2 days, ~$100–200 additional cost)
Test one higher-end model per provider to establish "quality baseline":

```bash
# 1. Anthropic Sonnet (best value upgrade)
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-sonnet
python pilot.py --provider anthropic --vignettes-count 293

# 2. OpenAI Standard (solid performance)
export PAHS_OPENAI_MODEL=openai/gpt-5.4
python pilot.py --provider openai --vignettes-count 293

# 3. Google Flash (incremental improvement)
export PAHS_GEMINI_MODEL=google/gemini-2.0-flash
python pilot.py --provider gemini --vignettes-count 293
```

**Total cost estimate:**
- Claude Sonnet: ~$70 (293 vignettes × 3 conditions × 2 lengths × $0.009/1K tokens)
- GPT-5.4: ~$40
- Gemini Flash: ~$8
- **Total: ~$118** (vs. $30 for current low-cost variants)

**Expected results:** 3 additional JSON files with improved hallucination detection

---

### Comprehensive Path (3–5 days, ~$300–500)
Test all upgrades plus current baseline for complete comparison:

```bash
# Baseline (already done)
# - openai/gpt-5.4-mini ✅
# - anthropic/claude-haiku-4-5 ✅
# - gemini/gemini-3.1-flash-lite ✅

# Tier 1 Upgrades (next)
export PAHS_OPENAI_MODEL=openai/gpt-5.4 && python pilot.py --provider openai --vignettes-count 293
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-sonnet && python pilot.py --provider anthropic --vignettes-count 293
export PAHS_GEMINI_MODEL=google/gemini-2.0-flash && python pilot.py --provider gemini --vignettes-count 293

# Optional: Tier 2 Premium (if budget allows)
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-opus && python pilot.py --provider anthropic --vignettes-count 293 --output-file 04_results/raw_json/PAHS_STUDY_RESULTS_2026_anthropic_claude-opus.json
```

---

## How to Compare Low-Cost vs. High-Cost

### 1. Automatic Leaderboard Update
After each new model run, the pooled analysis automatically includes all models:

```bash
python 03_src/evaluation/pool_hallucination_analysis.py
```

This generates:
- Updated leaderboard (ranked by detection rate)
- New comparison CSV tables
- Side-by-side hallucination rate graphs

### 2. Manual Comparison Script
Create a quick comparison script:

```python
import json, glob
import pandas as pd

# Load all model results
results = {}
for path in glob.glob('04_results/raw_json/PAHS_STUDY_RESULTS_2026_*.json'):
    with open(path) as f:
        model = path.split('_')[-1].replace('.json', '')
        rows = json.load(f)
        detected = sum(1 for r in rows if r.get('output', {}).get('hallucination_detected'))
        results[model] = {
            'total': len(rows),
            'detected': detected,
            'rate': round(100 * detected / len(rows), 1)
        }

# Display comparison
df = pd.DataFrame(results).T.sort_values('rate', ascending=False)
print(df)
```

### 3. Questions to Answer

After running upgrades, compare:

- **Detection rate improvement:** Does higher-cost model detect more hallucinations?
  - E.g., Claude Haiku: 25.5% vs. Claude Sonnet: ?%
  
- **False positive rate:** Does premium model have fewer false flags?
  - Fewer false positives = fewer alert fatigue issues
  
- **Adoption risk:** Does better model resist hallucination adoption?
  - Lower adoption rate = safer for clinical use
  
- **Condition sensitivity:** Do premium models benefit more from SAFETY_INSTRUCTION?
  - If yes → safety instructions are model-dependent

---

## Expected Outcomes by Tier

### Tier 0 (Current — Low-Cost Baseline)
- **OpenAI mini:** ~32% detection rate (moderate, prone to adoption)
- **Claude Haiku:** ~26% detection rate (worse, high adoption)
- **Gemini Flash Lite:** ~5% detection rate (poor, silent adoption)

### Tier 1 (Recommended Upgrade — Expected)
- **OpenAI gpt-5.4:** ~45–50% detection rate (better reasoning)
- **Claude Sonnet:** ~35–40% detection rate (improved accuracy)
- **Gemini Flash:** ~8–12% detection rate (incremental gain)

### Tier 2 (Premium — Aspirational)
- **OpenAI gpt-5:** ~60%+ detection rate (excellent, but slow)
- **Claude Opus:** ~50%+ detection rate (best, medical-grade)
- **Gemini Pro:** ~25%+ detection rate (improved reasoning)

---

## Cost Breakdown for Full Upgrade Study

| Model | Cost per Run | Upgrade Cost |
|-------|---|---|
| Current baseline (3 models) | ~$30 | – |
| Tier 1 upgrades (3 models) | ~$120 | +$90 |
| Tier 2 premium (2 models) | ~$150 | +$120 |
| **All 8 models (full comparison)** | **~$250** | **+$220** |

**Budget-conscious approach:** Just upgrade Anthropic (Claude Sonnet). Best ROI.  
**Comprehensive approach:** Upgrade all 3 providers to Tier 1.

---

## Step-by-Step Upgrade Execution

### Prerequisites
Ensure environment variables are properly set:
```bash
# Check current
env | grep PAHS_

# Set to upgrade model (example: Claude Sonnet)
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-sonnet

# Verify
echo $PAHS_ANTHROPIC_MODEL
```

### Run Upgraded Model
```bash
# Pilot (validation, 2 vignettes)
python pilot.py --provider anthropic

# Inspect output
cat 04_results/raw_json/PILOT_2026_RESULTS_anthropic_claude-3-sonnet.json

# Full study (all 293 vignettes)
python pilot.py --provider anthropic --vignettes-count 293
```

### Expected Runtime
- **Anthropic Sonnet:** 2–4 hours (similar to Haiku, better reasoning)
- **OpenAI gpt-5.4:** 3–6 hours (slower, larger model)
- **Gemini Flash:** 2–3 hours (fast, minimal slowdown from Lite)

### Monitor Progress
```bash
# Watch live status updates
tail -f 04_results/raw_json/PAHS_STUDY_RESULTS_2026_*.json | head -20
```

---

## Comparison Workflow After Upgrades

1. **Collect results** (all new model runs)
2. **Run pooled analysis:** `python 03_src/evaluation/pool_hallucination_analysis.py`
3. **Generate comparison tables:**
   ```bash
   # Export to CSV for Excel analysis
   python -c "
   import json
   import pandas as pd
   
   # Load summary files
   summaries = {}
   for model in ['openai_gpt-5.4-mini', 'openai_gpt-5.4', 'anthropic_claude-haiku-4-5', 'anthropic_claude-3-sonnet']:
       try:
           with open(f'04_results/analysis_ready/PAHS_STUDY_RESULTS_2026_{model}_summary.json') as f:
               summaries[model] = json.load(f)
       except:
           pass
   
   # Compare detection rates
   df = pd.DataFrame({
       model: [s.get('overall', {}).get('successful_defense_rate', 0) for s in summaries.values()]
   }).T
   
   print(df)
   df.to_csv('model_comparison.csv')
   "
   ```

4. **Update proposal & results sections** with upgraded model findings

---

## Recommendation Summary

**Priority 1 (Do This):**
- Upgrade **Anthropic to Claude Sonnet** (~$70, worth it)
- Keep OpenAI/Gemini as-is for now (diminishing returns for budget)

**Priority 2 (If Time/Budget Allows):**
- Upgrade **OpenAI to gpt-5.4** (~$40, solid improvement)
- Upgrade **Gemini to Flash** (~$8, cheap, incremental)

**Priority 3 (Skip Unless Critical):**
- Premium tier (Opus, gpt-5, Pro) — too expensive, overkill

**Why?** Balanced cost–benefit. Sonnet upgrade will demonstrate whether better models reduce hallucinations → publishable finding.

