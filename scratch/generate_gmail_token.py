import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
    if not os.path.exists("credentials.json"):
        print("Error: 'credentials.json' not found in the current directory.")
        print("Please download it from Google Cloud Console (OAuth Client ID -> Desktop App)")
        print("and save it as 'credentials.json' in this folder before running this script.")
        return

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    # Convert credentials to the required JSON format
    creds_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    # Save to a file for backup
    with open("token.json", "w") as token_file:
        json.dump(creds_data, token_file, indent=2)

    print("\n" + "=" * 80)
    print("SUCCESS: Authorized user successfully!")
    print("=" * 80)
    print(
        "\nCopy the single-line JSON string below and paste it as the value for GMAIL_TOKEN_JSON in your Railway environment variables:\n"
    )
    print(json.dumps(creds_data))
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
