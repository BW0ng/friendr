# ml_model/predictor.py
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

SAVE_DIR = Path("saved_models")

NUM_MATCHES = 6  # Number of top matches to return

def load_model(pet_type: str):
    if pet_type == "dog":
        return joblib.load(SAVE_DIR / "kmeans_dog.pkl")
    elif pet_type == "cat":
        return joblib.load(SAVE_DIR / "kmeans_cat.pkl")
    else:
        raise ValueError("pet_type must be 'dog' or 'cat'")

def predict_match(user_input: dict, pet_type: str, pet_data: pd.DataFrame):
    # Load appropriate model + scaler
    (kmeans, scaler) = load_model(pet_type)
    print(f"Loaded model for pet_type: {pet_type}")

    # Use the correct feature columns that match the training data
    feature_cols = [
        "dogs",
        "cats", 
        "kids",
        "energy",
        "affection",
        "training",
        "new_people"
    ]

    # Convert user input into numpy array and scale
    user_vector = np.array([[user_input[col] for col in feature_cols]])
    user_vector_scaled = scaler.transform(user_vector)
    print(f"User vector (scaled): {user_vector_scaled}")

    # Predict cluster for user
    cluster = kmeans.predict(user_vector_scaled)[0]
    print(f"User assigned to cluster: {cluster}")

    # Filter pets of that type
    pets = pet_data[pet_data["type"] == pet_type]
    print(f"Number of pets of type '{pet_type}': {len(pets)}")

    # Scale the pet dataset with the same scaler
    pets_scaled = scaler.transform(pets[feature_cols])
    print(f"Scaled pet features shape: {pets_scaled.shape}")

    # Compute similarity (Euclidean distance to user_vector)
    distances = np.linalg.norm(pets_scaled - user_vector_scaled, axis=1)
    print(f"Computed distances: {distances}")

    # Convert distances to similarity %
    similarities = 100 * (1 - (distances / distances.max()))

    # Attach similarity to pets
    pets = pets.copy()
    pets["match_percentage"] = similarities
    print(f"Pets with match percentages calculated: \n{pets}")

    # Return top 6 matches (configurable - change head(6) to head(n) for different number)
    top_matches = pets.sort_values("match_percentage", ascending=False).head(NUM_MATCHES)
    return top_matches.to_dict(orient="records")
