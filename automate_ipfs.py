import json
import os
import time
import requests

# Infura API credentials
PROJECT_ID = ""
PROJECT_SECRET = ""
INFURA_API = "https://ipfs.infura.io:5001/api/v0/add"

# Headers for authentication
auth = (PROJECT_ID, PROJECT_SECRET)

# Load JSON file
json_file = "samplejson.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Output data list
output_data = []

# Create a folder for storing temporary JSON files
output_folder = "split_json_files"
os.makedirs(output_folder, exist_ok=True)

# Upload each entry to IPFS
for index, entry in enumerate(data):
    try:
        # Extract necessary fields
        data_hash = entry.get("SHA-256 Hash", "unknown")
        owner_did = entry.get("Patient DID", "unknown")

        # Generate a filename
        file_name = f"file_{index}.json"
        file_path = os.path.join(output_folder, file_name)

        # Save entry as a separate JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

        # Upload file to Infura IPFS
        retries = 3
        for attempt in range(retries):
            try:
                with open(file_path, "rb") as f:
                    response = requests.post(INFURA_API, files={"file": f}, auth=auth)

                if response.status_code == 200:
                    cid = response.json()["Hash"]
                    ipfs_link = f"https://ipfs.io/ipfs/{cid}"

                    # Store result
                    output_data.append({
                        "dataHash": data_hash,
                        "ipfsLink": ipfs_link,
                        "ownerDID": owner_did
                    })

                    print(f"Uploaded {file_name} -> {ipfs_link}")
                    break  # Exit retry loop if successful
                else:
                    print(f"Attempt {attempt + 1} failed: {response.status_code} {response.text}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

        # Rate limit handling: Pause after every 50 uploads
        if (index + 1) % 50 == 0:
            print("Rate limit control: Pausing for 10 seconds...")
            time.sleep(10)

    except Exception as e:
        print(f"Error processing entry {index}: {e}")

# Save the final output JSON
output_file = "uploaded_cids.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

print("\n✅ All files uploaded! Results saved in 'uploaded_cids.json'.")
