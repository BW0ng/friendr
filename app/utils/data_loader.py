"""
Data loader for pet matching application.
Loads pet data from CSV and provides methods to get pets by type.
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
import random

class PetDataLoader:
    def __init__(self, csv_path: str = "data/friends4life_shelterluv_animals.csv"):
        """Initialize the data loader with the CSV file path."""
        self.csv_path = csv_path
        self.df = None
        self.image_mapping = {}
        self.load_data()
        self.load_image_mapping()
    
    def load_data(self):
        """Load and preprocess the pet data from CSV."""
        try:
            # Load the CSV
            self.df = pd.read_csv(self.csv_path)
            
            # Convert species column to lowercase and rename to type for consistency
            self.df['type'] = self.df['species'].str.lower()
            
            # Filter to only include dogs and cats
            self.df = self.df[self.df['type'].isin(['dog', 'cat'])]
            
            # Convert age from months to years (round to nearest year)
            self.df['age_years'] = (self.df['age'] / 12).round().astype(int)
            
            # Fill missing weight values with median weight by type
            for pet_type in ['dog', 'cat']:
                type_data = self.df[self.df['type'] == pet_type]
                median_weight = type_data['weight'].median()
                self.df.loc[self.df['type'] == pet_type, 'weight'] = self.df.loc[self.df['type'] == pet_type, 'weight'].fillna(median_weight)
            
            # Fill missing size values
            self.df['size'] = self.df['size'].fillna('Unknown')
            
            # Fill missing breed values
            self.df['breed'] = self.df['breed'].fillna('Mixed Breed')
            
            print(f"Loaded {len(self.df)} pets from {self.csv_path}")
            print(f"Pet distribution: {self.df['type'].value_counts().to_dict()}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def load_image_mapping(self):
        """Load the image mapping file if it exists."""
        mapping_path = Path("data/pet_image_mapping.json")
        if mapping_path.exists():
            try:
                with open(mapping_path, 'r') as f:
                    self.image_mapping = json.load(f)
                print(f"Loaded image mapping for {len(self.image_mapping)} pets")
            except Exception as e:
                print(f"Error loading image mapping: {e}")
                self.image_mapping = {}
    
    def get_pets_by_type(self, pet_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get pets filtered by type (dog or cat).
        
        Args:
            pet_type: 'dog' or 'cat'
            limit: Maximum number of pets to return (None for all)
            
        Returns:
            List of pet dictionaries
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Filter by type
        filtered_df = self.df[self.df['type'] == pet_type.lower()]
        
        # Apply limit if specified
        if limit:
            filtered_df = filtered_df.head(limit)
        
        # Convert to list of dictionaries
        pets = []
        for _, row in filtered_df.iterrows():
            pet_dict = {
                'type': row['type'],
                'name': row['name'],
                'age': row['age_years'],  # Use converted age in years
                'breed': row['breed'],
                'size': row['size'],
                'weight': float(row['weight']) if pd.notna(row['weight']) else None,
                'dogs': int(row['dogs']),
                'cats': int(row['cats']),
                'kids': int(row['kids']),
                'energy': int(row['energy']),
                'affection': int(row['affection']),
                'training': int(row['training']),
                'image_url': self.get_pet_image(row['name'])
            }
            pets.append(pet_dict)
        
        return pets
    
    def get_pet_image(self, pet_name: str) -> str:
        """
        Get the local image path for a pet.
        
        Args:
            pet_name: Name of the pet
            
        Returns:
            Local image path or None if not found
        """
        if pet_name in self.image_mapping:
            pet_type = self.image_mapping[pet_name]['type']
            filename = self.image_mapping[pet_name]['filename']
            return f"/image/{pet_type}/{filename}"
        
        # Fallback: try to find a matching image file
        # This is a backup method in case the mapping is incomplete
        for pet_type in ['dog', 'cat']:
            images_dir = Path(f"data/images/{pet_type}s")
            if images_dir.exists():
                # Look for files that might match this pet name
                safe_name = "".join(c for c in pet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                
                for image_file in images_dir.glob(f"*{safe_name}*"):
                    return f"/image/{pet_type}/{image_file.name}"
        
        return None
    
    def get_all_pets(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all pets.
        
        Args:
            limit: Maximum number of pets to return (None for all)
            
        Returns:
            List of pet dictionaries
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Apply limit if specified
        df_to_use = self.df
        if limit:
            df_to_use = self.df.head(limit)
        
        # Convert to list of dictionaries
        pets = []
        for _, row in df_to_use.iterrows():
            pet_dict = {
                'type': row['type'],
                'name': row['name'],
                'age': row['age_years'],  # Use converted age in years
                'breed': row['breed'],
                'size': row['size'],
                'weight': float(row['weight']) if pd.notna(row['weight']) else None,
                'dogs': int(row['dogs']),
                'cats': int(row['cats']),
                'kids': int(row['kids']),
                'energy': int(row['energy']),
                'affection': int(row['affection']),
                'training': int(row['training']),
                'image_url': self.get_pet_image(row['name'])
            }
            pets.append(pet_dict)
        
        return pets
    
    def get_random_pets(self, pet_type: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get random pets of a specific type.
        
        Args:
            pet_type: 'dog' or 'cat'
            count: Number of random pets to return
            
        Returns:
            List of random pet dictionaries
        """
        all_pets = self.get_pets_by_type(pet_type)
        return random.sample(all_pets, min(count, len(all_pets)))
    
    def get_pet_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pet data.
        
        Returns:
            Dictionary with statistics
        """
        if self.df is None:
            return {}
        
        stats = {
            'total_pets': len(self.df),
            'pet_types': self.df['type'].value_counts().to_dict(),
            'age_range': {
                'min': self.df['age_years'].min(),
                'max': self.df['age_years'].max(),
                'mean': round(self.df['age_years'].mean(), 1)
            },
            'weight_range': {
                'min': self.df['weight'].min(),
                'max': self.df['weight'].max(),
                'mean': round(self.df['weight'].mean(), 1)
            }
        }
        
        return stats

# Global instance for use in the application
pet_loader = PetDataLoader()
