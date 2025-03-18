import pandas as pd
import difflib

# Load the Symptoms CSV
symptoms_df = pd.read_csv("symptoms.csv")

# Load the Tips CSV
tips_df = pd.read_csv("tips.csv")

# Load the spell checker words
with open("SpellCheakerTextHelper.txt", "r") as file:
    correct_words = [line.strip().lower() for line in file.readlines()]

# Merge Symptoms and Tips on Symptom_ID
merged_df = pd.merge(symptoms_df, tips_df, on="Symptom_ID")

# Function to get the closest word if there is a typo
def correct_spelling(word):
    matches = difflib.get_close_matches(word.lower(), correct_words, n=1, cutoff=0.8)
    return matches[0] if matches else word  # Return closest match or original if no match found

# Function to retrieve tips for a given symptom
def get_tips_for_symptom(symptom_name):
    symptom_name = correct_spelling(symptom_name)  # Correct spelling before searching
    row = merged_df[merged_df["Symptom"] == symptom_name]
    
    if not row.empty:
        tips = row.iloc[0, 2:].dropna().tolist()  # Drop NaN values and convert to list
        return tips
    else:
        return [f"No tips found for '{symptom_name}'. Did you mean something else?"]

# Example Usage:
symptom_name = "acn"  # Intentionally misspelled
tips = get_tips_for_symptom(symptom_name)
print(f"Tips for {symptom_name}: {tips}")
