import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def syncing():
    print("Syncing local data...")
    # Add your syncing logic here
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Add credentials to the account
    creds = Credentials.from_service_account_file('utils/credentials-gsheet.json', scopes=scope)

    # Authorize the clientsheet 
    client = gspread.authorize(creds)

    # Get the instance of the Spreadsheet
    sheet = client.open('[Price List]KTC Item Database')

    # Get the 2nd DUMMY sheet of the Spreadsheet
    worksheet = sheet.get_worksheet(1)

    # Get all the records of the data
    records = worksheet.get_all_records()

    # Convert the json to dataframe
    try:
        df = pd.DataFrame.from_dict(records)

        all_tags = set()
        if 'Tags' in df.columns:
            # Parsing tags, seperated by commas
            for tags_str in df['Tags'].dropna():
                if isinstance(tags_str, str):
                    tags = [tag.strip() for tag in tags_str.split(',')]
                    all_tags.update(tags)
            
            all_tags = {tag for tag in all_tags if tag}
            sorted_tags = sorted(all_tags)

            with open('utils/unique_tags.txt', 'w') as f:
                for tag in sorted_tags:
                    f.write(f"{tag}\n")

            print(f"Extracted {len(sorted_tags)} unique tags")
        else:
            print("No 'Tags' column found in the data")

    except Exception as e:
        print(f"Sync unsuccessful: {e}")
        return

    # Save the dataframe to excel
    df.to_excel('utils/data.xlsx', index=False)
    
    print("Sync successful")

if __name__ == "__main__":
    syncing()