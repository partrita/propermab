#!/usr/bin/env python3
"""
Propermab calculation script for pembrolizumab
Usage: python pembrolizumab.py
"""

import os
import sys
import time
import csv
from pathlib import Path

def main():
    print("=" * 60)
    print("PROPERMAB - Pembrolizumab Feature Calculation")
    print("=" * 60)
    
    try:
        # Import propermab modules
        print("Loading propermab modules...")
        from propermab import defaults
        from propermab.features import feature_utils
        print("✓ Propermab modules loaded successfully")
        
        # Detect environment and set paths
        if os.path.exists('/app/default_config.json'):
            # Running in Docker container
            config_path = '/app/default_config.json'
            pdb_path = '/mnt/host/tests/pembrolizumab_ib.pdb'
            output_dir = '/mnt/host/output'
            print("✓ Running in Docker container")
        else:
            # Running locally
            config_path = '../default_config.json'
            pdb_path = '../tests/pembrolizumab_ib.pdb'
            output_dir = '../output'
            print("✓ Running in local environment")
        
        print(f"✓ Config path: {config_path}")
        print(f"✓ PDB path: {pdb_path}")
        print(f"✓ Output directory: {output_dir}")
        
        # Check if files exist
        if not os.path.exists(config_path):
            print(f"✗ ERROR: Configuration file not found: {config_path}")
            return 1
            
        if not os.path.exists(pdb_path):
            print(f"✗ ERROR: PDB file not found: {pdb_path}")
            return 1
        
        # Load configuration
        print("\nLoading configuration...")
        defaults.system_config.update_from_json(config_path)
        print("✓ Configuration loaded successfully")
        
        # Verify external dependencies
        print("\nVerifying external dependencies...")
        dependencies = {
            'NanoShaper': defaults.system_config.config.get('nanoshaper_binary_path'),
            'APBS': defaults.system_config.config.get('apbs_binary_path'),
            'Multivalue': defaults.system_config.config.get('multivalue_binary_path'),
            'Amber file': defaults.system_config.config.get('atom_radii_file')
        }
        
        all_deps_ok = True
        for name, path in dependencies.items():
            if path and os.path.exists(path):
                print(f"✓ {name}: {path}")
            else:
                print(f"✗ {name}: {path} (NOT FOUND)")
                if name == 'Amber file':  # Amber file is critical
                    all_deps_ok = False
        
        if not all_deps_ok:
            print("\n✗ ERROR: Critical dependencies missing!")
            return 1
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Output directory created: {output_dir}")
        
        # Start feature calculation
        print("\n" + "=" * 60)
        print("STARTING FEATURE CALCULATION")
        print("=" * 60)
        print(f"Processing: {os.path.basename(pdb_path)}")
        
        start_time = time.time()
        
        # Calculate molecular features
        print("Calculating molecular features...")
        mol_features = feature_utils.calculate_features_from_pdb(pdb_path)
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        print("✓ Feature calculation completed successfully!")
        print(f"✓ Total features calculated: {len(mol_features)}")
        print(f"✓ Calculation time: {calculation_time:.2f} seconds")
        
        # Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print("\nCalculated features:")
        for i, (feature_name, value) in enumerate(mol_features.items(), 1):
            print(f"{i:2d}. {feature_name}: {value}")
        
        # Save results to CSV file
        output_file = os.path.join(output_dir, 'pembrolizumab_features.csv')
        
        # Prepare results for CSV
        csv_row = {
            'protein': 'pembrolizumab',
            'pdb_file': pdb_path,
            'calculation_time_seconds': calculation_time,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            'total_features': len(mol_features)
        }
        
        # Add all molecular features to the row
        csv_row.update(mol_features)
        
        # Write to CSV file
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_row.keys())
            writer.writeheader()
            writer.writerow(csv_row)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        print("\n" + "=" * 60)
        print("CALCULATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
