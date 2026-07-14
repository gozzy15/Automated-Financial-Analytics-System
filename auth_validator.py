#!/usr/bin/env python3
"""Simple utility for testing Google Drive authentication."""

from cloud_manager import GoogleDriveHandler

def main():
    print("Testing Google Drive Authentication...")
    try:
        gdrive = GoogleDriveHandler()
        print("✅ Authentication successful!")
        
        # List files
        files = gdrive.list_files()
        for file in files[:5]:
            print(f" - {file['name']}")
        print(f"Found {len(files)} files in Drive")
        
    except Exception as exc:
        print(f"❌ Authentication failed: {exc}")

if __name__ == "__main__":
    main()