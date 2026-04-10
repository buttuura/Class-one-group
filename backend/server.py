Great! ✅ Now the big one:

## File 5: backend/server.py

**Path:** `backend/server.py`

This is 831 lines - the main FastAPI application with all routes:
Action: file_editor view /app/hashtag/backend/server.py
Observation: [Showing lines 1-200 of 831 total] /app/hashtag/backend/server.py:
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
 [200 lines shown. Remaining: lines 201-831 (631 lines). Use view_range parameter to continue.]
