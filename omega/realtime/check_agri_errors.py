import json
import joblib

m = joblib.load('omega/realtime/models/realtime_intent_model.pkl')
hw = json.load(open('omega/realtime/data/handwritten_test_100.json', encoding='utf-8'))

for r in hw:
    if r['intent'] == 'agriculture':
        p = m.predict([r['text']])[0]
        if p != 'agriculture':
            probs = m.predict_proba([r['text']])[0]
            print(f"Text: '{r['text']}' -> Pred: {p} (Agri conf: {probs[list(m.classes_).index('agriculture')]:.4f}, Pred conf: {max(probs):.4f})")
