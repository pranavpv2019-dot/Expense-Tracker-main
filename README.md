
### Personal Expense Tracker 💰

A Django-based web application for managing personal finances. Users can track income and expenses, monitor balances, analyze spending with charts, manage recurring expenses, receive email alerts, scan bills using OCR, and download financial reports in Excel format. The project also includes user authentication and an admin panel for efficient data management.

### Key Features

- 🔐 User Registration and Secure Login
- 💰 Income and Expense Management
- 📊 Expense Analysis with Charts
- 🔄 Recurring Expense Management
- 📧 Email Alerts for High Spending
- 🧾 OCR-Based Bill Scanning
- 📥 Excel Report Download
- 📜 Expense History Tracking
- 👤 User Profile Management
- 🛠️ Admin Panel for Data Management
- 📱 User-Friendly Web Interface

### Technologies Used

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Django
- Database: SQLite
- OCR: Tesseract OCR
- Data Visualization: Chart.js
- Email Service: Django Email Backend
- Data Export: Excel / OpenPyXL
- Development Tools: VS Code, Git, GitHub


## Installation

Follow these steps to set up the project locally:

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/pranavpv2019-dot/Expense-Tracker-main.git
cd Expense-Tracker-main
cd expense-tracker
```
### 2. Create a Virtual Environment (Optional but recommended)
It's recommended to use a virtual environment for managing dependencies. You can create one by running:
```bash
python -m venv venv
```
Activate the virtual environment:
On Windows:
```bash
venv\Scripts\activate
```
On Mac/Linux:
```bash
source venv/bin/activate
```
### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```
### 4. Set Up the Database
Run the migrations to set up the database:
Python Expense Tracker Output:
```bash
python manage.py migrate
```
### 5. Create a Superuser (for Admin Access)
If you want to access the Django admin panel, create a superuser:
```bash
python manage.py createsuperuser
```
Follow the prompts to set the username, email, and password.

### 6. Run the Development Server
Start the development server to run the application:
```bash
python manage.py runserver
```
The application should now be accessible at http://127.0.0.1:8000/

**Usage**

**Accessing the Application:** Visit http://127.0.0.1:8000/ in your web browser to start using the expense tracker.

**Admin Panel:** Access the Django admin panel at http://127.0.0.1:8000/admin/ using the superuser credentials created earlier.

