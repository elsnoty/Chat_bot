from flask import Flask, request, jsonify
import pandas as pd
from rapidfuzz import fuzz, process  # Import process.extractOne
from spellchecker import SpellChecker
import re

app = Flask(__name__)

# Load data
symptoms_df = pd.read_csv('symptoms.csv')
tips_df = pd.read_csv('tips.csv')

# Initialize spell checker
spell = SpellChecker()

def correct_sentence(sentence):
    """Correct spelling mistakes using SpellChecker."""
    corrected_words = [spell.correction(word) if word not in spell else word for word in sentence.split()]
    return " ".join(corrected_words)

def preprocess_text(text):
    """Preprocess text: convert to lowercase and extract words/phrases."""
    text = text.lower()
    tokens = re.findall(r'\b[\w\s]+\b', text)  # Extract words and phrases
    return tokens

def extract_symptoms(text, threshold=85):  # Lower threshold to allow typos
    """Extract potential symptoms from input text using flexible fuzzy matching."""
    tokens = preprocess_text(text)  
    symptom_list = symptoms_df['Symptom'].str.lower().tolist()
    
    extracted = []
    for phrase in tokens:
        best_match = process.extractOne(phrase, symptom_list, scorer=fuzz.WRatio)  # Use WRatio for typo handling
        
        if best_match and best_match[1] >= threshold:  # Accept near matches
            extracted.append(best_match[0])  
    
    return list(set(extracted))  # Remove duplicates

def get_best_symptom_matches(user_inputs, threshold=85):  # Lower threshold for typos
    """Find closest symptom matches with typo tolerance."""
    matched_indices = []
    symptoms_list = symptoms_df['Symptom'].tolist()
    
    for user_input in user_inputs:
        best_match = process.extractOne(user_input, symptoms_list, scorer=fuzz.WRatio)  # Use WRatio for typo flexibility
        
        if best_match and best_match[1] >= threshold:  # Ensure good match
            matched_index = symptoms_df[symptoms_df['Symptom'].str.lower() == best_match[0].lower()].index.tolist()
            matched_indices.extend(matched_index)
    
    return list(set(matched_indices))  # Remove duplicates

def get_tips_for_symptoms(matched_indices):
    """Retrieve tips for matched symptoms."""
    tips_list = []
    for index in matched_indices:
        symptom_name = symptoms_df.loc[index, 'Symptom']
        symptom_id = symptoms_df.loc[index, 'Symptom_ID']
        tips = tips_df[tips_df['Symptom_ID'] == symptom_id][['Tip1', 'Tip2', 'Tip3']].values.flatten()
        tips_list.append({
            "symptom": symptom_name,
            "tips": [tip for tip in tips if pd.notna(tip)]
        })
    return tips_list

@app.route('/get_tips', methods=['POST'])
def get_tips():
    data = request.json
    user_input = data.get('text', '').strip()
    
    corrected_input = correct_sentence(user_input)  # Fix typos first
   
    
    extracted_symptoms = extract_symptoms(corrected_input)
   
    
    matched_indices = get_best_symptom_matches(extracted_symptoms)
    
    
    tips = get_tips_for_symptoms(matched_indices)
    
    
    return jsonify({"symptoms": tips})

@app.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    app.run(debug=True)
