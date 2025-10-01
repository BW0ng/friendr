#!/usr/bin/env python3
"""
Script to fix image mapping file extensions to match actual files on disk.
"""

import json
from pathlib import Path
import os

def fix_image_extensions():
    """Fix image mapping file extensions to match actual files"""
    
    mapping_path = Path("data/pet_image_mapping.json")
    images_base_path = Path("data/images")
    
    # Load the mapping
    with open(mapping_path, 'r') as f:
        mapping = json.load(f)
    
    print(f"Loaded {len(mapping)} pets from mapping file")
    
    # Check each entry and fix extensions
    fixed_count = 0
    missing_count = 0
    
    for pet_name, entry in mapping.items():
        pet_type = entry['type']
        current_filename = entry['filename']
        
        # Construct the expected file path
        images_dir = images_base_path / f"{pet_type}s"
        expected_path = images_dir / current_filename
        
        # If the file doesn't exist, try to find it with different extensions
        if not expected_path.exists():
            # Try different extensions
            base_name = expected_path.stem  # filename without extension
            
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                test_path = images_dir / f"{base_name}{ext}"
                if test_path.exists():
                    # Found the file! Update the mapping
                    new_filename = f"{base_name}{ext}"
                    entry['filename'] = new_filename
                    print(f"Fixed {pet_name}: {current_filename} → {new_filename}")
                    fixed_count += 1
                    break
            else:
                print(f"Missing image for {pet_name}: {current_filename}")
                missing_count += 1
        else:
            # File exists as expected
            pass
    
    # Save the updated mapping
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n✅ Fixed {fixed_count} image extensions")
    print(f"⚠️  {missing_count} pets still missing images")
    print(f"📁 Updated mapping file saved")
    
    return mapping

def verify_all_images_exist():
    """Verify that all mapped images actually exist on disk"""
    
    mapping_path = Path("data/pet_image_mapping.json")
    images_base_path = Path("data/images")
    
    with open(mapping_path, 'r') as f:
        mapping = json.load(f)
    
    print(f"\n🔍 Verifying all {len(mapping)} mapped images exist...")
    
    missing_images = []
    for pet_name, entry in mapping.items():
        pet_type = entry['type']
        filename = entry['filename']
        
        image_path = images_base_path / f"{pet_type}s" / filename
        
        if not image_path.exists():
            missing_images.append((pet_name, filename))
    
    if missing_images:
        print(f"❌ {len(missing_images)} images still missing:")
        for pet_name, filename in missing_images[:10]:  # Show first 10
            print(f"  {pet_name}: {filename}")
        if len(missing_images) > 10:
            print(f"  ... and {len(missing_images) - 10} more")
    else:
        print("✅ All mapped images exist on disk!")
    
    return len(missing_images) == 0

if __name__ == "__main__":
    print("🔧 Fixing image mapping file extensions...")
    
    # Fix the extensions
    mapping = fix_image_extensions()
    
    # Verify everything exists
    all_exist = verify_all_images_exist()
    
    if all_exist:
        print("\n🎉 All image mapping issues resolved!")
    else:
        print("\n⚠️  Some images still missing - may need additional default image assignment")
