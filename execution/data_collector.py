import json
import os
import argparse
from typing import Dict, Any

def read_file(filepath: str) -> str:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return ""

def scan_markdown_files(directory: str) -> Dict[str, str]:
    """Recursively scans a directory for .md files and returns {relative_path: content}."""
    files = {}
    if not os.path.exists(directory):
        return files
    for root, _, filenames in os.walk(directory):
        for fname in filenames:
            if fname.endswith(".md"):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, directory)
                content = read_file(full_path)
                if content:
                    files[rel_path] = content
    return files


def collect_data(client_dir: str) -> Dict[str, Any]:
    """
    Collects data from the standard client folder structure.
    """
    data_package = {
        "client_profile": {},
        "questionnaire_data": {},
        "meeting_transcripts": {},
        "process_documentation": {},
        "raw_files": {}
    }

    # Read client profile
    profile_path = os.path.join(client_dir, "Client Context/Client_Profile.md")
    content = read_file(profile_path)
    if content:
        data_package["raw_files"]["profile"] = content
        data_package["profile_content"] = content
    else:
        print(f"Warning: File not found: {profile_path}")

    # Read questionnaire
    questionnaire_path = os.path.join(client_dir, "Process Documentation/Onboarding Responses/Pre-Discovery Questionnaire.md")
    content = read_file(questionnaire_path)
    if content:
        data_package["raw_files"]["questionnaire"] = content
        data_package["questionnaire_content"] = content
    else:
        print(f"Warning: File not found: {questionnaire_path}")

    # Scan all meeting transcripts
    transcripts_dir = os.path.join(client_dir, "Meeting Transcripts")
    data_package["meeting_transcripts"] = scan_markdown_files(transcripts_dir)
    for key, content in data_package["meeting_transcripts"].items():
        data_package["raw_files"][f"transcript:{key}"] = content

    # Scan all process documentation
    docs_dir = os.path.join(client_dir, "Process Documentation")
    data_package["process_documentation"] = scan_markdown_files(docs_dir)
    for key, content in data_package["process_documentation"].items():
        data_package["raw_files"][f"doc:{key}"] = content

    return data_package


def save_to_tmp(data: Dict[str, Any], client_dir: str, filename: str = "data_package.json"):
    tmp_dir = os.path.join(client_dir, ".tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    with open(os.path.join(tmp_dir, filename), "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {filename} to {tmp_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Audit Data Collector")
    parser.add_argument("--client-dir", help="Path to the client's root directory")

    args = parser.parse_args()

    if args.client_dir:
        package = collect_data(args.client_dir)
        save_to_tmp(package, args.client_dir)
    else:
        print("Please provide --client-dir argument.")
