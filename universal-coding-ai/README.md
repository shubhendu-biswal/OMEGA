# Universal Coding Problem Solver AI

An end-to-end code-capable language model fine-tuning, evaluation, sandbox execution, and self-correction framework supporting **18 programming languages**:
Java, Python, C, C++, JavaScript, TypeScript, C#, Go, Rust, Kotlin, Swift, PHP, Ruby, Dart, Scala, R, SQL, and MATLAB.

## Features
- **18 Language Support**: Solves, debugs, optimizes, and converts code across all 18 target languages.
- **20 Algorithmic Domains**: Covers Arrays, Strings, Hashing, Sorting, Searching, Two Pointers, Sliding Window, Stack, Queue, Heap, Recursion, Backtracking, Greedy, Dynamic Programming, Trees, Graphs, Trie, Union Find, Bit Manipulation, Math, Debugging, Optimization, and Language Conversion.
- **Data Pipeline**: Automated cleaning, deduplication, isolated execution validation, and leakage-free splitting (80/10/10).
- **LoRA / SFT Training**: Supervised Fine-Tuning with LoRA adapter support and CPU/GPU hardware fallback.
- **Isolated Sandbox**: Timeout, memory, and security restricted execution for Python, Java, C, C++, and Node.js.
- **Self-Correction Engine**: Closed-loop feedback cycle (up to 3 retries) feeding compile/runtime tracebacks back into the inference model.
- **Benchmark Suite**: Execution-based metric evaluation measuring Compilation Accuracy, Functional Accuracy, Test Pass Rate, and Language Accuracy.

## Project Structure
```text
universal-coding-ai/
├── dataset/
├── preprocessing/
├── training/
├── evaluation/
├── model/
├── backend/
├── sandbox/
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Clean, deduplicate, validate, format, and split dataset:
   ```bash
   python preprocessing/clean_dataset.py
   python preprocessing/remove_duplicates.py
   python preprocessing/validate_code.py
   python preprocessing/format_dataset.py
   python preprocessing/split_dataset.py
   ```
3. Run training:
   ```bash
   python training/train.py --config training/training_config.yaml
   ```
4. Run evaluation benchmark:
   ```bash
   python evaluation/benchmark.py
   ```
5. Inference:
   ```bash
   python training/inference.py --problem "Given an array of integers, find two numbers whose sum equals target. Give Java code." --language "Java"
   ```
