import os
import json
import pandas as pd

def convert_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Convertir les données en DataFrame
    df = pd.json_normalize(data)
    
    # Garder uniquement les colonnes timestamp et value
    df = df[['timestamp', 'value']]
    
    if "energy" in csv_file:
        df.rename(columns={"value": "value (Watt)"}, inplace=True)
        
    # Sauvegarder en CSV
    df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python wattmeter_format.py <input_json_file> <output_csv_file>")
        sys.exit(1)

    input_json_file = sys.argv[1]
    output_csv_file = sys.argv[2]
    convert_json_to_csv(input_json_file, output_csv_file)

