Great! ✅

## File 4: backend/init_sheets.py

**Path:** `backend/init_sheets.py`
Action: file_editor view /app/hashtag/backend/init_sheets.py
Observation: [Showing lines 1-69 of 69 total] /app/hashtag/backend/init_sheets.py:
1|import gspread
2|from google.oauth2.service_account import Credentials
3|import os
4|from dotenv import load_dotenv
5|
6|load_dotenv()
7|
8|# Set up credentials
9|SCOPES = [
10|    'https://www.googleapis.com/auth/spreadsheets',
11|    'https://www.googleapis.com/auth/drive'
12|]
13|
14|creds = Credentials.from_service_account_file(
15|    os.environ['GOOGLE_CREDENTIALS_PATH'],
16|    scopes=SCOPES
17|)
18|
19|# Connect to Google Sheets
20|client = gspread.authorize(creds)
21|spreadsheet_id = os.environ['SPREADSHEET_ID']
22|
23|print(f"Connecting to spreadsheet: {spreadsheet_id}")
24|
25|try:
26|    # Open spreadsheet
27|    spreadsheet = client.open_by_key(spreadsheet_id)
28|    print(f"✅ Successfully connected to: {spreadsheet.title}")
29|    
30|    # Initialize sheets
31|    sheet_names = ['Users', 'Deposits', 'Withdrawals', 'Loans']
32|    
33|    for sheet_name in sheet_names:
34|        try:
35|            sheet = spreadsheet.worksheet(sheet_name)
36|            print(f"✅ Sheet '{sheet_name}' already exists")
37|        except gspread.exceptions.WorksheetNotFound:
38|            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
39|            print(f"✅ Created sheet: {sheet_name}")
40|            
41|            # Add headers
42|            if sheet_name == 'Users':
43|                headers = ['id', 'username', 'passwordHash', 'fullName', 'phoneNumber', 
44|                          'memberType', 'accountBalance', 'totalDeposited', 'isAdmin', 
45|                          'isSuperAdmin', 'createdAt', 'updatedAt']
46|            elif sheet_name == 'Deposits':
47|                headers = ['id', 'userId', 'amount', 'accountNumberUsed', 'operator', 
48|                          'accountName', 'status', 'submittedAt', 'approvedAt', 
49|                          'approvedBy', 'rejectionReason']
50|            elif sheet_name == 'Withdrawals':
51|                headers = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
52|                          'approvedAt', 'approvedBy', 'rejectionReason']
53|            elif sheet_name == 'Loans':
54|                headers = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
55|                          'approvedAt', 'approvedBy', 'rejectionReason', 'amountRepaid']
56|            
57|            sheet.update('A1', [headers])
58|            print(f"   Added headers to {sheet_name}")
59|    
60|    print("\n✅ Google Sheets database initialized successfully!")
61|    print(f"View your database: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
62|    
63|except gspread.exceptions.APIError as e:
64|    print(f"\n❌ API Error: {e}")
65|    print("\nMake sure you've shared the spreadsheet with:")
66|    print("class-one-savings-group@awesome-habitat-374402.iam.gserviceaccount.com")
67|except Exception as e:
68|    print(f"\n❌ Error: {e}")
69|
[End of file]
