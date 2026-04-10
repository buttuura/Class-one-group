Good! But since you need to copy it directly, let me provide you the complete content here. I'll show you the full file in one message:

**Path:** `backend/server.py`

**FULL CONTENT (830 lines):**

```python
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import sheets_db as db

ROOT_DIR = Path(__file__).parent
STATIC_DIR = ROOT_DIR / 'static'
load_dotenv(ROOT_DIR / '.env')

# JWT settings
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
LOAN_INTEREST_RATE = 0.03  # 3% per month
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Initialize sheet headers on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Google Sheets headers on application startup"""
    logger.info("Running startup tasks...")
    db.initialize_all_sheet_headers()
    logger.info("Startup complete!")
```

The file is too long (830 lines) to paste in chat. Let me give you a better solution:
Action: file_editor view /app/hashtag/backend/server.py
Observation: [Showing lines 1-831 of 831 total] /app/hashtag/backend/server.py:
1|from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
2|from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
3|from fastapi.staticfiles import StaticFiles
4|from fastapi.responses import FileResponse
5|from dotenv import load_dotenv
6|from starlette.middleware.cors import CORSMiddleware
7|import os
8|import logging
9|from pathlib import Path
10|from pydantic import BaseModel
11|from typing import List, Optional
12|from datetime import datetime, timedelta
13|from passlib.context import CryptContext
14|import jwt
15|import sheets_db as db
16|
17|ROOT_DIR = Path(__file__).parent
18|STATIC_DIR = ROOT_DIR / 'static'
19|load_dotenv(ROOT_DIR / '.env')
20|
21|# JWT settings
22|SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
23|ALGORITHM = "HS256"
24|LOAN_INTEREST_RATE = 0.03  # 3% per month
25|ACCESS_TOKEN_EXPIRE_DAYS = 30
26|
27|# Password hashing
28|pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
29|security = HTTPBearer()
30|
31|# Create the main app
32|app = FastAPI()
33|api_router = APIRouter(prefix="/api")
34|
35|# Initialize sheet headers on startup
36|@app.on_event("startup")
37|async def startup_event():
38|    """Initialize Google Sheets headers on application startup"""
39|    logger.info("Running startup tasks...")
40|    db.initialize_all_sheet_headers()
41|    logger.info("Startup complete!")
42|
43|# ========== PYDANTIC MODELS ==========
44|
45|class UserRegister(BaseModel):
46|    username: str
47|    password: str
48|    fullName: str
49|    phoneNumber: str
50|
51|class UserLogin(BaseModel):
52|    username: str
53|    password: str
54|
55|class Token(BaseModel):
56|    access_token: str
57|    token_type: str
58|    user: dict
59|
60|class DepositCreate(BaseModel):
61|    amount: float
62|    accountNumberUsed: str
63|    operator: str
64|    accountName: str
65|
66|class DepositApprove(BaseModel):
67|    depositId: str
68|    action: str
69|    reason: Optional[str] = None
70|
71|class WithdrawalCreate(BaseModel):
72|    amount: float
73|    reason: Optional[str] = None
74|
75|class WithdrawalApprove(BaseModel):
76|    withdrawalId: str
77|    action: str
78|    reason: Optional[str] = None
79|
80|class LoanApprove(BaseModel):
81|    loanId: str
82|    action: str
83|    reason: Optional[str] = None
84|
85|class LoanRepay(BaseModel):
86|    loanId: str
87|    amount: float
88|
89|class ManualDeposit(BaseModel):
90|    userId: str
91|    amount: float
92|    accountNumberUsed: str
93|    operator: str
94|    accountName: str
95|
96|class LoanRequest(BaseModel):
97|    amount: float
98|    reason: Optional[str] = None
99|
100|class CreateAdmin(BaseModel):
101|    username: str
102|    password: str
103|    fullName: str
104|    phoneNumber: str
105|
106|class UpdateMemberType(BaseModel):
107|    userId: str
108|    memberType: str
109|
110|# ========== HELPER FUNCTIONS ==========
111|
112|def verify_password(plain_password, hashed_password):
113|    return pwd_context.verify(plain_password, hashed_password)
114|
115|def get_password_hash(password):
116|    return pwd_context.hash(password)
117|
118|def create_access_token(data: dict):
119|    to_encode = data.copy()
120|    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
121|    to_encode.update({"exp": expire})
122|    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
123|    return encoded_jwt
124|
125|async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
126|    token = credentials.credentials
127|    try:
128|        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
129|        username: str = payload.get("sub")
130|        if username is None:
131|            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
132|    except jwt.ExpiredSignatureError:
133|        raise HTTPException(status_code=401, detail="Token has expired")
134|    except jwt.JWTError:
135|        raise HTTPException(status_code=401, detail="Could not validate credentials")
136|    
137|    user = db.find_user_by_username(username)
138|    if user is None:
139|        raise HTTPException(status_code=401, detail="User not found")
140|    
141|    return user
142|
143|async def get_admin_user(current_user: dict = Depends(get_current_user)):
144|    if not current_user.get('isAdmin'):
145|        raise HTTPException(status_code=403, detail="Admin access required")
146|    return current_user
147|
148|async def get_super_admin_user(current_user: dict = Depends(get_current_user)):
149|    if not current_user.get('isSuperAdmin'):
150|        raise HTTPException(status_code=403, detail="Super admin access required")
151|    return current_user
152|
153|# ========== AUTH ROUTES ==========
154|
155|@api_router.post("/auth/register", response_model=Token)
156|async def register(user_data: UserRegister):
157|    existing_user = db.find_user_by_username(user_data.username)
158|    if existing_user:
159|        raise HTTPException(status_code=400, detail="Username already exists")
160|    
161|    hashed_password = get_password_hash(user_data.password)
162|    user = db.create_user({
163|        "username": user_data.username,
164|        "passwordHash": hashed_password,
165|        "fullName": user_data.fullName,
166|        "phoneNumber": user_data.phoneNumber,
167|        "memberType": "ordinary",
168|        "accountBalance": 0,
169|        "totalDeposited": 0,
170|        "isAdmin": False,
171|        "isSuperAdmin": False
172|    })
173|    
174|    access_token = create_access_token(data={"sub": user_data.username})
175|    
176|    user_response = {
177|        "_id": user['id'],
178|        "username": user['username'],
179|        "fullName": user['fullName'],
180|        "phoneNumber": user['phoneNumber'],
181|        "memberType": user['memberType'],
182|        "accountBalance": user['accountBalance'],
183|        "totalDeposited": user['totalDeposited'],
184|        "isAdmin": user['isAdmin'],
185|        "isSuperAdmin": user.get('isSuperAdmin', False)
186|    }
187|    
188|    return {
189|        "access_token": access_token,
190|        "token_type": "bearer",
191|        "user": user_response
192|    }
193|
194|@api_router.post("/auth/login", response_model=Token)
195|async def login(user_data: UserLogin):
196|    user = db.find_user_by_username(user_data.username)
197|    if not user or not verify_password(user_data.password, user['passwordHash']):
198|        raise HTTPException(status_code=401, detail="Invalid username or password")
199|    
200|    access_token = create_access_token(data={"sub": user_data.username})
201|    
202|    user_response = {
203|        "_id": user['id'],
204|        "username": user['username'],
205|        "fullName": user['fullName'],
206|        "phoneNumber": user['phoneNumber'],
207|        "memberType": user['memberType'],
208|        "accountBalance": user['accountBalance'],
209|        "totalDeposited": user['totalDeposited'],
210|        "isAdmin": user.get('isAdmin', False),
211|        "isSuperAdmin": user.get('isSuperAdmin', False)
212|    }
213|    
214|    return {
215|        "access_token": access_token,
216|        "token_type": "bearer",
217|        "user": user_response
218|    }
219|
220|@api_router.get("/auth/me")
221|async def get_me(current_user: dict = Depends(get_current_user)):
222|    return {
223|        "_id": current_user['id'],
224|        "username": current_user['username'],
225|        "fullName": current_user['fullName'],
226|        "phoneNumber": current_user['phoneNumber'],
227|        "memberType": current_user['memberType'],
228|        "accountBalance": current_user['accountBalance'],
229|        "totalDeposited": current_user['totalDeposited'],
230|        "isAdmin": current_user.get('isAdmin', False),
231|        "isSuperAdmin": current_user.get('isSuperAdmin', False)
232|    }
233|
234|# ========== DEPOSIT ROUTES ==========
235|
236|@api_router.post("/deposits")
237|async def create_deposit(deposit_data: DepositCreate, current_user: dict = Depends(get_current_user)):
238|    deposit = db.create_deposit({
239|        "userId": current_user['id'],
240|        "amount": deposit_data.amount,
241|        "accountNumberUsed": deposit_data.accountNumberUsed,
242|        "operator": deposit_data.operator,
243|        "accountName": deposit_data.accountName,
244|        "status": "pending",
245|        "approvedAt": "",
246|        "approvedBy": "",
247|        "rejectionReason": ""
248|    })
249|    
250|    return {"message": "Deposit submitted successfully", "deposit": deposit}
251|
252|@api_router.get("/deposits")
253|async def get_deposits(current_user: dict = Depends(get_current_user)):
254|    if current_user.get('isAdmin'):
255|        deposits = db.find_deposits()
256|    else:
257|        deposits = db.find_deposits({"userId": current_user['id']})
258|    
259|    # Add user details
260|    for deposit in deposits:
261|        user = db.find_user_by_id(deposit['userId'])
262|        if user:
263|            deposit['userDetails'] = {
264|                "username": user['username'],
265|                "fullName": user['fullName'],
266|                "phoneNumber": user['phoneNumber']
267|            }
268|    
269|    return deposits
270|
271|@api_router.put("/deposits/approve")
272|async def approve_deposit(approve_data: DepositApprove, admin_user: dict = Depends(get_admin_user)):
273|    deposit = db.find_deposit_by_id(approve_data.depositId)
274|    if not deposit:
275|        raise HTTPException(status_code=404, detail="Deposit not found")
276|    
277|    if deposit['status'] != 'pending':
278|        raise HTTPException(status_code=400, detail="Deposit already processed")
279|    
280|    if approve_data.action == 'approve':
281|        db.update_deposit(approve_data.depositId, {
282|            "status": "approved",
283|            "approvedAt": datetime.utcnow().isoformat(),
284|            "approvedBy": admin_user['id']
285|        })
286|        
287|        user = db.find_user_by_id(deposit['userId'])
288|        new_balance = float(user['accountBalance']) + float(deposit['amount'])
289|        new_total = float(user['totalDeposited']) + float(deposit['amount'])
290|        
291|        # Auto-upgrade to premium if total deposited >= 55,000 UGX
292|        update_data = {
293|            "accountBalance": new_balance,
294|            "totalDeposited": new_total
295|        }
296|        if new_total >= 55000 and user.get('memberType') != 'premium':
297|            update_data["memberType"] = "premium"
298|        
299|        db.update_user(deposit['userId'], update_data)
300|        
301|        return {"message": "Deposit approved successfully", "newBalance": new_balance}
302|    
303|    elif approve_data.action == 'reject':
304|        db.update_deposit(approve_data.depositId, {
305|            "status": "rejected",
306|            "approvedAt": datetime.utcnow().isoformat(),
307|            "approvedBy": admin_user['id'],
308|            "rejectionReason": approve_data.reason or ""
309|        })
310|        
311|        return {"message": "Deposit rejected"}
312|    
313|    raise HTTPException(status_code=400, detail="Invalid action")
314|
315|@api_router.post("/deposits/manual")
316|async def create_manual_deposit(deposit_data: ManualDeposit, admin_user: dict = Depends(get_admin_user)):
317|    deposit = db.create_deposit({
318|        "userId": deposit_data.userId,
319|        "amount": deposit_data.amount,
320|        "accountNumberUsed": deposit_data.accountNumberUsed,
321|        "operator": deposit_data.operator,
322|        "accountName": deposit_data.accountName,
323|        "status": "approved",
324|        "approvedAt": datetime.utcnow().isoformat(),
325|        "approvedBy": admin_user['id'],
326|        "rejectionReason": ""
327|    })
328|    
329|    user = db.find_user_by_id(deposit_data.userId)
330|    if not user:
331|        raise HTTPException(status_code=404, detail="User not found")
332|    
333|    new_balance = float(user['accountBalance']) + deposit_data.amount
334|    new_total = float(user['totalDeposited']) + deposit_data.amount
335|    
336|    # Auto-upgrade to premium if total deposited >= 55,000 UGX
337|    update_data = {
338|        "accountBalance": new_balance,
339|        "totalDeposited": new_total
340|    }
341|    if new_total >= 55000 and user.get('memberType') != 'premium':
342|        update_data["memberType"] = "premium"
343|    
344|    db.update_user(deposit_data.userId, update_data)
345|    
346|    return {"message": "Manual deposit added successfully", "newBalance": new_balance}
347|
348|# ========== WITHDRAWAL ROUTES ==========
349|
350|@api_router.post("/withdrawals")
351|async def create_withdrawal(withdrawal_data: WithdrawalCreate, current_user: dict = Depends(get_current_user)):
352|    if float(current_user['accountBalance']) < withdrawal_data.amount:
353|        raise HTTPException(status_code=400, detail="Insufficient balance")
354|    
355|    withdrawal = db.create_withdrawal({
356|        "userId": current_user['id'],
357|        "amount": withdrawal_data.amount,
358|        "reason": withdrawal_data.reason or "",
359|        "status": "pending",
360|        "approvedAt": "",
361|        "approvedBy": "",
362|        "rejectionReason": ""
363|    })
364|    
365|    return {"message": "Withdrawal request submitted successfully", "withdrawal": withdrawal}
366|
367|@api_router.get("/withdrawals")
368|async def get_withdrawals(current_user: dict = Depends(get_current_user)):
369|    if current_user.get('isAdmin'):
370|        withdrawals = db.find_withdrawals()
371|    else:
372|        withdrawals = db.find_withdrawals({"userId": current_user['id']})
373|    
374|    for withdrawal in withdrawals:
375|        user = db.find_user_by_id(withdrawal['userId'])
376|        if user:
377|            withdrawal['userDetails'] = {
378|                "username": user['username'],
379|                "fullName": user['fullName'],
380|                "phoneNumber": user['phoneNumber'],
381|                "accountBalance": user['accountBalance']
382|            }
383|    
384|    return withdrawals
385|
386|@api_router.put("/withdrawals/approve")
387|async def approve_withdrawal(approve_data: WithdrawalApprove, admin_user: dict = Depends(get_admin_user)):
388|    withdrawal = db.find_withdrawal_by_id(approve_data.withdrawalId)
389|    if not withdrawal:
390|        raise HTTPException(status_code=404, detail="Withdrawal not found")
391|    
392|    if withdrawal['status'] != 'pending':
393|        raise HTTPException(status_code=400, detail="Withdrawal already processed")
394|    
395|    user = db.find_user_by_id(withdrawal['userId'])
396|    
397|    if approve_data.action == 'approve':
398|        if float(user['accountBalance']) < float(withdrawal['amount']):
399|            raise HTTPException(status_code=400, detail="User has insufficient balance")
400|        
401|        db.update_withdrawal(approve_data.withdrawalId, {
402|            "status": "approved",
403|            "approvedAt": datetime.utcnow().isoformat(),
404|            "approvedBy": admin_user['id']
405|        })
406|        
407|        new_balance = float(user['accountBalance']) - float(withdrawal['amount'])
408|        db.update_user(withdrawal['userId'], {
409|            "accountBalance": new_balance
410|        })
411|        
412|        return {"message": "Withdrawal approved successfully", "newBalance": new_balance}
413|    
414|    elif approve_data.action == 'reject':
415|        db.update_withdrawal(approve_data.withdrawalId, {
416|            "status": "rejected",
417|            "approvedAt": datetime.utcnow().isoformat(),
418|            "approvedBy": admin_user['id'],
419|            "rejectionReason": approve_data.reason or ""
420|        })
421|        
422|        return {"message": "Withdrawal rejected"}
423|    
424|    raise HTTPException(status_code=400, detail="Invalid action")
425|
426|# ========== USER ROUTES ==========
427|
428|@api_router.get("/users/profile")
429|async def get_profile(current_user: dict = Depends(get_current_user)):
430|    is_eligible = current_user['memberType'] == 'premium'
431|    
432|    deposits = db.find_deposits({"userId": current_user['id']})
433|    deposits = sorted(deposits, key=lambda x: x.get('submittedAt', ''), reverse=True)[:5]
434|    
435|    withdrawals = db.find_withdrawals({"userId": current_user['id']})
436|    withdrawals = sorted(withdrawals, key=lambda x: x.get('requestedAt', ''), reverse=True)[:5]
437|    
438|    for d in deposits:
439|        d['type'] = 'deposit'
440|        d['date'] = d.get('submittedAt', '')
441|    
442|    for w in withdrawals:
443|        w['type'] = 'withdrawal'
444|        w['date'] = w.get('requestedAt', '')
445|    
446|    transactions = deposits + withdrawals
447|    transactions = sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)[:10]
448|    
449|    # Loan summary for this user
450|    user_loans = db.find_loans({"userId": current_user['id']})
451|    total_loans_taken = sum(float(l.get('amount', 0)) for l in user_loans if l.get('status') in ['approved', 'repaid'])
452|    active_loans = [l for l in user_loans if l.get('status') == 'approved']
453|    total_owed = 0
454|    for loan in active_loans:
455|        info = calculate_loan_interest(loan)
456|        total_owed += info['totalOwed']
457|    total_repaid = sum(float(l.get('amountRepaid', 0)) for l in user_loans)
458|    
459|    # Group totals (all approved deposits across all users)
460|    all_deposits = db.find_deposits()
461|    group_total_collected = sum(float(d.get('amount', 0)) for d in all_deposits if d.get('status') == 'approved')
462|    
463|    # Total members
464|    all_users = db.get_all_users()
465|    total_members = len([u for u in all_users if not u.get('isAdmin') and not u.get('isSuperAdmin')])
466|    
467|    return {
468|        "user": {
469|            "_id": current_user['id'],
470|            "username": current_user['username'],
471|            "fullName": current_user['fullName'],
472|            "phoneNumber": current_user['phoneNumber'],
473|            "memberType": current_user['memberType'],
474|            "accountBalance": current_user['accountBalance'],
475|            "totalDeposited": current_user['totalDeposited'],
476|            "isAdmin": current_user.get('isAdmin', False),
477|            "isSuperAdmin": current_user.get('isSuperAdmin', False)
478|        },
479|        "loanEligibility": {
480|            "isEligible": is_eligible,
481|            "reason": "Premium members are eligible for loans" if is_eligible else "Only premium members (55,000 UGX/month) are eligible"
482|        },
483|        "loanSummary": {
484|            "totalLoansTaken": total_loans_taken,
485|            "totalOwed": round(total_owed, 0),
486|            "totalRepaid": total_repaid,
487|            "activeLoans": len(active_loans)
488|        },
489|        "groupStats": {
490|            "totalCollected": group_total_collected,
491|            "totalMembers": total_members
492|        },
493|        "recentTransactions": transactions
494|    }
495|
496|@api_router.get("/users/transactions")
497|async def get_transactions(current_user: dict = Depends(get_current_user)):
498|    deposits = db.find_deposits({"userId": current_user['id']})
499|    withdrawals = db.find_withdrawals({"userId": current_user['id']})
500|    
501|    for d in deposits:
502|        d['type'] = 'deposit'
503|        d['date'] = d.get('submittedAt', '')
504|    
505|    for w in withdrawals:
506|        w['type'] = 'withdrawal'
507|        w['date'] = w.get('requestedAt', '')
508|    
509|    transactions = deposits + withdrawals
510|    transactions = sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)
511|    
512|    return transactions
513|
514|@api_router.get("/users")
515|async def get_all_users(admin_user: dict = Depends(get_admin_user)):
516|    users = db.get_all_users()
517|    
518|    user_list = []
519|    for user in users:
520|        user_list.append({
521|            "_id": user['id'],
522|            "username": user['username'],
523|            "fullName": user['fullName'],
524|            "phoneNumber": user['phoneNumber'],
525|            "memberType": user['memberType'],
526|            "accountBalance": user['accountBalance'],
527|            "totalDeposited": user['totalDeposited'],
528|            "isAdmin": user.get('isAdmin', False),
529|            "isSuperAdmin": user.get('isSuperAdmin', False),
530|            "createdAt": user.get('createdAt', '')
531|        })
532|    
533|    return user_list
534|
535|@api_router.put("/users/member-type")
536|async def update_user_member_type(data: UpdateMemberType, admin_user: dict = Depends(get_super_admin_user)):
537|    if data.memberType not in ['ordinary', 'premium']:
538|        raise HTTPException(status_code=400, detail="Invalid member type")
539|    
540|    success = db.update_user(data.userId, {"memberType": data.memberType})
541|    
542|    if not success:
543|        raise HTTPException(status_code=404, detail="User not found")
544|    
545|    return {"message": "Member type updated successfully", "memberType": data.memberType}
546|
547|@api_router.delete("/users/{user_id}")
548|async def delete_user(user_id: str, super_admin: dict = Depends(get_super_admin_user)):
549|    if user_id == super_admin['id']:
550|        raise HTTPException(status_code=400, detail="Cannot delete your own account")
551|    
552|    success = db.delete_user(user_id)
553|    
554|    if not success:
555|        raise HTTPException(status_code=404, detail="User not found")
556|    
557|    db.delete_deposits_by_user(user_id)
558|    db.delete_withdrawals_by_user(user_id)
559|    db.delete_loans_by_user(user_id)
560|    
561|    return {"message": "User deleted successfully"}
562|
563|# ========== LOAN ROUTES ==========
564|
565|def calculate_loan_interest(loan: dict) -> dict:
566|    """Calculate interest on a loan. 3% per month on remaining balance."""
567|    loan_amount = float(loan.get('amount', 0))
568|    amount_repaid = float(loan.get('amountRepaid', 0))
569|    remaining_principal = loan_amount - amount_repaid
570|    
571|    if remaining_principal <= 0 or loan.get('status') != 'approved':
572|        return {
573|            "principal": loan_amount,
574|            "amountRepaid": amount_repaid,
575|            "remainingPrincipal": max(0, remaining_principal),
576|            "interestAccrued": 0,
577|            "totalOwed": max(0, remaining_principal),
578|            "monthsElapsed": 0
579|        }
580|    
581|    # Calculate months since approval
582|    approved_at = loan.get('approvedAt', '')
583|    if approved_at:
584|        try:
585|            approved_date = datetime.fromisoformat(approved_at.replace('Z', '+00:00').replace('+00:00', ''))
586|        except:
587|            approved_date = datetime.utcnow()
588|        
589|        now = datetime.utcnow()
590|        days_elapsed = (now - approved_date).days
591|        months_elapsed = days_elapsed // 30  # Full months only
592|    else:
593|        months_elapsed = 0
594|    
595|    # 3% interest per month on remaining balance (compounding)
596|    interest_balance = remaining_principal
597|    total_interest = 0
598|    for m in range(months_elapsed):
599|        month_interest = interest_balance * LOAN_INTEREST_RATE
600|        total_interest += month_interest
601|        interest_balance += month_interest
602|    
603|    total_owed = remaining_principal + total_interest
604|    
605|    return {
606|        "principal": loan_amount,
607|        "amountRepaid": amount_repaid,
608|        "remainingPrincipal": remaining_principal,
609|        "interestAccrued": round(total_interest, 0),
610|        "totalOwed": round(total_owed, 0),
611|        "monthsElapsed": months_elapsed
612|    }
613|
614|@api_router.get("/loans/eligibility")
615|async def check_loan_eligibility(current_user: dict = Depends(get_current_user)):
616|    is_eligible = current_user['memberType'] == 'premium'
617|    max_loan = float(current_user['accountBalance']) * 0.5
618|    
619|    return {
620|        "isEligible": is_eligible,
621|        "memberType": current_user['memberType'],
622|        "maxLoanAmount": max_loan if is_eligible else 0,
623|        "reason": "Premium members are eligible for loans up to 50% of their balance" if is_eligible else "Only premium members are eligible for loans"
624|    }
625|
626|@api_router.post("/loans")
627|async def request_loan(loan_data: LoanRequest, current_user: dict = Depends(get_current_user)):
628|    if current_user['memberType'] != 'premium':
629|        raise HTTPException(status_code=403, detail="Only premium members can request loans")
630|    
631|    max_loan = float(current_user['accountBalance']) * 0.5
632|    if loan_data.amount > max_loan:
633|        raise HTTPException(status_code=400, detail=f"Maximum loan amount is {max_loan} UGX")
634|    
635|    loan = db.create_loan({
636|        "userId": current_user['id'],
637|        "amount": loan_data.amount,
638|        "reason": loan_data.reason or "",
639|        "status": "pending",
640|        "approvedAt": "",
641|        "approvedBy": ""
642|    })
643|    
644|    return {"message": "Loan request submitted successfully", "loan": loan}
645|
646|@api_router.get("/loans")
647|async def get_loans(current_user: dict = Depends(get_current_user)):
648|    if current_user.get('isAdmin'):
649|        loans = db.find_loans()
650|    else:
651|        loans = db.find_loans({"userId": current_user['id']})
652|    
653|    for loan in loans:
654|        user = db.find_user_by_id(loan['userId'])
655|        if user:
656|            loan['userDetails'] = {
657|                "username": user['username'],
658|                "fullName": user['fullName'],
659|                "phoneNumber": user['phoneNumber']
660|            }
661|        # Add interest calculations
662|        loan['interestInfo'] = calculate_loan_interest(loan)
663|    
664|    return loans
665|
666|@api_router.post("/loans/repay")
667|async def repay_loan(repay_data: LoanRepay, current_user: dict = Depends(get_current_user)):
668|    loan = db.find_loan_by_id(repay_data.loanId)
669|    if not loan:
670|        raise HTTPException(status_code=404, detail="Loan not found")
671|    
672|    if loan['userId'] != current_user['id']:
673|        raise HTTPException(status_code=403, detail="Not your loan")
674|    
675|    if loan['status'] != 'approved':
676|        raise HTTPException(status_code=400, detail="Loan not active")
677|    
678|    interest_info = calculate_loan_interest(loan)
679|    total_owed = interest_info['totalOwed']
680|    
681|    if repay_data.amount <= 0:
682|        raise HTTPException(status_code=400, detail="Amount must be positive")
683|    
684|    if repay_data.amount > float(current_user['accountBalance']):
685|        raise HTTPException(status_code=400, detail="Insufficient balance")
686|    
687|    pay_amount = min(repay_data.amount, total_owed)
688|    
689|    current_repaid = float(loan.get('amountRepaid', 0))
690|    new_repaid = current_repaid + pay_amount
691|    
692|    # Deduct from user balance
693|    new_balance = float(current_user['accountBalance']) - pay_amount
694|    db.update_user(current_user['id'], {"accountBalance": new_balance})
695|    
696|    # Check if fully repaid
697|    new_interest = calculate_loan_interest({**loan, 'amountRepaid': new_repaid})
698|    if new_interest['totalOwed'] <= 0:
699|        db.update_loan(repay_data.loanId, {
700|            "amountRepaid": new_repaid,
701|            "status": "repaid"
702|        })
703|        return {"message": "Loan fully repaid!", "newBalance": new_balance, "fullyRepaid": True}
704|    else:
705|        db.update_loan(repay_data.loanId, {
706|            "amountRepaid": new_repaid
707|        })
708|        return {"message": f"Payment of {pay_amount} UGX recorded", "newBalance": new_balance, "fullyRepaid": False, "remaining": new_interest['totalOwed']}
709|
710|@api_router.put("/loans/approve")
711|async def approve_loan(approve_data: LoanApprove, admin_user: dict = Depends(get_admin_user)):
712|    loan = db.find_loan_by_id(approve_data.loanId)
713|    if not loan:
714|        raise HTTPException(status_code=404, detail="Loan not found")
715|    
716|    if loan['status'] != 'pending':
717|        raise HTTPException(status_code=400, detail="Loan already processed")
718|    
719|    user = db.find_user_by_id(loan['userId'])
720|    
721|    if approve_data.action == 'approve':
722|        db.update_loan(approve_data.loanId, {
723|            "status": "approved",
724|            "approvedAt": datetime.utcnow().isoformat(),
725|            "approvedBy": admin_user['id']
726|        })
727|        
728|        # Add loan amount to user balance
729|        new_balance = float(user['accountBalance']) + float(loan['amount'])
730|        db.update_user(loan['userId'], {
731|            "accountBalance": new_balance
732|        })
733|        
734|        return {"message": "Loan approved successfully", "newBalance": new_balance}
735|    
736|    elif approve_data.action == 'reject':
737|        db.update_loan(approve_data.loanId, {
738|            "status": "rejected",
739|            "approvedAt": datetime.utcnow().isoformat(),
740|            "approvedBy": admin_user['id'],
741|            "rejectionReason": approve_data.reason or ""
742|        })
743|        
744|        return {"message": "Loan rejected"}
745|    
746|    raise HTTPException(status_code=400, detail="Invalid action")
747|
748|# ========== ADMIN ROUTES ==========
749|
750|@api_router.get("/admin/stats")
751|async def get_admin_stats(admin_user: dict = Depends(get_admin_user)):
752|    total_users = db.count_users()
753|    pending_deposits = db.count_deposits({"status": "pending"})
754|    pending_withdrawals = db.count_withdrawals({"status": "pending"})
755|    pending_loans = db.count_loans({"status": "pending"})
756|    
757|    total_deposits = db.sum_deposits({"status": "approved"})
758|    
759|    premium_users = db.count_users({"memberType": "premium"})
760|    ordinary_users = db.count_users({"memberType": "ordinary"})
761|    
762|    return {
763|        "totalUsers": total_users,
764|        "pendingDeposits": pending_deposits,
765|        "pendingWithdrawals": pending_withdrawals,
766|        "pendingLoans": pending_loans,
767|        "totalDepositsApproved": total_deposits,
768|        "premiumUsers": premium_users,
769|        "ordinaryUsers": ordinary_users
770|    }
771|
772|@api_router.post("/admin/create")
773|async def create_admin_user(admin_data: CreateAdmin, admin_user: dict = Depends(get_super_admin_user)):
774|    existing_user = db.find_user_by_username(admin_data.username)
775|    if existing_user:
776|        raise HTTPException(status_code=400, detail="Username already exists")
777|    
778|    hashed_password = get_password_hash(admin_data.password)
779|    new_admin = db.create_user({
780|        "username": admin_data.username,
781|        "passwordHash": hashed_password,
782|        "fullName": admin_data.fullName,
783|        "phoneNumber": admin_data.phoneNumber,
784|        "memberType": "premium",
785|        "accountBalance": 0,
786|        "totalDeposited": 0,
787|        "isAdmin": True,
788|        "isSuperAdmin": False
789|    })
790|    
791|    return {
792|        "message": "Admin user created successfully",
793|        "admin": {
794|            "_id": new_admin['id'],
795|            "username": new_admin['username'],
796|            "fullName": new_admin['fullName'],
797|            "phoneNumber": new_admin['phoneNumber'],
798|            "isAdmin": True
799|        }
800|    }
801|
802|# Include the router in the main app
803|app.include_router(api_router)
804|
805|app.add_middleware(
806|    CORSMiddleware,
807|    allow_credentials=True,
808|    allow_origins=["*"],
809|    allow_methods=["*"],
810|    allow_headers=["*"],
811|)
812|
813|# Serve frontend static files (built React app)
814|if STATIC_DIR.exists():
815|    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
816|    
817|    @app.get("/{full_path:path}")
818|    async def serve_frontend(full_path: str):
819|        """Serve the React app for all non-API routes"""
820|        file_path = STATIC_DIR / full_path
821|        if file_path.is_file():
822|            return FileResponse(file_path)
823|        return FileResponse(STATIC_DIR / "index.html")
824|
825|# Configure logging
826|logging.basicConfig(
827|    level=logging.INFO,
828|    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
829|)
830|logger = logging.getLogger(__name__)
831|
[End of file]
