#!/usr/bin/env python3
"""
Script to assign default images to pets that don't have photos.
Uses the old default images from the original dataset.
"""

import pandas as pd
import json
import random
from pathlib import Path
import shutil

def assign_default_images():
    """Assign default images to pets without photos"""
    
    # Paths
    csv_path = Path("data/friends4life_shelterluv_animals.csv")
    images_base_path = Path("data/images")
    mapping_path = Path("data/pet_image_mapping.json")
    
    # Load the CSV
    df = pd.read_csv(csv_path)
    df['type'] = df['species'].str.lower()
    df = df[df['type'].isin(['dog', 'cat'])]
    
    # Load existing image mapping
    if mapping_path.exists():
        with open(mapping_path, 'r') as f:
            image_mapping = json.load(f)
    else:
        image_mapping = {}
    
    # Find pets without images
    pets_without_images = []
    for _, row in df.iterrows():
        if row['name'] not in image_mapping:
            pets_without_images.append({
                'name': row['name'],
                'type': row['type']
            })
    
    print(f"Found {len(pets_without_images)} pets without images")
    
    # Get list of available default images
    default_dog_images = []
    default_cat_images = []
    
    # Look for default images in the existing directories
    dogs_dir = images_base_path / "dogs"
    cats_dir = images_base_path / "cats"
    
    if dogs_dir.exists():
        for img_file in dogs_dir.glob("*"):
            if img_file.name.startswith(('dog_', 'cat_')) and img_file.suffix in ['.jpg', '.jpeg', '.png']:
                # Check if it looks like a default image (simple naming pattern)
                if len(img_file.stem.split('_')) == 2:  # e.g., "dog_114" or "cat_1"
                    default_dog_images.append(img_file.name)
    
    if cats_dir.exists():
        for img_file in cats_dir.glob("*"):
            if img_file.name.startswith(('dog_', 'cat_')) and img_file.suffix in ['.jpg', '.jpeg', '.png']:
                # Check if it looks like a default image (simple naming pattern)
                if len(img_file.stem.split('_')) == 2:  # e.g., "dog_114" or "cat_1"
                    default_cat_images.append(img_file.name)
    
    print(f"Found {len(default_dog_images)} default dog images")
    print(f"Found {len(default_cat_images)} default cat images")
    
    # Assign default images to pets without photos
    assigned_count = 0
    
    for pet in pets_without_images:
        pet_type = pet['type']
        pet_name = pet['name']
        
        if pet_type == 'dog' and default_dog_images:
            # Pick a random default dog image
            default_image = random.choice(default_dog_images)
            assigned_count += 1
        elif pet_type == 'cat' and default_cat_images:
            # Pick a random default cat image
            default_image = random.choice(default_cat_images)
            assigned_count += 1
        else:
            print(f"No default images available for {pet_type}s")
            continue
        
        # Add to mapping
        image_mapping[pet_name] = {
            'type': pet_type,
            'filename': default_image,
            'original_url': 'default_image'
        }
        
        print(f"Assigned {default_image} to {pet_name}")
    
    # Save updated mapping
    with open(mapping_path, 'w') as f:
        json.dump(image_mapping, f, indent=2)
    
    print(f"\n✅ Assigned {assigned_count} default images")
    print(f"Total pets with images: {len(image_mapping)}")
    
    return image_mapping

def create_more_default_images():
    """Create additional default images by copying existing ones with different names"""
    
    images_base_path = Path("data/images")
    dogs_dir = images_base_path / "dogs"
    cats_dir = images_base_path / "cats"
    
    # Find existing images to use as templates
    dog_templates = []
    cat_templates = []
    
    if dogs_dir.exists():
        for img_file in dogs_dir.glob("*.jpg"):
            dog_templates.append(img_file)
    
    if cats_dir.exists():
        for img_file in cats_dir.glob("*.jpg"):
            cat_templates.append(img_file)
    
    print(f"Found {len(dog_templates)} dog templates and {len(cat_templates)} cat templates")
    
    # Create additional default images if we have templates but few defaults
    default_count = 0
    
    # Create some additional default dog images
    if len(dog_templates) > 0:
        for i in range(5):  # Create 5 additional default dog images
            template = random.choice(dog_templates)
            default_name = f"default_dog_{i+1}.jpg"
            default_path = dogs_dir / default_name
            
            if not default_path.exists():
                shutil.copy2(template, default_path)
                default_count += 1
                print(f"Created default dog image: {default_name}")
    
    # Create some additional default cat images
    if len(cat_templates) > 0:
        for i in range(5):  # Create 5 additional default cat images
            template = random.choice(cat_templates)
            default_name = f"default_cat_{i+1}.jpg"
            default_path = cats_dir / default_name
            
            if not default_path.exists():
                shutil.copy2(template, default_path)
                default_count += 1
                print(f"Created default cat image: {default_name}")
    
    print(f"Created {default_count} additional default images")

if __name__ == "__main__":
    print("🐾 Assigning default images to pets without photos...")
    
    # First, create some additional default images if needed
    create_more_default_images()
    
    # Then assign default images to pets without photos
    mapping = assign_default_images()
    
    print("\n🎉 Default image assignment complete!")
