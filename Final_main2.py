import json
import os
import subprocess
from time import sleep

# Load the JSON file
json_file = "genomic_data_with_did_hash.json"  # Change to your actual file name
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Create a folder for storing JSON files
output_folder = "split_json_files"
os.makedirs(output_folder, exist_ok=True)

# Store output data
output_data = []

for index, entry in enumerate(data):
    try:
        # Extract required fields
        ownerDID = entry.get("Patient DID", "Unknown_DID")
        dataHash = entry.get("SHA-256 Hash", f"hash_{index}")
        sampleID = entry.get("Sample ID", f"Sample_{index}")  # Use Sample ID for filename

        # Create filename based on Sample ID
        file_name = f"{sampleID}.json"
        file_path = os.path.join(output_folder, file_name)

        # Save entry as a separate JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

        # Upload file to local IPFS and get CID
        result = subprocess.run(["ipfs", "add", "-Q", file_path], capture_output=True, text=True)
        cid = result.stdout.strip()

        # Pin the file to prevent garbage collection
        subprocess.run(["ipfs", "pin", "add", cid])

        # Add to IPFS Desktop "Files" tab (MFS)
        subprocess.run(["ipfs", "files", "cp", f"/ipfs/{cid}", f"/{file_name}"])

        # Generate IPFS Link
        ipfsLink = f"https://ipfs.io/ipfs/{cid}"

        # Store final output data
        output_data.append({
            "dataHash": dataHash,
            "ipfsLink": ipfsLink,
            "ownerDID": ownerDID
        })

        print(f"Uploaded {file_name} -> CID: {cid}")

    except Exception as e:
        print(f"Error processing entry {index}: {e}")

    sleep(0.1)  # Small delay to avoid rate limits

# Save the final output JSON file
with open("genomic_output.json", "w", encoding="utf-8") as output_file:
    json.dump(output_data, output_file, indent=2)

print("\n✅ All files uploaded and output.json generated!")
