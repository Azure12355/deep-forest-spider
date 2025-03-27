import json
import csv
import os
from uuid import UUID

# Define input and output directories
INPUT_DIR = 'data/pest_host_part_list'
OUTPUT_DIR = 'cleaned_data/pest_host_part'
JSON_FILE = os.path.join(INPUT_DIR, 'pest_host_part_batch_1.json')
SPECIES_CSV = os.path.join(OUTPUT_DIR, 'species_host_part.csv')
REFERENCE_CSV = os.path.join(OUTPUT_DIR, 'reference_relation.csv')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def validate_uuid(uuid_str):
    """Validate if a string is a valid UUID."""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def clean_data():
    """Main function to clean pest_host_part data and write to CSV files."""
    # Read JSON file
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Lists to store cleaned data for each table
    species_host_part_rows = []
    reference_relation_rows = []

    # Process each record in the JSON data
    for record in data:
        # Extract and validate species_guid
        species_guid = record.get('species_id', '')
        if not validate_uuid(species_guid):
            print(f"Warning: Invalid UUID '{species_guid}' in record rowid {record.get('rowid', 'unknown')}. Skipping.")
            continue

        # Map fields to species_host_part table
        species_host_part_row = {
            'species_guid': species_guid,
            'plant_parts': record.get('PlantParts', ''),  # Required field, default to empty string if missing
            'pest_stage': record.get('Peststage', ''),    # Optional field
            'visibility_type': record.get('VisibilityType', ''),  # Optional field
            'spreading_way': record.get('SpreadingWay', '')  # Optional field
        }

        # Ensure plant_parts is not empty as it’s NOT NULL in the database
        if not species_host_part_row['plant_parts']:
            print(f"Warning: Missing 'PlantParts' in record rowid {record.get('rowid', 'unknown')}. Skipping.")
            continue

        species_host_part_rows.append(species_host_part_row)

        # Process Icodes for reference_relation table
        icodes = record.get('Icodes', [])
        for icode in icodes:
            icode_id = icode.get('ICodeID', '')
            # Validate icode is an integer
            try:
                int(icode_id)
            except (ValueError, TypeError):
                print(f"Warning: Invalid ICodeID '{icode_id}' in record rowid {record.get('rowid', 'unknown')}. Skipping reference.")
                continue

            reference_relation_row = {
                'species_guid': species_guid,
                'icode': icode_id,
                'author_display': icode.get('AuthorDisplay', ''),  # Optional field
                'title': None  # Title not provided in JSON, set to None
            }
            reference_relation_rows.append(reference_relation_row)

    # Write to species_host_part CSV
    species_fieldnames = ['species_guid', 'plant_parts', 'pest_stage', 'visibility_type', 'spreading_way']
    with open(SPECIES_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=species_fieldnames)
        writer.writeheader()
        writer.writerows(species_host_part_rows)

    # Write to reference_relation CSV
    reference_fieldnames = ['species_guid', 'icode', 'author_display', 'title']
    with open(REFERENCE_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reference_fieldnames)
        writer.writeheader()
        writer.writerows(reference_relation_rows)

    print(f"Data cleaning completed. Files written: {SPECIES_CSV}, {REFERENCE_CSV}")
    print(f"Processed {len(species_host_part_rows)} species_host_part records and {len(reference_relation_rows)} reference_relation records.")

def main():
    """Entry point for the script."""
    print(f"Starting data cleaning for {JSON_FILE}")
    clean_data()

if __name__ == "__main__":
    main()