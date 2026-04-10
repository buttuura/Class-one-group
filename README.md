# Savings Group Manager

A full-stack savings group management application with Google Sheets as the database.

## Features

- ✅ User Registration & Login (JWT Authentication)
- ✅ Member Dashboard with Balance Tracking
- ✅ Deposit Submissions with Admin Approval
- ✅ Withdrawal Requests
- ✅ Loan System (Premium members can request up to 50% of balance)
- ✅ Admin Dashboard for Approvals
- ✅ Super Admin User Management
- ✅ Automatic Member Type Upgrades (Ordinary → Premium at 55K UGX)
- ✅ Loan Interest Calculation (3% per month)

## Tech Stack

**Backend:**
- FastAPI (Python)
- Google Sheets (Database via gspread)
- JWT Authentication
- bcrypt Password Hashing

**Frontend:**
- React 19
- React Router
- Axios
- Tailwind CSS
- React Hot Toast

## Deployment on Render

### Step 1: Set Up Google Sheets

1. Create a new Google Sheet
2. Create a service account in Google Cloud Console
3. Enable Google Sheets API
4. Share the spreadsheet with the service account email
5. Download the service account JSON credentials

### Step 2: Deploy to Render

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables

Add these on Render:

JWT_SECRET=your-secret-key-here SPREADSHEET_ID=your-google-sheets-id GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}


## Default Admin Account

After first deployment:
- **Username:** `admin`
- **Password:** `123456`

**⚠️ Change this password immediately!**

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login
- GET `/api/auth/me` - Get current user

### Deposits
- POST `/api/deposits` - Create deposit
- GET `/api/deposits` - Get deposits
- PUT `/api/deposits/approve` - Approve/reject (Admin)

### Withdrawals
- POST `/api/withdrawals` - Request withdrawal
- GET `/api/withdrawals` - Get withdrawals
- PUT `/api/withdrawals/approve` - Approve/reject (Admin)

### Loans
- POST `/api/loans` - Request loan
- GET `/api/loans` - Get loans
- PUT `/api/loans/approve` - Approve/reject (Admin)
- POST `/api/loans/repay` - Repay loan

### Admin
- GET `/api/admin/stats` - Get dashboard stats
- POST `/api/admin/create` - Create admin (Super Admin)
- GET `/api/users` - Get all users (Admin)

## License

MIT
