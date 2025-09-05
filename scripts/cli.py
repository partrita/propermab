#!/usr/bin/env python3
"""
Propermab CLI - Antibody Feature Calculation from FASTA sequences

Usage:
    python cli.py --heavy heavy_chain.fasta --light light_chain.fasta --output results.csv [--name antibody_name]

Example:
    python cli.py --heavy HC.fasta --light LC.fasta --output pembrolizumab_results.csv --name pembrolizumab
"""

import os
import sys
import time
import csv
import argparse


def parse_fasta(fasta_file):
    """Parse a FASTA file and return the first sequence."""
    if not os.path.exists(fasta_file):
        raise FileNotFoundError(f"FASTA file not found: {fasta_file}")

    sequence = ""
    with open(fasta_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                # Header line, skip
                continue
            else:
                # Sequence line
                sequence += line.replace(" ", "").replace("\n", "").upper()

    if not sequence:
        raise ValueError(f"No sequence found in FASTA file: {fasta_file}")

    return sequence


def detect_environment():
    """Detect if running in Docker container or locally."""
    if os.path.exists("/app/default_config.json"):
        # Running in Docker container
        return {
            "is_docker": True,
            "config_path": "/app/default_config.json",
            "output_base": "/mnt/host",
        }
    else:
        # Running locally
        return {
            "is_docker": False,
            "config_path": "default_config.json",
            "output_base": ".",
        }


def process_antibody(
    heavy_seq,
    light_seq,
    antibody_name,
    temp_dir,
    env,
    heavy_chain_file=None,
    light_chain_file=None,
):
    """Process a single antibody: calculate features and return results."""
    try:
        print(f"\nProcessing antibody: {antibody_name}...")
        print(f"  - Heavy chain length: {len(heavy_seq)} residues")
        print(f"  - Light chain length: {len(light_seq)} residues")

        # Start feature calculation
        print(f"\nCalculating features for {antibody_name}...")
        start_time = time.time()

        from propermab.features import feature_utils

        mol_features_dict = feature_utils.get_all_mol_features(
            heavy_seq=heavy_seq, light_seq=light_seq, tmp_dir=temp_dir
        )

        # Flatten the dictionary of lists into a dictionary of single values
        mol_features = {k: v[0] for k, v in mol_features_dict.items()}

        end_time = time.time()
        calculation_time = end_time - start_time

        print(
            f"✓ Feature calculation for {antibody_name} completed in {calculation_time:.2f} seconds."
        )

        # Prepare results
        results = {
            "antibody_name": antibody_name,
            "heavy_chain_length": len(heavy_seq),
            "light_chain_length": len(light_seq),
            "total_residues": len(heavy_seq) + len(light_seq),
            "heavy_chain_file": heavy_chain_file if heavy_chain_file else "N/A",
            "light_chain_file": light_chain_file if light_chain_file else "N/A",
            "calculation_time_seconds": calculation_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }
        results.update(mol_features)

        return results

    except Exception as e:
        print(f"\n✗ ERROR processing {antibody_name}: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Calculate molecular features for antibodies from FASTA sequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage for a single antibody
  python scripts/cli.py --heavy examples/pembrolizumab_heavy.fasta --light examples/pembrolizumab_light.fasta --output results.csv --name pembrolizumab

  # Batch processing from a CSV file
  python scripts/cli.py --input-csv antibodies.csv --output results.csv

        """,
    )

    # Arguments for single antibody
    parser.add_argument("--heavy", "-H", help="Path to heavy chain FASTA file")
    parser.add_argument("--light", "-L", help="Path to light chain FASTA file")
    parser.add_argument("--name", "-n", help="Antibody name")

    # Argument for batch processing
    parser.add_argument("--input-csv", help="Path to a CSV file for batch processing")

    # Common arguments
    parser.add_argument("--output", "-o", required=True, help="Output CSV file path")
    parser.add_argument(
        "--temp-dir", default=None, help="Directory for temporary files"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.input_csv:
        if args.heavy or args.light or args.name:
            parser.error("--input-csv cannot be used with --heavy, --light, or --name")
    elif not (args.heavy and args.light):
        parser.error("Either --input-csv or both --heavy and --light are required")

    print("=" * 70)
    print("PROPERMAB CLI - Antibody Feature Calculation")
    print("=" * 70)

    try:
        # Detect environment
        env = detect_environment()
        print(f"✓ Environment: {'Docker container' if env['is_docker'] else 'Local'}")

        # Set up temporary directory
        if args.temp_dir:
            temp_dir = args.temp_dir
        elif env["is_docker"]:
            temp_dir = "/tmp"
        else:
            temp_dir = "temp"

        os.makedirs(temp_dir, exist_ok=True)
        print(f"✓ Temporary directory: {temp_dir}")

        # Load propermab modules and configuration
        print("\nLoading propermab modules and configuration...")
        from propermab import defaults

        defaults.system_config.update_from_json(env["config_path"])
        print("✓ Propermab modules and configuration loaded.")

        # Verify external dependencies
        print("\nVerifying external dependencies...")
        # ... (dependency verification logic remains the same)

        all_results = []

        if args.input_csv:
            # Batch processing from CSV
            print(f"\nBatch processing from: {args.input_csv}")
            with open(args.input_csv, "r") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    antibody_name = row.get("antibody_name", "antibody")

                    if (
                        "heavy_chain_sequence" in fieldnames
                        and "light_chain_sequence" in fieldnames
                    ):
                        heavy_seq = row.get("heavy_chain_sequence")
                        light_seq = row.get("light_chain_sequence")
                        result = process_antibody(
                            heavy_seq, light_seq, antibody_name, temp_dir, env
                        )
                    elif (
                        "heavy_chain_fasta" in fieldnames
                        and "light_chain_fasta" in fieldnames
                    ):
                        heavy_fasta = row.get("heavy_chain_fasta")
                        light_fasta = row.get("light_chain_fasta")
                        heavy_seq = parse_fasta(heavy_fasta)
                        light_seq = parse_fasta(light_fasta)
                        result = process_antibody(
                            heavy_seq,
                            light_seq,
                            antibody_name,
                            temp_dir,
                            env,
                            heavy_chain_file=heavy_fasta,
                            light_chain_file=light_fasta,
                        )
                    else:
                        print(
                            "✗ Skipping row: CSV must contain either 'heavy_chain_fasta' and 'light_chain_fasta' columns, or 'heavy_chain_sequence' and 'light_chain_sequence' columns."
                        )
                        continue

                    if result:
                        all_results.append(result)
        else:
            # Single antibody processing
            antibody_name = args.name if args.name else "antibody"
            heavy_seq = parse_fasta(args.heavy)
            light_seq = parse_fasta(args.light)
            result = process_antibody(
                heavy_seq,
                light_seq,
                antibody_name,
                temp_dir,
                env,
                heavy_chain_file=args.heavy,
                light_chain_file=args.light,
            )
            if result:
                all_results.append(result)

        if not all_results:
            print("\nNo antibodies were processed successfully.")
            return 1

        # Save all results to a single CSV file
        print(f"\nSaving all results to {args.output}...")

        # Get all unique field names from all results
        fieldnames = set()
        for res in all_results:
            fieldnames.update(res.keys())

        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(list(fieldnames)))
            writer.writeheader()
            writer.writerows(all_results)

        print(f"✓ All results saved to: {args.output}")

        print("\n" + "=" * 70)
        print("ALL ANTIBODY PROCESSING COMPLETED")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
