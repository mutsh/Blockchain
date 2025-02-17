import json
import os
import requests
from time import sleep

# Pinata API credentials (Replace with your keys)
PINATA_API_KEY = ""
PINATA_SECRET_API_KEY = ""

# Load JSON file
json_file = "genomic_data_with_did_hash.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Create a folder for storing JSON files
output_folder = "split_json_files"
os.makedirs(output_folder, exist_ok=True)

# Store CIDs in the required format
uploaded_data = []

def upload_to_pinata(file_path, file_name):
    """Uploads file to Pinata and returns CID."""
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    with open(file_path, "rb") as file:
        response = requests.post(url, headers=headers, files={"file": (file_name, file)})
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            print(f"Error uploading {file_name}: {response.text}")
            return None

# Process each entry in JSON file
for index, entry in enumerate(data):
    try:
        # Extract fields
        sample_id = entry.get("Sample ID", f"Sample_{index}")  # Fallback name
        data_hash = entry.get("SHA-256 Hash", "")
        owner_did = entry.get("Patient DID", "")

        # Create filename
        file_name = f"{sample_id}.json"
        file_path = os.path.join(output_folder, file_name)

        # Save entry as a separate JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

        # Upload to Pinata and get CID
        cid = upload_to_pinata(file_path, file_name)
        if cid:
            ipfs_link = f"https://ipfs.io/ipfs/{cid}"
            uploaded_data.append({
                "dataHash": data_hash,
                "ipfsLink": ipfs_link,
                "ownerDID": owner_did
            })
            print(f"Uploaded {file_name} -> CID: {cid}")

    except Exception as e:
        print(f"Error processing entry {index}: {e}")

    sleep(0.1)  # Small delay to avoid rate limits

# Save final output
with open("uploaded_cids.json", "w", encoding="utf-8") as cid_file:
    json.dump(uploaded_data, cid_file, indent=2)

print("\nAll files uploaded to Pinata, structured data saved in uploaded_cids.json")
