import joblib
import os

def load_predictor():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, 'models', 'risk_model.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model file not found. Please train the model first.")
    
    return joblib.load(model_path)

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Pre-download NLTK data if not present (quietly)
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except:
    pass

def clean_text(text):
    """Standardizes text to match the format used during model training."""
    if not text:
        return ""
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

def predict_risk(text):
    """
    Predicts risk for a list of strings or a single string.
    Automatically applies clean_text preprocessing before prediction.
    """
    model = load_predictor()
    
    # Ensure text is a list for batch processing
    if isinstance(text, str):
        text_list = [text]
    else:
        text_list = text
    
    # Apply preprocessing to match training data format
    cleaned_texts = [clean_text(t) for t in text_list]
    
    prediction = model.predict(cleaned_texts)
    probabilities = model.predict_proba(cleaned_texts)
    
    results = []
    for i in range(len(text_list)):
        result = {
            'text': text_list[i],
            'is_risky': bool(prediction[i]),
            'risk_probability': float(probabilities[i][1])
        }
        results.append(result)
        
    return results

if __name__ == '__main__':
    sample_texts = [
        "The company shall not make any investments without prior approval.",
        "We agree to pay the standard fee for the services rendered."
    ]
    predictions = predict_risk(sample_texts)
    for p in predictions:
        print(f"Risk: {p['is_risky']} | Prob: {p['risk_probability']:.2f} | Text: {p['text']}")
