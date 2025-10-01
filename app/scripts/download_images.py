#!/usr/bin/env python3
"""
Script to download images from the ShelterLuv CSV data and organize them
into the existing image directory structure.
"""

import pandas as pd
import requests
import os
from pathlib import Path
from urllib.parse import urlparse
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_image(url, save_path, max_retries=3):
    """Download an image from URL with retry logic"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the image
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {save_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to download {url} after {max_retries} attempts")
                return False
    
    return False

def main():
    # Paths
    csv_path = Path("data/friends4life_shelterluv_animals.csv")
    images_base_path = Path("data/images")
    
    # Create image directories
    cats_dir = images_base_path / "cats"
    dogs_dir = images_base_path / "dogs"
    cats_dir.mkdir(parents=True, exist_ok=True)
    dogs_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the CSV
    df = pd.read_csv(csv_path)
    
    # Filter out rows with missing species or image_url
    df = df.dropna(subset=['species', 'image_url'])
    
    # Convert species to lowercase for consistency
    df['type'] = df['species'].str.lower()
    
    # Filter for only dogs and cats
    df = df[df['type'].isin(['dog', 'cat'])]
    
    logger.info(f"Found {len(df)} pets with images to download")
    logger.info(f"Dogs: {len(df[df['type'] == 'dog'])}, Cats: {len(df[df['type'] == 'cat'])}")
    
    downloaded_count = 0
    failed_count = 0
    
    for idx, row in df.iterrows():
        pet_type = row['type']
        pet_name = row['name']
        image_url = row['image_url']
        
        # Skip default placeholder images
        if 'default_cat.png' in image_url or 'default_dog.png' in image_url:
            logger.info(f"Skipping default image for {pet_name}")
            continue
        
        # Determine save directory and filename
        if pet_type == 'dog':
            save_dir = dogs_dir
            prefix = 'dog'
        else:
            save_dir = cats_dir
            prefix = 'cat'
        
        # Generate filename from URL or use pet name
        try:
            parsed_url = urlparse(image_url)
            file_extension = os.path.splitext(parsed_url.path)[1]
            if not file_extension:
                file_extension = '.jpg'  # Default to jpg
            
            # Use a combination of name and index for unique filenames
            safe_name = "".join(c for c in pet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{prefix}_{idx}_{safe_name}{file_extension}"
            
            save_path = save_dir / filename
            
            # Download the image
            if download_image(image_url, save_path):
                downloaded_count += 1
            else:
                failed_count += 1
            
            # Be respectful to the server
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error processing {pet_name}: {e}")
            failed_count += 1
    
    logger.info(f"Download complete! Downloaded: {downloaded_count}, Failed: {failed_count}")
    
    # Create a mapping file for the backend
    create_image_mapping(df)

def create_image_mapping(df):
    """Create a mapping file for the backend to use"""
    mapping = {}
    
    for idx, row in df.iterrows():
        pet_type = row['type']
        pet_name = row['name']
        
        # Skip default images
        if 'default_cat.png' in row['image_url'] or 'default_dog.png' in row['image_url']:
            continue
        
        if pet_type == 'dog':
            prefix = 'dog'
        else:
            prefix = 'cat'
        
        # Generate the same filename as in download
        safe_name = "".join(c for c in pet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{prefix}_{idx}_{safe_name}.jpg"  # Assume jpg for mapping
        
        mapping[pet_name] = {
            'type': pet_type,
            'filename': filename,
            'original_url': row['image_url']
        }
    
    # Save mapping as JSON
    import json
    mapping_path = Path("data/pet_image_mapping.json")
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    logger.info(f"Created image mapping file: {mapping_path}")

if __name__ == "__main__":
    main()
