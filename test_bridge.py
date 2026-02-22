"""Quick import and smoke-test of the SAM-AI bridge module."""
import sys, os

# Add paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from integration.sam_bridge import compute_truth_level, run_full_analysis
    print("✅ SAM-AI bridge imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Smoke test: compute truth level
print("\n--- Testing compute_truth_level ---")
result = compute_truth_level(
    "If it rains, the ground is wet. It is raining. The ground is wet.",
    llm_confidence=0.85,
)
print(f"  Truth Score:   {result['truth_score']}")
print(f"  Rating:        {result['reliability_rating']}")
print(f"  SAM Calib:     {result['calibrated_confidence']}")
print(f"  Category:      {result['category']}")

# Smoke test: run full analysis
print("\n--- Testing run_full_analysis ---")
report = run_full_analysis("All mammals are animals. All dogs are mammals. Therefore all dogs are animals.")
print(f"  Success:       {report['success']}")
print(f"  Category:      {report['category']}")
print(f"  Quality:       {report['meta_evaluation']['overall_quality']}")
print(f"  Is Valid:      {report['meta_evaluation']['is_valid']}")
print(f"  Calibrated:    {report['uncertainty']['calibrated_confidence']}")
print(f"  Corrected:     {report['correction']['was_corrected']}")

print("\n✅ All smoke tests passed!")
