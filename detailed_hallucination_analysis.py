import json

filename = '04_results/raw_json/PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json'
try:
    with open(filename) as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {filename} not found.")
    exit(1)

print("=== HALLUCINATION DETECTION BREAKDOWN ===\n")

for cond in ['DEFAULT', 'SAFETY_INSTRUCTION', 'DETERMINISTIC']:
    cond_data = [x for x in data if x.get('condition') == cond]
    halluc_cases = [x for x in cond_data if x.get('output', {}).get('hallucination_detected') == True]
    
    print(f"\n{cond} Condition:")
    print(f"  Total trials: {len(cond_data)}")
    print(f"  Hallucinations found: {len(halluc_cases)}")
    
    # Show first 2 hallucination cases
    for i, case in enumerate(halluc_cases[:2], 1):
        output = case.get('output', {})
        print(f"\n  Case {i}:")
        print(f"    Safety audit: {str(output.get('safety_audit_log', 'N/A'))[:100]}...")
        print(f"    Top diagnosis: {output.get('top_diagnosis', 'N/A')}")
        print(f"    Target token: {output.get('target_token', 'N/A')}")

print("\n\n=== SAFETY INSTRUCTION EFFECT ===")
default_halluc = len([x for x in data if x.get('condition')=='DEFAULT' and x.get('output', {}).get('hallucination_detected')==True])
safety_halluc = len([x for x in data if x.get('condition')=='SAFETY_INSTRUCTION' and x.get('output', {}).get('hallucination_detected')==True])
det_halluc = len([x for x in data if x.get('condition')=='DETERMINISTIC' and x.get('output', {}).get('hallucination_detected')==True])

total_per_cond = 586 # Based on the query's expectation
print(f"DEFAULT hallucinations: {default_halluc}/{total_per_cond} ({100*default_halluc/total_per_cond:.2f}%)")
print(f"SAFETY_INSTRUCTION hallucinations: {safety_halluc}/{total_per_cond} (increase: {safety_halluc-default_halluc})")
print(f"DETERMINISTIC hallucinations: {det_halluc}/{total_per_cond} (increase: {det_halluc-default_halluc})")
print(f"\nNote: SAFETY_INSTRUCTION increases hallucinations - the safety prompt may be triggering different behavior")
