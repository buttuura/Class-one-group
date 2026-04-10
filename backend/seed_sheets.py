Perfect! ✅

## File 8: backend/seed_sheets.py

**Path:** `backend/seed_sheets.py`
Action: file_editor view /app/hashtag/backend/seed_sheets.py
Observation: [Showing lines 1-87 of 87 total] /app/hashtag/backend/seed_sheets.py:
1|import gspread
2|from google.oauth2.service_account import Credentials
3|import os
4|from dotenv import load_dotenv
5|from passlib.context import CryptContext
6|import uuid
7|from datetime import datetime
8|
9|load_dotenv()
10|
11|pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
12|
13|# Set up credentials
14|SCOPES = [
15|    'https://www.googleapis.com/auth/spreadsheets',
16|    'https://www.googleapis.com/auth/drive'
17|]
18|
19|creds = Credentials.from_service_account_file(
20|    os.environ['GOOGLE_CREDENTIALS_PATH'],
21|    scopes=SCOPES
22|)
23|
24|client = gspread.authorize(creds)
25|spreadsheet = client.open_by_key(os.environ['SPREADSHEET_ID'])
26|users_sheet = spreadsheet.worksheet('Users')
27|
28|# Check if admin exists
29|all_users = users_sheet.get_all_records()
30|admin_exists = any(user['username'] == 'admin' for user in all_users)
31|
32|if admin_exists:
33|    print("Admin user already exists")
34|else:
35|    # Create admin user
36|    hashed_password = pwd_context.hash("123456")
37|    admin_id = str(uuid.uuid4())
38|    now = datetime.utcnow().isoformat()
39|    
40|    admin_row = [
41|        admin_id,              # id
42|        'admin',               # username
43|        hashed_password,       # passwordHash
44|        'Admin User',          # fullName
45|        '0700000000',         # phoneNumber
46|        'premium',            # memberType
47|        0,                    # accountBalance
48|        0,                    # totalDeposited
49|        'TRUE',               # isAdmin
50|        'TRUE',               # isSuperAdmin
51|        now,                  # createdAt
52|        now                   # updatedAt
53|    ]
54|    
55|    users_sheet.append_row(admin_row)
56|    print("✅ Admin user created successfully!")
57|    print("   Username: admin")
58|    print("   Password: 123456")
59|
60|# Create test user
61|testuser_exists = any(user['username'] == 'testuser' for user in all_users)
62|
63|if not testuser_exists:
64|    hashed_password = pwd_context.hash("test123")
65|    user_id = str(uuid.uuid4())
66|    now = datetime.utcnow().isoformat()
67|    
68|    user_row = [
69|        user_id,
70|        'testuser',
71|        hashed_password,
72|        'Test User',
73|        '0700000001',
74|        'ordinary',
75|        0,
76|        0,
77|        'FALSE',
78|        'FALSE',
79|        now,
80|        now
81|    ]
82|    
83|    users_sheet.append_row(user_row)
84|    print("✅ Test user created successfully!")
85|    print("   Username: testuser")
86|    print("   Password: test123")
87|
[End of file]
