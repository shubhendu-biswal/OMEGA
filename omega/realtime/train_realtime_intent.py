import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
MODELS_DIR = os.path.join(CURRENT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TARGET_CLASSES = [
    "math",
    "gk",
    "agriculture",
    "crop_recommendation",
    "fertilizer_recommendation",
    "conversation",
    "out_of_scope",
    "realtime"
]

def load_data():
    train_path = os.path.join(DATA_DIR, "intent_train_v3.json")
    test_path = os.path.join(DATA_DIR, "intent_held_out_test_v3.json")
    
    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        
    X_train = [r["text"] for r in train_data]
    y_train = [r["intent"] for r in train_data]
    
    X_test = [r["text"] for r in test_data]
    y_test = [r["intent"] for r in test_data]
    
    return X_train, y_train, X_test, y_test

def train_and_evaluate():
    print("=" * 70)
    print("  OMEGA Stage 1: Realtime Intent Classifier Training & Evaluation")
    print("=" * 70)
    
    X_train, y_train, X_test, y_test = load_data()
    print(f"Dataset summary:")
    print(f"  - Training samples: {len(X_train):,}")
    print(f"  - Held-out test samples: {len(X_test):,}")
    
    # 1. Feature Extraction: Dual Word + Character n-grams for Hinglish & English
    print("\n[1/4] Constructing Feature Extraction Pipeline...")
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=30000,
        token_pattern=r'(?u)\b\w+\b'
    )
    
    char_vectorizer = TfidfVectorizer(
        ngram_range=(2, 5),
        analyzer='char',
        sublinear_tf=True,
        min_df=3,
        max_features=45000
    )
    
    features = FeatureUnion([
        ('word', word_vectorizer),
        ('char', char_vectorizer)
    ])
    
    base_clf = LinearSVC(C=1.5, class_weight='balanced', random_state=42, max_iter=3000)
    calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=3)
    
    pipeline = Pipeline([
        ('features', features),
        ('classifier', calibrated_clf)
    ])
    
    # 2. Train Model
    print("\n[2/4] Training Realtime Intent Model on Training Split...")
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    train_duration = time.time() - start_time
    print(f"  Model trained in {train_duration:.2f} seconds.")
    
    # 3. Evaluate on Held-Out Test Split
    print("\n[3/4] Evaluating on HELD-OUT Test Split (Zero Cluster Overlap)...")
    y_test_pred = pipeline.predict(X_test)
    y_test_probs = pipeline.predict_proba(X_test)
    
    test_acc = accuracy_score(y_test, y_test_pred)
    macro_f1 = f1_score(y_test, y_test_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_test_pred, average='weighted')
    
    print(f"\nHELD-OUT EVALUATION METRICS:")
    print(f"  - Overall Accuracy:  {test_acc * 100:.2f}% ({int(test_acc * len(y_test))}/{len(y_test)})")
    print(f"  - Macro-F1 Score:    {macro_f1:.4f}")
    print(f"  - Weighted-F1 Score: {weighted_f1:.4f}")
    
    classes = list(pipeline.classes_)
    report_dict = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, output_dict=True)
    report_str = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, digits=4)
    print("\nDetailed Per-Class Classification Report (Held-Out Test):")
    print(report_str)
    
    cm = confusion_matrix(y_test, y_test_pred, labels=classes)
    print("\nConfusion Matrix (Rows: Ground Truth, Cols: Predicted):")
    print(f"{'':<25}" + "".join([f"{c[:10]:>12}" for c in classes]))
    for idx, row in enumerate(cm):
        row_str = "".join([f"{val:>12}" for val in row])
        print(f"{classes[idx]:<25}{row_str}")

    # 4. Check Explicit Stage 1 Pass Criteria:
    # PASS Criterion 1: realtime recall above 90%
    # PASS Criterion 2: static GK questions misrouted to realtime below 5%
    realtime_precision = report_dict["realtime"]["precision"]
    realtime_recall = report_dict["realtime"]["recall"]
    realtime_f1 = report_dict["realtime"]["f1-score"]
    
    # Calculate static GK misroute rate to realtime
    gk_total = 0
    gk_misrouted_to_realtime = 0
    for true_y, pred_y in zip(y_test, y_test_pred):
        if true_y == "gk":
            gk_total += 1
            if pred_y == "realtime":
                gk_misrouted_to_realtime += 1
                
    gk_misroute_rate = (gk_misrouted_to_realtime / gk_total) if gk_total > 0 else 0.0
    
    print("\n" + "=" * 70)
    print("  STAGE 1 PASS CRITERIA VERIFICATION")
    print("=" * 70)
    print(f"  1. Realtime Recall: {realtime_recall * 100:.2f}% (Threshold: > 90.00%)")
    pass_recall = realtime_recall > 0.90
    print(f"     Status: {'[PASS]' if pass_recall else '[FAIL]'}")
    
    print(f"  2. Static GK Misrouted to Realtime: {gk_misroute_rate * 100:.2f}% ({gk_misrouted_to_realtime}/{gk_total}) (Threshold: < 5.00%)")
    pass_gk = gk_misroute_rate < 0.05
    print(f"     Status: {'[PASS]' if pass_gk else '[FAIL]'}")

    overall_pass = pass_recall and pass_gk
    print(f"\n  STAGE 1 OVERALL RESULT: {'[STAGE 1 PASS]' if overall_pass else '[STAGE 1 FAIL]'}")
    print("=" * 70)

    # 5. Save Model Artifacts
    print(f"\n[4/4] Saving model artifacts to {MODELS_DIR}...")
    model_file = os.path.join(MODELS_DIR, "realtime_intent_model.pkl")
    metadata_file = os.path.join(MODELS_DIR, "realtime_intent_metadata.json")
    
    joblib.dump(pipeline, model_file)
    print(f"  Saved trained pipeline to: {model_file}")
    
    metadata = {
        "model_type": "FeatureUnion(Word_Char_TFIDF) + CalibratedClassifierCV(LinearSVC)",
        "classes": classes,
        "num_training_samples": len(X_train),
        "num_held_out_samples": len(X_test),
        "held_out_metrics": {
            "accuracy": round(test_acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "realtime_precision": round(realtime_precision, 4),
            "realtime_recall": round(realtime_recall, 4),
            "realtime_f1": round(realtime_f1, 4),
            "static_gk_misroute_to_realtime_rate": round(gk_misroute_rate, 4),
            "gk_misrouted_count": gk_misrouted_to_realtime,
            "gk_total_count": gk_total
        },
        "pass_criteria": {
            "realtime_recall_above_90": bool(pass_recall),
            "gk_misroute_below_5": bool(pass_gk),
            "overall_pass": bool(overall_pass)
        },
        "training_duration_seconds": round(train_duration, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved metadata to: {metadata_file}")
    
    # Also save synchronized version in ml_service/assets/v2/intent/ without overwriting legacy intent_model.pkl
    v2_assets_dir = os.path.join(CURRENT_DIR, "..", "..", "ml_service", "assets", "v2", "intent")
    try:
        os.makedirs(v2_assets_dir, exist_ok=True)
        joblib.dump(pipeline, os.path.join(v2_assets_dir, "intent_model_v3_realtime.pkl"))
        with open(os.path.join(v2_assets_dir, "intent_metadata_v3_realtime.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"  Saved non-destructive copy to: {v2_assets_dir}/intent_model_v3_realtime.pkl")
    except Exception as e:
        print(f"  Note on v2 assets sync: {e}")

    return {
        "test_acc": test_acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "realtime_precision": realtime_precision,
        "realtime_recall": realtime_recall,
        "realtime_f1": realtime_f1,
        "gk_misroute_rate": gk_misroute_rate,
        "report_dict": report_dict,
        "report_str": report_str,
        "cm": cm.tolist(),
        "classes": classes,
        "pass_recall": pass_recall,
        "pass_gk": pass_gk,
        "overall_pass": overall_pass
    }

if __name__ == "__main__":
    train_and_evaluate()
