#!/usr/bin/env python3

"""
MXC Get
Version: 1.1.0

Primary License:
This project is licensed under the GNU Affero General Public License version 3 or later (AGPL-3+).

Fallback Licenses:
- European Union Public License version 1.2 or later (EUPL-1.2+)
- Open Software License version 3.0 or later (OSL-3+)
- GNU General Public License version 3 or later (GPL-3+)

Conditions for SaaS/Network Use:
If this software is used in SaaS or network-based applications, the terms of AGPL-3+ must be followed, regardless of fallback licensing.

Contact:
Email: drrenardscd@tutanota.de
GitHub: https://github.com/DrRenardScD
"""

import os
import requests
import magic
import json
import uuid
from datetime import datetime

# Load configuration
def load_config(config_file="config.json"):
    with open(config_file, "r") as f:
        return json.load(f)

# Logging function
def log_debug(config, message):
    if config["debug_value"] in ["verbose", "info"]:
        if config["debug_value"] == "verbose":
            print(f"[DEBUG] {message}")
        if config["debug_file"]:
            with open(config["debug_file"], "a") as log_file:
                log_file.write(f"[{datetime.now()}] {message}\n")

# Get file extension from MIME
def get_file_extension_from_mime(mime_type, config):
    return config["mime_types"].get(mime_type, "unknown")

# Determine output filename
def generate_filename(media_id, filename, extension, config):
    naming_scheme = config["output_naming"]
    if naming_scheme == "uuid":
        return f"{uuid.uuid4().hex}.{extension}"
    elif naming_scheme == "media_id":
        return f"{media_id}.{extension}"
    elif naming_scheme == "media_id+filename":
        return f"{media_id}_{filename}.{extension}" if filename else f"{media_id}.{extension}"
    elif naming_scheme == "uuid+filename":
        return f"{uuid.uuid4().hex}_{filename}.{extension}" if filename else f"{uuid.uuid4().hex}.{extension}"
    return f"{media_id}.{extension}"  # Default

# Magic-based MIME detection
def get_file_extension_from_magic(file_path):
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        return mime_type
    except Exception as e:
        return "unknown"

# Download file
def download_file(mxc_url, normal_url, config):
    os.makedirs(config["dl_loc"], exist_ok=True)
    log_debug(config, f"Downloading from: {normal_url}")

    try:
        # Get headers and extension
        response = requests.head(normal_url, timeout=10)
        mime_type = response.headers.get("Content-Type", "unknown")
        extension = get_file_extension_from_mime(mime_type, config)
        media_id = normal_url.split("/")[-1]
        
        # Temp download
        temp_file = os.path.join(config["dl_loc"], f"{media_id}.tmp")
        curl_command = f"curl -o {temp_file} -# {normal_url}"
        wget_command = f"wget -O {temp_file} {normal_url}"
        
        if os.system(curl_command) != 0:
            if os.system(wget_command) != 0:
                log_debug(config, "Failed to download file.")
                return None
        
        # Use magic numbers if MIME is unknown
        if extension == "unknown":
            magic_mime = get_file_extension_from_magic(temp_file)
            extension = get_file_extension_from_mime(magic_mime, config)

        # Determine final filename
        filename = response.headers.get("Content-Disposition", "").split("filename=")[-1].strip('"') or None
        output_file = generate_filename(media_id, filename, extension, config)
        final_path = os.path.join(config["dl_loc"], output_file)
        os.rename(temp_file, final_path)

        # Log result
        log_debug(config, f"Saved as: {final_path}")
        return final_path
    except Exception as e:
        log_debug(config, f"Error during download: {e}")
        return None

# Main logic
def main():
    # Load configuration
    config = load_config()

    while True:
        mxc_url = input("Enter MXC URL (or 'q' to quit): ").strip()
        if mxc_url.lower() in ["q", "quit"]:
            break

        # Convert MXC to HTTP
        if not mxc_url.startswith("mxc://"):
            print("Invalid MXC URL.")
            continue
        normal_url = mxc_url.replace("mxc://", "https://")

        # Download file
        download_file(mxc_url, normal_url, config)

if __name__ == "__main__":
    main()
