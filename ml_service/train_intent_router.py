import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
    precision_recall_fscore_support
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ASSETS_V2_INTENT_DIR = os.path.join(os.path.dirname(__file__), "assets", "v2", "intent")
os.makedirs(ASSETS_V2_INTENT_DIR, exist_ok=True)

TARGET_CLASSES = [
    "math",
    "gk",
    "agriculture",
    "crop_recommendation",
    "fertilizer_recommendation",
    "conversation",
    "out_of_scope"
]

def load_data():
    train_path = os.path.join(DATA_DIR, "intent_train.json")
    test_path = os.path.join(DATA_DIR, "intent_held_out_test.json")
    hindi_path = os.path.join(DATA_DIR, "intent_hindi_hinglish_100.json")
    
    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(hindi_path, "r", encoding="utf-8") as f:
        hindi_data = json.load(f)
        
    X_train = [r["text"] for r in train_data]
    y_train = [r["intent"] for r in train_data]
    
    X_test = [r["text"] for r in test_data]
    y_test = [r["intent"] for r in test_data]
    
    X_hindi = [r["query"] for r in hindi_data]
    y_hindi = [r["intent"] for r in hindi_data]
    
    return X_train, y_train, X_test, y_test, X_hindi, y_hindi

def train_and_evaluate():
    print("=" * 65)
    print("  OMEGA Stage 2: Intent Classifier & Router Training")
    print("=" * 65)
    
    X_train, y_train, X_test, y_test, X_hindi, y_hindi = load_data()
    print(f"Dataset summary:")
    print(f"  - Training samples: {len(X_train):,}")
    print(f"  - Held-out test samples: {len(X_test):,}")
    print(f"  - Hindi/Hinglish test samples: {len(X_hindi):,}")
    
    # 1. Feature Extraction: Dual Word + Character n-grams for Hinglish & English
    print("\n[1/4] Constructing Feature Extraction Pipeline...")
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=25000,
        token_pattern=r'(?u)\b\w+\b'
    )
    
    char_vectorizer = TfidfVectorizer(
        ngram_range=(2, 5),
        analyzer='char',
        sublinear_tf=True,
        min_df=3,
        max_features=40000
    )
    
    features = FeatureUnion([
        ('word', word_vectorizer),
        ('char', char_vectorizer)
    ])
    
    # Base classifier: LinearSVC calibrated for smooth, well-calibrated probabilities
    base_clf = LinearSVC(C=1.5, class_weight='balanced', random_state=42, max_iter=3000)
    calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=3)
    
    pipeline = Pipeline([
        ('features', features),
        ('classifier', calibrated_clf)
    ])
    
    print("\n[2/4] Training Router Model on Training Split...")
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    train_duration = time.time() - start_time
    print(f"  Model trained in {train_duration:.2f} seconds.")
    
    # 2. Evaluation on Held-Out Test Set (CRITICAL: Never report training accuracy)
    print("\n[3/4] Evaluating on HELD-OUT Test Split (Zero Template Overlap)...")
    y_test_pred = pipeline.predict(X_test)
    y_test_probs = pipeline.predict_proba(X_test)
    
    test_acc = accuracy_score(y_test, y_test_pred)
    macro_f1 = f1_score(y_test, y_test_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_test_pred, average='weighted')
    
    print(f"\nHELD-OUT EVALUATION METRICS:")
    print(f"  - Overall Accuracy:  {test_acc * 100:.2f}%")
    print(f"  - Macro-F1 Score:    {macro_f1:.4f}  (Pass Criterion: > 0.90)")
    print(f"  - Weighted-F1 Score: {weighted_f1:.4f}")
    
    # Check Pass Criterion
    if macro_f1 >= 0.90:
        print(f"\n  [PASS] Macro-F1 ({macro_f1:.4f}) EXCEEDS the > 0.90 requirement!")
    else:
        print(f"\n  [FAIL] Macro-F1 ({macro_f1:.4f}) is below the > 0.90 threshold.")
        
    classes = list(pipeline.classes_)
    
    print("\nDetailed Per-Class Classification Report (Held-Out Test):")
    report_dict = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, output_dict=True)
    report_str = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, digits=4)
    print(report_str)
    
    cm = confusion_matrix(y_test, y_test_pred, labels=classes)
    print("\nConfusion Matrix (Rows: Ground Truth, Cols: Predicted):")
    print(f"{'':<25}" + "".join([f"{c[:10]:>12}" for c in classes]))
    for idx, row in enumerate(cm):
        row_str = "".join([f"{val:>12}" for val in row])
        print(f"{classes[idx]:<25}{row_str}")

    # 3. Evaluation on 100 Hindi / Hinglish Test Set
    print("\n[4/4] Evaluating on 100 HINDI / HINGLISH Test Set...")
    y_hindi_pred = pipeline.predict(X_hindi)
    y_hindi_probs = pipeline.predict_proba(X_hindi)
    
    hindi_acc = accuracy_score(y_hindi, y_hindi_pred)
    hindi_macro_f1 = f1_score(y_hindi, y_hindi_pred, average='macro')
    
    print(f"\nHINDI / HINGLISH EVALUATION METRICS (100 Items):")
    print(f"  - Accuracy: {hindi_acc * 100:.2f}% ({int(hindi_acc * len(y_hindi))}/{len(y_hindi)})")
    print(f"  - Macro-F1: {hindi_macro_f1:.4f}")
    
    print("\nDetailed Per-Class Classification Report (Hindi/Hinglish Test):")
    hindi_report_str = classification_report(y_hindi, y_hindi_pred, labels=classes, target_names=classes, digits=4)
    print(hindi_report_str)
    
    # Check Hindi failure cases if any
    failures = []
    for q, true_lbl, pred_lbl, probs in zip(X_hindi, y_hindi, y_hindi_pred, y_hindi_probs):
        if true_lbl != pred_lbl:
            top_prob = float(np.max(probs))
            failures.append({
                "query": q,
                "expected": true_lbl,
                "predicted": pred_lbl,
                "confidence": round(top_prob, 4)
            })
            
    if failures:
        print(f"\nHindi/Hinglish Misclassifications ({len(failures)} failures):")
        for f in failures:
            print(f"  * Query: '{f['query']}'")
            print(f"    Expected: {f['expected']}, Predicted: {f['predicted']} (Conf: {f['confidence']})")
    else:
        print("\nPerfect 100% classification on Hindi/Hinglish test set!")

    # 4. Save Model Artifacts
    print(f"\nSaving model artifacts to {ASSETS_V2_INTENT_DIR}...")
    model_file = os.path.join(ASSETS_V2_INTENT_DIR, "intent_model.pkl")
    metadata_file = os.path.join(ASSETS_V2_INTENT_DIR, "intent_metadata.json")
    
    joblib.dump(pipeline, model_file)
    print(f"  Saved trained pipeline to {model_file}")
    
    metadata = {
        "model_type": "FeatureUnion(Word_Char_TFIDF) + CalibratedClassifierCV(LinearSVC)",
        "classes": TARGET_CLASSES,
        "classes_in_classifier": list(pipeline.classes_),
        "num_training_samples": len(X_train),
        "num_held_out_samples": len(X_test),
        "held_out_metrics": {
            "accuracy": round(test_acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4)
        },
        "hindi_hinglish_metrics": {
            "num_samples": len(X_hindi),
            "accuracy": round(hindi_acc, 4),
            "macro_f1": round(hindi_macro_f1, 4),
            "failures_count": len(failures)
        },
        "training_duration_seconds": round(train_duration, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved metadata to {metadata_file}")
    
    # Save a copy in workspace assets/v2/intent if needed
    root_assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "v2", "intent")
    try:
        os.makedirs(root_assets_dir, exist_ok=True)
        joblib.dump(pipeline, os.path.join(root_assets_dir, "intent_model.pkl"))
        with open(os.path.join(root_assets_dir, "intent_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"  Synchronized copy to workspace root: {root_assets_dir}")
    except Exception as e:
        print(f"  (Note: root sync skipped: {e})")

    return {
        "test_acc": test_acc,
        "macro_f1": macro_f1,
        "hindi_acc": hindi_acc,
        "hindi_macro_f1": hindi_macro_f1,
        "report_dict": report_dict,
        "cm": cm.tolist(),
        "failures": failures
    }

if __name__ == "__main__":
    train_and_evaluate()
