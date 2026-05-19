import json
from collections import Counter

with open('04_results/raw_json/PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json') as f:
    data = json.load(f)

# The 'output' field is a dictionary containing the detailed results
def extract_safety_patterns(items):
    adoption_failure = 0
    detection_success = 0
    dangerous_reasoning = 0
    
    for item in items:
        output = item.get('output', {})
        if isinstance(output, dict):
            log = str(output.get('safety_audit_log', '')).lower()
            if 'unrecognized' in log:
                adoption_failure += 1
            if 'hallucination_trap' in log:
                detection_success += 1
            if 'dangerous_reasoning' in log:
                dangerous_reasoning += 1
    return adoption_failure, detection_success, dangerous_reasoning

for cond in ['DEFAULT', 'SAFETY_INSTRUCTION', 'DETERMINISTIC']:
    cond_items = [x for x in data if x.get('condition') == cond]
    n = len(cond_items)
    if n > 0:
        halluc_detected = sum(1 for x in cond_items if isinstance(x.get('output'), dict) and x['output'].get('hallucination_detected') == True)
        adoption_fail, detect_success, danger_reason = extract_safety_patterns(cond_items)
        
        print(f"\n{cond} (n={n})")
        print(f"  Hallucinations detected: {halluc_detected} ({100*halluc_detected/n:.1f}%)")
        print(f"  Adoption failures: {adoption_fail} ({100*adoption_fail/n:.1f}%)")
        print(f"  Detection successes: {detect_success} ({100*detect_success/n:.1f}%)")
        print(f"  Dangerous reasoning: {danger_reason} ({100*danger_reason/n:.1f}%)")

# Show top safety patterns
print("\n=== Safety Audit Log Patterns ===")
patterns = Counter()
for x in data:
    output = x.get('output', {})
    if isinstance(output, dict):
        log = str(output.get('safety_audit_log', '')).lower()
        if 'hallucination_trap' in log: patterns['hallucination_trap'] += 1
        if 'unrecognized' in log: patterns['unrecognized'] += 1
        if 'dangerous_reasoning' in log: patterns['dangerous_reasoning'] += 1
        if 'safe' in log: patterns['safe'] += 1

for pattern, count in patterns.most_common(10):
    print(f"{pattern}: {count}")
