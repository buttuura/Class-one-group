Perfect! ✅ (.env files are usually not in git repos, that's correct)

## File 3: backend/sheets_db.py

**Path:** `backend/sheets_db.py`

This file is about 528 lines. I'll give it to you in full:
Action: file_editor view /app/hashtag/backend/sheets_db.py
Observation: [Showing lines 1-528 of 528 total] /app/hashtag/backend/sheets_db.py:
1|import gspread
2|from google.oauth2.service_account import Credentials
3|import os
4|import json
5|from dotenv import load_dotenv
6|import uuid
7|from datetime import datetime
8|from typing import Optional, List, Dict
9|import time
10|import threading
11|import logging
12|
13|load_dotenv()
14|
15|logger = logging.getLogger(__name__)
16|
17|# Set up credentials
18|SCOPES = [
19|    'https://www.googleapis.com/auth/spreadsheets',
20|    'https://www.googleapis.com/auth/drive'
21|]
22|
23|# Support both file-based and environment variable-based credentials
24|google_creds_path = os.environ.get('GOOGLE_CREDENTIALS_PATH', '')
25|google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
26|
27|if google_creds_json:
28|    # Load from environment variable (for Render/cloud deployment)
29|    creds_info = json.loads(google_creds_json)
30|    # Fix private key newlines that may get lost in env vars
31|    if 'private_key' in creds_info:
32|        creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')
33|    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
34|elif google_creds_path and os.path.exists(google_creds_path):
35|    # Load from file (for local development)
36|    creds = Credentials.from_service_account_file(google_creds_path, scopes=SCOPES)
37|else:
38|    raise Exception("No Google credentials found. Set GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_PATH")
39|
40|client = gspread.authorize(creds)
41|spreadsheet = client.open_by_key(os.environ['SPREADSHEET_ID'])
42|
43|# Get worksheets
44|users_sheet = spreadsheet.worksheet('Users')
45|deposits_sheet = spreadsheet.worksheet('Deposits')
46|withdrawals_sheet = spreadsheet.worksheet('Withdrawals')
47|loans_sheet = spreadsheet.worksheet('Loans')
48|
49|# ===== CACHE SYSTEM =====
50|# Cache Google Sheets data in memory to avoid hitting API rate limits (60 reads/min)
51|CACHE_TTL = 30  # seconds
52|_cache = {}
53|_cache_lock = threading.Lock()
54|
55|def _get_cached(sheet_name: str, sheet_obj):
56|    """Get sheet data from cache or fetch from Google Sheets"""
57|    with _cache_lock:
58|        cached = _cache.get(sheet_name)
59|        if cached and (time.time() - cached['time']) < CACHE_TTL:
60|            return cached['data']
61|    
62|    # Fetch from Google Sheets with retry
63|    for attempt in range(3):
64|        try:
65|            data = sheet_obj.get_all_records()
66|            with _cache_lock:
67|                _cache[sheet_name] = {'data': data, 'time': time.time()}
68|            return data
69|        except gspread.exceptions.APIError as e:
70|            if '429' in str(e) and attempt < 2:
71|                logger.warning(f"Rate limited on {sheet_name}, retrying in {2 ** attempt}s...")
72|                time.sleep(2 ** attempt)
73|            else:
74|                raise
75|    return []
76|
77|def _invalidate_cache(sheet_name: str):
78|    """Clear cache for a specific sheet after writes"""
79|    with _cache_lock:
80|        _cache.pop(sheet_name, None)
81|
82|def dict_to_row(data: dict, columns: list) -> list:
83|    """Convert dictionary to row based on column order"""
84|    return [data.get(col, '') for col in columns]
85|
86|def row_to_dict(row: list, columns: list) -> dict:
87|    """Convert row to dictionary based on column headers"""
88|    return {columns[i]: row[i] if i < len(row) else '' for i in range(len(columns))}
89|
90|def normalize_bool(value) -> bool:
91|    """Convert Google Sheets boolean strings to actual Python booleans"""
92|    if isinstance(value, bool):
93|        return value
94|    if isinstance(value, str):
95|        return value.upper() == 'TRUE'
96|    return bool(value)
97|
98|def normalize_user(user: dict) -> dict:
99|    """Normalize boolean fields in user data from Google Sheets"""
100|    user['isAdmin'] = normalize_bool(user.get('isAdmin', False))
101|    user['isSuperAdmin'] = normalize_bool(user.get('isSuperAdmin', False))
102|    user['accountBalance'] = float(user.get('accountBalance', 0))
103|    user['totalDeposited'] = float(user.get('totalDeposited', 0))
104|    return user
105|
106|# ===== USERS OPERATIONS =====
107|
108|def create_user(user_data: dict) -> dict:
109|    """Create a new user"""
110|    user_id = str(uuid.uuid4())
111|    now = datetime.utcnow().isoformat()
112|    
113|    user_data['id'] = user_id
114|    user_data['createdAt'] = now
115|    user_data['updatedAt'] = now
116|    
117|    columns = ['id', 'username', 'passwordHash', 'fullName', 'phoneNumber', 
118|               'memberType', 'accountBalance', 'totalDeposited', 'isAdmin', 
119|               'isSuperAdmin', 'createdAt', 'updatedAt']
120|    
121|    row = dict_to_row(user_data, columns)
122|    users_sheet.append_row(row)
123|    _invalidate_cache('users')
124|    
125|    return user_data
126|
127|def find_user_by_username(username: str) -> Optional[dict]:
128|    """Find user by username"""
129|    all_users = _get_cached('users', users_sheet)
130|    for user in all_users:
131|        if user['username'] == username:
132|            return normalize_user(dict(user))
133|    return None
134|
135|def find_user_by_id(user_id: str) -> Optional[dict]:
136|    """Find user by ID"""
137|    all_users = _get_cached('users', users_sheet)
138|    for user in all_users:
139|        if user['id'] == user_id:
140|            return normalize_user(dict(user))
141|    return None
142|
143|def update_user(user_id: str, update_data: dict) -> bool:
144|    """Update user by ID"""
145|    all_records = _get_cached('users', users_sheet)
146|    for idx, user in enumerate(all_records):
147|        if user['id'] == user_id:
148|            row_num = idx + 2  # +2 because of header and 0-index
149|            
150|            # Get current user data and update
151|            user = dict(user)
152|            for key, value in update_data.items():
153|                user[key] = value
154|            user['updatedAt'] = datetime.utcnow().isoformat()
155|            
156|            columns = ['id', 'username', 'passwordHash', 'fullName', 'phoneNumber', 
157|                      'memberType', 'accountBalance', 'totalDeposited', 'isAdmin', 
158|                      'isSuperAdmin', 'createdAt', 'updatedAt']
159|            
160|            row = dict_to_row(user, columns)
161|            users_sheet.update(f'A{row_num}:L{row_num}', [row])
162|            _invalidate_cache('users')
163|            return True
164|    return False
165|
166|def get_all_users() -> List[dict]:
167|    """Get all users"""
168|    users = _get_cached('users', users_sheet)
169|    return [normalize_user(dict(u)) for u in users]
170|
171|def delete_user(user_id: str) -> bool:
172|    """Delete user by ID"""
173|    all_records = _get_cached('users', users_sheet)
174|    for idx, user in enumerate(all_records):
175|        if user['id'] == user_id:
176|            row_num = idx + 2
177|            users_sheet.delete_rows(row_num)
178|            _invalidate_cache('users')
179|            return True
180|    return False
181|
182|def count_users(filter_dict: dict = None) -> int:
183|    """Count users with optional filter"""
184|    all_users = _get_cached('users', users_sheet)
185|    if not filter_dict:
186|        return len(all_users)
187|    
188|    count = 0
189|    for user in all_users:
190|        user = normalize_user(user)
191|        match = True
192|        for key, value in filter_dict.items():
193|            if user.get(key) != value:
194|                match = False
195|                break
196|        if match:
197|            count += 1
198|    return count
199|
200|# ===== DEPOSITS OPERATIONS =====
201|
202|def create_deposit(deposit_data: dict) -> dict:
203|    """Create a new deposit"""
204|    deposit_id = str(uuid.uuid4())
205|    now = datetime.utcnow().isoformat()
206|    
207|    deposit_data['id'] = deposit_id
208|    deposit_data['submittedAt'] = now
209|    
210|    columns = ['id', 'userId', 'amount', 'accountNumberUsed', 'operator', 
211|               'accountName', 'status', 'submittedAt', 'approvedAt', 
212|               'approvedBy', 'rejectionReason']
213|    
214|    row = dict_to_row(deposit_data, columns)
215|    deposits_sheet.append_row(row)
216|    _invalidate_cache('deposits')
217|    
218|    return deposit_data
219|
220|def find_deposits(filter_dict: dict = None) -> List[dict]:
221|    """Find deposits with optional filter"""
222|    all_deposits = _get_cached('deposits', deposits_sheet)
223|    
224|    if not filter_dict:
225|        return all_deposits
226|    
227|    filtered = []
228|    for deposit in all_deposits:
229|        match = True
230|        for key, value in filter_dict.items():
231|            if deposit.get(key) != value:
232|                match = False
233|                break
234|        if match:
235|            filtered.append(deposit)
236|    
237|    return filtered
238|
239|def find_deposit_by_id(deposit_id: str) -> Optional[dict]:
240|    """Find deposit by ID"""
241|    all_deposits = _get_cached('deposits', deposits_sheet)
242|    for deposit in all_deposits:
243|        if deposit['id'] == deposit_id:
244|            return deposit
245|    return None
246|
247|def update_deposit(deposit_id: str, update_data: dict) -> bool:
248|    """Update deposit by ID"""
249|    all_records = _get_cached('deposits', deposits_sheet)
250|    for idx, deposit in enumerate(all_records):
251|        if deposit['id'] == deposit_id:
252|            row_num = idx + 2
253|            
254|            deposit = dict(deposit)
255|            for key, value in update_data.items():
256|                deposit[key] = value
257|            
258|            columns = ['id', 'userId', 'amount', 'accountNumberUsed', 'operator', 
259|                      'accountName', 'status', 'submittedAt', 'approvedAt', 
260|                      'approvedBy', 'rejectionReason']
261|            
262|            row = dict_to_row(deposit, columns)
263|            deposits_sheet.update(f'A{row_num}:K{row_num}', [row])
264|            _invalidate_cache('deposits')
265|            return True
266|    return False
267|
268|def delete_deposits_by_user(user_id: str) -> int:
269|    """Delete all deposits for a user"""
270|    all_records = _get_cached('deposits', deposits_sheet)
271|    rows_to_delete = []
272|    
273|    for idx, deposit in enumerate(all_records):
274|        if deposit['userId'] == user_id:
275|            rows_to_delete.append(idx + 2)
276|    
277|    for row_num in reversed(rows_to_delete):
278|        deposits_sheet.delete_rows(row_num)
279|    
280|    _invalidate_cache('deposits')
281|    return len(rows_to_delete)
282|
283|def count_deposits(filter_dict: dict = None) -> int:
284|    """Count deposits with optional filter"""
285|    deposits = find_deposits(filter_dict)
286|    return len(deposits)
287|
288|def sum_deposits(filter_dict: dict) -> float:
289|    """Sum deposit amounts with filter"""
290|    deposits = find_deposits(filter_dict)
291|    total = sum(float(d.get('amount', 0)) for d in deposits)
292|    return total
293|
294|# ===== WITHDRAWALS OPERATIONS =====
295|
296|def create_withdrawal(withdrawal_data: dict) -> dict:
297|    """Create a new withdrawal"""
298|    withdrawal_id = str(uuid.uuid4())
299|    now = datetime.utcnow().isoformat()
300|    
301|    withdrawal_data['id'] = withdrawal_id
302|    withdrawal_data['requestedAt'] = now
303|    
304|    columns = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
305|               'approvedAt', 'approvedBy', 'rejectionReason']
306|    
307|    row = dict_to_row(withdrawal_data, columns)
308|    withdrawals_sheet.append_row(row)
309|    _invalidate_cache('withdrawals')
310|    
311|    return withdrawal_data
312|
313|def find_withdrawals(filter_dict: dict = None) -> List[dict]:
314|    """Find withdrawals with optional filter"""
315|    all_withdrawals = _get_cached('withdrawals', withdrawals_sheet)
316|    
317|    if not filter_dict:
318|        return all_withdrawals
319|    
320|    filtered = []
321|    for withdrawal in all_withdrawals:
322|        match = True
323|        for key, value in filter_dict.items():
324|            if withdrawal.get(key) != value:
325|                match = False
326|                break
327|        if match:
328|            filtered.append(withdrawal)
329|    
330|    return filtered
331|
332|def find_withdrawal_by_id(withdrawal_id: str) -> Optional[dict]:
333|    """Find withdrawal by ID"""
334|    all_withdrawals = _get_cached('withdrawals', withdrawals_sheet)
335|    for withdrawal in all_withdrawals:
336|        if withdrawal['id'] == withdrawal_id:
337|            return withdrawal
338|    return None
339|
340|def update_withdrawal(withdrawal_id: str, update_data: dict) -> bool:
341|    """Update withdrawal by ID"""
342|    all_records = _get_cached('withdrawals', withdrawals_sheet)
343|    for idx, withdrawal in enumerate(all_records):
344|        if withdrawal['id'] == withdrawal_id:
345|            row_num = idx + 2
346|            
347|            withdrawal = dict(withdrawal)
348|            for key, value in update_data.items():
349|                withdrawal[key] = value
350|            
351|            columns = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
352|                      'approvedAt', 'approvedBy', 'rejectionReason']
353|            
354|            row = dict_to_row(withdrawal, columns)
355|            withdrawals_sheet.update(f'A{row_num}:I{row_num}', [row])
356|            _invalidate_cache('withdrawals')
357|            return True
358|    return False
359|
360|def delete_withdrawals_by_user(user_id: str) -> int:
361|    """Delete all withdrawals for a user"""
362|    all_records = _get_cached('withdrawals', withdrawals_sheet)
363|    rows_to_delete = []
364|    
365|    for idx, withdrawal in enumerate(all_records):
366|        if withdrawal['userId'] == user_id:
367|            rows_to_delete.append(idx + 2)
368|    
369|    for row_num in reversed(rows_to_delete):
370|        withdrawals_sheet.delete_rows(row_num)
371|    
372|    _invalidate_cache('withdrawals')
373|    return len(rows_to_delete)
374|
375|def count_withdrawals(filter_dict: dict = None) -> int:
376|    """Count withdrawals with optional filter"""
377|    withdrawals = find_withdrawals(filter_dict)
378|    return len(withdrawals)
379|
380|# ===== LOANS OPERATIONS =====
381|
382|def create_loan(loan_data: dict) -> dict:
383|    """Create a new loan"""
384|    loan_id = str(uuid.uuid4())
385|    now = datetime.utcnow().isoformat()
386|    
387|    loan_data['id'] = loan_id
388|    loan_data['requestedAt'] = now
389|    loan_data['rejectionReason'] = loan_data.get('rejectionReason', '')
390|    loan_data['amountRepaid'] = loan_data.get('amountRepaid', 0)  # Default to 0
391|    
392|    columns = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
393|               'approvedAt', 'approvedBy', 'rejectionReason', 'amountRepaid']
394|    
395|    row = dict_to_row(loan_data, columns)
396|    loans_sheet.append_row(row)
397|    _invalidate_cache('loans')
398|    
399|    return loan_data
400|
401|def find_loans(filter_dict: dict = None) -> List[dict]:
402|    """Find loans with optional filter"""
403|    all_loans = _get_cached('loans', loans_sheet)
404|    
405|    # Ensure amountRepaid exists in all loan records (default to 0)
406|    for loan in all_loans:
407|        if 'amountRepaid' not in loan or loan.get('amountRepaid') == '':
408|            loan['amountRepaid'] = 0
409|    
410|    if not filter_dict:
411|        return all_loans
412|    
413|    filtered = []
414|    for loan in all_loans:
415|        match = True
416|        for key, value in filter_dict.items():
417|            if loan.get(key) != value:
418|                match = False
419|                break
420|        if match:
421|            filtered.append(loan)
422|    
423|    return filtered
424|
425|def find_loan_by_id(loan_id: str) -> Optional[dict]:
426|    """Find loan by ID"""
427|    all_loans = _get_cached('loans', loans_sheet)
428|    for loan in all_loans:
429|        if loan['id'] == loan_id:
430|            return loan
431|    return None
432|
433|def update_loan(loan_id: str, update_data: dict) -> bool:
434|    """Update loan by ID"""
435|    all_records = _get_cached('loans', loans_sheet)
436|    for idx, loan in enumerate(all_records):
437|        if loan['id'] == loan_id:
438|            row_num = idx + 2
439|            
440|            loan = dict(loan)
441|            for key, value in update_data.items():
442|                loan[key] = value
443|            
444|            columns = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
445|                      'approvedAt', 'approvedBy', 'rejectionReason', 'amountRepaid']
446|            
447|            row = dict_to_row(loan, columns)
448|            loans_sheet.update(f'A{row_num}:J{row_num}', [row])
449|            _invalidate_cache('loans')
450|            return True
451|    return False
452|
453|def delete_loans_by_user(user_id: str) -> int:
454|    """Delete all loans for a user"""
455|    all_records = _get_cached('loans', loans_sheet)
456|    rows_to_delete = []
457|    
458|    for idx, loan in enumerate(all_records):
459|        if loan['userId'] == user_id:
460|            rows_to_delete.append(idx + 2)
461|    
462|    for row_num in reversed(rows_to_delete):
463|        loans_sheet.delete_rows(row_num)
464|    
465|    _invalidate_cache('loans')
466|    return len(rows_to_delete)
467|
468|def count_loans(filter_dict: dict = None) -> int:
469|    """Count loans with optional filter"""
470|    loans = find_loans(filter_dict)
471|    return len(loans)
472|
473|# ===== SHEET HEADER VALIDATION =====
474|
475|def ensure_sheet_headers(sheet_name: str, required_headers: list, sheet_obj) -> None:
476|    """
477|    Ensure that a sheet has all required column headers.
478|    If headers are missing, add them to the end of the header row.
479|    """
480|    try:
481|        existing_headers = sheet_obj.row_values(1)
482|        
483|        # Check for missing headers
484|        missing_headers = [h for h in required_headers if h not in existing_headers]
485|        
486|        if missing_headers:
487|            logger.info(f"Adding missing headers to {sheet_name}: {missing_headers}")
488|            # Append missing headers to the existing ones
489|            updated_headers = existing_headers + missing_headers
490|            sheet_obj.update('1:1', [updated_headers])
491|            logger.info(f"✅ Successfully added headers to {sheet_name}")
492|            # Invalidate cache to force refresh
493|            _invalidate_cache(sheet_name.lower())
494|        else:
495|            logger.info(f"✅ All required headers present in {sheet_name}")
496|            
497|    except Exception as e:
498|        logger.error(f"❌ Error ensuring headers for {sheet_name}: {e}")
499|        raise
500|
501|def initialize_all_sheet_headers():
502|    """Initialize headers for all sheets on startup"""
503|    logger.info("Initializing sheet headers...")
504|    
505|    # Users sheet headers
506|    users_headers = ['id', 'username', 'passwordHash', 'fullName', 'phoneNumber', 
507|                     'memberType', 'accountBalance', 'totalDeposited', 'isAdmin', 
508|                     'isSuperAdmin', 'createdAt', 'updatedAt']
509|    ensure_sheet_headers('Users', users_headers, users_sheet)
510|    
511|    # Deposits sheet headers
512|    deposits_headers = ['id', 'userId', 'amount', 'accountNumberUsed', 'operator', 
513|                        'accountName', 'status', 'submittedAt', 'approvedAt', 
514|                        'approvedBy', 'rejectionReason']
515|    ensure_sheet_headers('Deposits', deposits_headers, deposits_sheet)
516|    
517|    # Withdrawals sheet headers
518|    withdrawals_headers = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
519|                           'approvedAt', 'approvedBy', 'rejectionReason']
520|    ensure_sheet_headers('Withdrawals', withdrawals_headers, withdrawals_sheet)
521|    
522|    # Loans sheet headers (including amountRepaid!)
523|    loans_headers = ['id', 'userId', 'amount', 'reason', 'status', 'requestedAt', 
524|                     'approvedAt', 'approvedBy', 'rejectionReason', 'amountRepaid']
525|    ensure_sheet_headers('Loans', loans_headers, loans_sheet)
526|    
527|    logger.info("✅ Sheet header initialization complete!")
528|
[End of file]
