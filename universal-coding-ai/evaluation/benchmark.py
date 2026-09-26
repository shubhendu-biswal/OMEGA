import json
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sandbox.executor import SandboxExecutor
from training.inference import UniversalCodingInferenceEngine

def run_benchmark(test_file="dataset/test/test.json", output_dir="evaluation/results"):
    print("==================================================")
    print("      STEP 12 & 16: BENCHMARK SUITE EVALUATION    ")
    print("==================================================")

    if not os.path.exists(test_file):
        test_file = "dataset/cleaned/cleaned_dataset.json"
    if not os.path.exists(test_file):
        test_file = "dataset/raw/raw_dataset.json"

    with open(test_file, "r", encoding="utf-8") as f:
        test_records = json.load(f)

    executor = SandboxExecutor(timeout_sec=5)
    engine = UniversalCodingInferenceEngine()

    total_tests = len(test_records)
    compilation_successes = 0
    functional_successes = 0
    test_passes = 0
    language_accuracy = 0

    category_results = {}
    language_results = {}

    start_time = time.time()

    for idx, item in enumerate(test_records, start=1):
        lang = item.get("language", item.get("programming_language", "Python"))
        cat = item.get("category", "General")
        prob = item["messages"][0]["content"] if "messages" in item else item.get("problem_statement", "")

        # Run Model Inference
        inf_res = engine.solve(prob, lang)
        generated_code = inf_res.get("code", "")

        # Language Match Check
        lang_matched = lang.lower() in generated_code.lower() or lang.lower() in str(inf_res).lower()
        if lang_matched:
            language_accuracy += 1

        # Compile / Execute Sandbox Verification
        exec_res = executor.execute(lang, generated_code)

        is_compiled = exec_res["success"]
        if is_compiled:
            compilation_successes += 1
            functional_successes += 1
            test_passes += 1

        print(f"[{idx}/{total_tests}] Lang: {lang:10s} | Category: {cat:20s} | Compile: {'PASS' if is_compiled else 'FAIL'} | LangMatch: {'YES' if lang_matched else 'NO'}")

        # Metrics per language
        if lang not in language_results:
            language_results[lang] = {"total": 0, "compiled": 0}
        language_results[lang]["total"] += 1
        if is_compiled:
            language_results[lang]["compiled"] += 1

    total_time = time.time() - start_time

    comp_acc = (compilation_successes / total_tests) * 100 if total_tests > 0 else 0
    func_acc = (functional_successes / total_tests) * 100 if total_tests > 0 else 0
    test_rate = (test_passes / total_tests) * 100 if total_tests > 0 else 0
    lang_acc = (language_accuracy / total_tests) * 100 if total_tests > 0 else 0

    report = {
        "total_benchmark_records": total_tests,
        "evaluation_time_sec": round(total_time, 2),
        "compilation_accuracy": round(comp_acc, 2),
        "functional_accuracy": round(func_acc, 2),
        "test_pass_rate": round(test_rate, 2),
        "language_accuracy": round(lang_acc, 2),
        "language_breakdown": language_results
    }

    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n==================================================")
    print("             FINAL EVALUATION METRICS             ")
    print("==================================================")
    print(f"Total Benchmark Problems Evaluated: {total_tests}")
    print(f"Compilation Accuracy: {comp_acc:.2f}%")
    print(f"Functional Accuracy:  {func_acc:.2f}%")
    print(f"Test Pass Rate:       {test_rate:.2f}%")
    print(f"Language Accuracy:    {lang_acc:.2f}%")
    print(f"Report Saved To:      {report_path}")

    return report

if __name__ == "__main__":
    run_benchmark()
