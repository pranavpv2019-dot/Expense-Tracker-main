from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info,UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models.functions import Abs
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.csrf import csrf_protect
import time
import csv
import json
from django.core.paginator import Paginator
from .models import Addmoney_info
from datetime import date, timedelta
#email pop up message
from django.core.mail import send_mail
from django.conf import settings
#recurring expense
from .models import RecurringExpense
from datetime import date, timedelta



# Create your views here.
def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request,'home/login.html')
   # return HttpResponse('This is home')
def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')

        # Pagination
        paginator = Paginator(addmoney_info, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Total expense & income
        total_expense = addmoney_info.filter(add_money='Expense').aggregate(
            total=Sum(Abs('quantity'))  # <-- Make expenses positive
        )['total'] or 0

        total_income = addmoney_info.filter(add_money='Income').aggregate(
            total=Sum('quantity')
        )['total'] or 0

        # Current balance
        current_balance = total_income - total_expense

        context = {
            'page_obj': page_obj,
            'total_expense': total_expense,
            'total_income': total_income,
            'current_income': current_balance,
        }

        return render(request,'home/index.html', context)

    return redirect('home')
def expense(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        # Get all income and expense transactions for the user
        addmoney_info = Addmoney_info.objects.filter(
            user=user1,
            Date__gte=one_month_ago,
            Date__lte=todays_date
        )

        # Use Django's Sum aggregation to get the total expense.
        # This is more efficient than a Python loop.
        total_expense = addmoney_info.filter(add_money='Expense').aggregate(Sum('quantity'))['quantity__sum']

        # Handle the case where there are no expenses (the sum would be None)
        if total_expense is None:
            total_expense = 0

        # Pass the calculated total expense to the template in a context dictionary
        context = {
            'total_expense': total_expense,
        }
        
        return render(request, 'home/index.html', context)
    
    return redirect('home')

        
def register(request):
    return render(request,'home/register.html')
    #return HttpResponse('This is blog')
def password(request):
    return render(request,'home/password.html')

def charts(request):
    return render(request,'home/charts.html')
def search(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.GET['fromdate']
        todate = request.GET['todate']
        addmoney = Addmoney_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addmoney_info.objects.filter(user=user).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def addmoney(request):
    return render(request,'home/addmoney.html')

def profile(request):
    if request.session.has_key('is_logged'):
        return render(request,'home/profile.html')
    return redirect('/home')

def profile_edit(request,id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        # user_id = request.session["user_id"]
        # user1 = User.objects.get(id=user_id)
        return render(request,'home/profile_edit.html',{'add':add})
    return redirect("/home")

# def profile_update(request,id):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user = User.objects.get(id=id)
#             user.first_name = request.POST["fname"]
#             user.last_name = request.POST["lname"]
#             user.email = request.POST["email"]
#             user.userprofile.Savings = request.POST["Savings"]
#             user.userprofile.income = request.POST["income"]
#             user.userprofile.profession = request.POST["profession"]
#             user.userprofile.save()
#             user.save()
#             return redirect("/profile")
#     return redirect("/home")   
def profile_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST.get("fname", "")
            user.last_name = request.POST.get("lname", "")
            user.email = request.POST.get("email", "")
            user.userprofile.Savings = request.POST.get("Savings", 0)
            user.userprofile.income = request.POST.get("income", 0)
            user.userprofile.profession = request.POST.get("profession", "")

            # ✅ Handle profile image upload
            if 'profile_image' in request.FILES:
                user.userprofile.profile_image = request.FILES['profile_image']

            user.userprofile.save()
            user.save()
            return redirect("/profile")
    return redirect("/home")
def handleSignup(request):
    if request.method =='POST':
            # get the post parameters
            uname = request.POST["uname"]
            fname=request.POST["fname"]
            lname=request.POST["lname"]
            email = request.POST["email"]
            profession = request.POST['profession']
            Savings = request.POST['Savings']
            income = request.POST['income']
            pass1 = request.POST["pass1"]
            pass2 = request.POST["pass2"]
            profile = UserProfile(Savings = Savings,profession=profession,income=income)
            # check for errors in input
            if request.method == 'POST':
                try:
                    user_exists = User.objects.get(username=request.POST['uname'])
                    messages.error(request," Username already taken, Try something else!!!")
                    return redirect("/register")    
                except User.DoesNotExist:
                    if len(uname)>15:
                        messages.error(request," Username must be max 15 characters, Please try again")
                        return redirect("/register")
            
                    if not uname.isalnum():
                        messages.error(request," Username should only contain letters and numbers, Please try again")
                        return redirect("/register")
            
                    if pass1 != pass2:
                        messages.error(request," Password do not match, Please try again")
                        return redirect("/register")
            
            # create the user
            user = User.objects.create_user(uname, email, pass1)
            user.first_name=fname
            user.last_name=lname
            user.email = email
            # profile = UserProfile.objects.all()

            user.save()
            # p1=profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request," Your account has been successfully created")
            return redirect("/")
    else:
        return HttpResponse('404 - NOT FOUND ')
    return redirect('/login')

# def handlelogin(request):
#     if request.method =='POST':
#         # get the post parameters
#         loginuname = request.POST["loginuname"]
#         loginpassword1=request.POST["loginpassword1"]
#         user = authenticate(username=loginuname, password=loginpassword1)
#         if user is not None:
#             dj_login(request, user)
#             request.session['is_logged'] = True
#             user = request.user.id 
#             request.session["user_id"] = user
#             messages.success(request, " Successfully logged in")
#             return redirect('/index')
#         else:
#             messages.error(request," Invalid Credentials, Please try again")  
#             return redirect("/")  
#     return HttpResponse('404-not found')
@csrf_protect
def handleloginpage(request):
    return render(request, 'login.html')


# ---------- Handle Login with 3-Attempt Limit + 1-Min Timeout ----------

def handlelogin(request):
    if request.method == 'POST':
        loginuname = request.POST.get("loginuname")
        loginpassword1 = request.POST.get("loginpassword1")

        # Initialize session counters if not already set
        if 'login_attempts' not in request.session:
            request.session['login_attempts'] = 0
        if 'lockout_time' not in request.session:
            request.session['lockout_time'] = None

        lockout_time = request.session.get('lockout_time')
        current_time = time.time()

        # --- LOCKOUT CHECK: render timeout page ---
        if lockout_time and current_time < lockout_time:
            remaining = int(lockout_time - current_time)
            # Render a dedicated timeout page with countdown
            return render(request, 'home/timeout.html', {'remaining': remaining})

        # Authenticate user
        user = authenticate(username=loginuname, password=loginpassword1)

        if user is not None:
            # Reset counters on successful login
            dj_login(request, user)
            request.session['is_logged'] = True
            request.session['user_id'] = user.id
            request.session['login_attempts'] = 0
            request.session['lockout_time'] = None
            messages.success(request, "Successfully logged in")
            return redirect('/index')

        else:
            # Increment failed attempts
            request.session['login_attempts'] += 1
            remaining_attempts = 3 - request.session['login_attempts']

            if request.session['login_attempts'] >= 3:
                # Set 1-minute lockout
                request.session['lockout_time'] = current_time + 60
                return render(request, 'home/timeout.html', {'remaining': 60})
            else:
                messages.error(request, f"Invalid credentials. {remaining_attempts} attempt(s) left.")
                return redirect('/')

    return HttpResponse('404 - Not Found')

def handleLogout(request):
        del request.session['is_logged']
        del request.session["user_id"] 
        logout(request)
        messages.success(request, " Successfully logged out")
        return redirect('home')

#add money form
# def addmoney_submission(request):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user_id = request.session["user_id"]
#             user1 = User.objects.get(id=user_id)
#             addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')
#             add_money = request.POST["add_money"]
#             quantity = request.POST["quantity"]
#             Date = request.POST["Date"]
#             Category = request.POST["Category"]
#             add = Addmoney_info(user = user1,add_money=add_money,quantity=quantity,Date = Date,Category= Category)
#             add.save()
#             paginator = Paginator(addmoney_info1, 4)
#             page_number = request.GET.get('page')
#             page_obj = Paginator.get_page(paginator,page_number)
#             context = {
#                 'page_obj' : page_obj
#                 }
#             return render(request,'home/index.html',context)
#     return redirect('/index')

# def addmoney_submission(request):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user_id = request.session["user_id"]
#             user1 = User.objects.get(id=user_id)

#             add_money = request.POST["add_money"]
#             quantity = request.POST["quantity"]
#             Date = request.POST["Date"]
#             Category = request.POST["Category"]

#             # --- CORRECTION STARTS HERE ---
#             # Convert quantity to a float
#             try:
#                 quantity = float(quantity)
#             except (ValueError, TypeError):
#                 # Handle cases where quantity is not a valid number
#                 messages.error(request, "Please enter a valid amount.")
#                 return redirect('/addmoney')

#             # If the transaction is an expense, convert the quantity to a negative number
#             if add_money == 'Expense':
#                 quantity = -quantity
#             # --- CORRECTION ENDS HERE ---

#             add = Addmoney_info(
#                 user=user1,
#                 add_money=add_money,  # Note: This field is now redundant but kept for consistency
#                 quantity=quantity,
#                 Date=Date,
#                 Category=Category
#             )
#             add.save()

#             # The rest of the code is for rendering the page
#             addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')
#             paginator = Paginator(addmoney_info1, 4)
#             page_number = request.GET.get('page')
#             page_obj = Paginator.get_page(paginator, page_number)
            
#             context = {
#                 'page_obj': page_obj
#             }
#             messages.success(request, "Transaction added successfully!")
#             return render(request, 'home/index.html', context)
#     return redirect('/index')
# def addmoney_update(request,id):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             add  = Addmoney_info.objects.get(id=id)
#             add .add_money = request.POST["add_money"]
#             add.quantity = request.POST["quantity"]
#             add.Date = request.POST["Date"]
#             add.Category = request.POST["Category"]
#             add .save()
#             return redirect("/index")
#     return redirect("/home")   

# =================== Add Money Submission ===================
def addmoney_submission(request):
    if request.session.get('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)

            add_money = request.POST.get("add_money")   # Income / Expense
            quantity = request.POST.get("quantity")
            Date = request.POST.get("Date")
            Category = request.POST.get("Category")

            # Validate amount
            try:
                quantity = float(quantity)
            except (ValueError, TypeError):
                messages.error(request, "Please enter a valid amount.")
                return redirect('/addmoney')

            # Expense should be negative
            if add_money == 'Expense':
                quantity = -quantity

            # Save transaction
            Addmoney_info.objects.create(
                user=user1,
                add_money=add_money,
                quantity=quantity,
                Date=Date,
                Category=Category
            )

            # ================= EMAIL ALERT FOR THIS USER =================
            THRESHOLD_PERCENT = 0.8  # Alert when 80% of income is spent

            # Calculate total income for this user
            total_income = Addmoney_info.objects.filter(
                user=user1, add_money='Income'
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0

            # Calculate total expense
            total_expense = Addmoney_info.objects.filter(
                user=user1, add_money='Expense'
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0

            total_expense = abs(total_expense)  # convert negative expense to positive

            # Send email if threshold reached
            if total_income > 0 and total_expense >= THRESHOLD_PERCENT * total_income:
                try:
                    send_mail(
                        subject="⚠ Income Limit Alert",
                        message=f"""
Hello {user1.username},

You have spent ₹{total_expense} out of your total income ₹{total_income}.

Please manage your spending to avoid exceeding your income.
""",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user1.email],
                        fail_silently=False,  # Set False to catch errors
                    )
                    messages.warning(request, "You are approaching your income limit! Alert email sent.")
                except Exception as e:
                    print(f"Error sending email to {user1.username}: {e}")

            else:
                messages.success(request, "Transaction added successfully!")

            return redirect('/index')

    return redirect('/home')
def addmoney_update(request, id):
    if request.session.get('is_logged'):
        if request.method == "POST":
            try:
                add = Addmoney_info.objects.get(id=id)
                add.add_money = request.POST.get("add_money")
                add.quantity = request.POST.get("quantity")
                add.Category = request.POST.get("Category")

                # Handle empty date
                date_input = request.POST.get("Date")
                if date_input:
                    add.Date = date_input  # valid user input
                else:
                    add.Date = date.today()  # default to today

                add.save()
                messages.success(request, "Transaction updated successfully!")
                return redirect("/index")
            except Addmoney_info.DoesNotExist:
                messages.error(request, "Transaction not found!")
                return redirect("/index")

    return redirect("/home")
def expense_edit(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        return render(request,'home/expense_edit.html',{'addmoney_info':addmoney_info})
    return redirect("/home")  

# def expense_delete(request,id):
#     if request.session.has_key('is_logged'):
#         addmoney_info = Addmoney_info.objects.get(id=id)
#         addmoney_info.delete()
#         return redirect("/index")
#     return redirect("/home")  
def expense_delete(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        addmoney_info.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect("/index")
    return redirect("/home")

def expense_month(request):
    todays_date = datetime.date.today()
    one_month_ago = todays_date-datetime.timedelta(days=30)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        # if addmoney_info.add_money=="Expense":
        return addmoney_info.Category    
    Category_list = list(set(map(get_Category,addmoney)))

    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

#monlthy record
def stats(request):
    if request.session.get('is_logged'):

        todays_date = date.today()
        one_month_ago = todays_date - timedelta(days=30)

        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        records = Addmoney_info.objects.filter(
            user=user1,
            Date__gte=one_month_ago,
            Date__lte=todays_date
        )

        # ✅ Expense always positive
        total_expense = sum(
            abs(i.quantity) for i in records if i.add_money == 'Expense'
        )

        total_income = sum(
            i.quantity for i in records if i.add_money == 'Income'
        )

        # ✅ Initial saved
        raw_saved = total_income - total_expense

        # ✅ Extra spent
        extra_spent = 0
        if raw_saved < 0:
            extra_spent = abs(raw_saved)
            total_saved = 0
            messages.warning(request, "⚠️ Expenses exceeded your income!")
        else:
            total_saved = raw_saved

        # ✅ Target
        target_savings = user1.userprofile.Savings

        # ✅ Target shortage (FINAL CORRECT LOGIC)
        if total_income >= total_expense:
            target_shortage = max(0, target_savings - total_saved)
        else:
            target_shortage = target_savings + extra_spent

        # ✅ Remaining savings
        remaining_savings = target_savings + total_saved

        return render(request, 'home/stats.html', {
            'total_expense': total_expense,
            'total_income': total_income,
            'total_saved': total_saved,
            'extra_spent': extra_spent,
            'target_savings': target_savings,
            'target_shortage': target_shortage,
            'remaining_savings': remaining_savings,
        })

    return redirect('/login')
# def expense_week(request):
#     todays_date = datetime.date.today()
#     one_week_ago = todays_date-datetime.timedelta(days=7)
#     user_id = request.session["user_id"]
#     user1 = User.objects.get(id=user_id)
#     addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
#     finalrep ={}

#     def get_Category(addmoney_info):
#         return addmoney_info.Category
#     Category_list = list(set(map(get_Category,addmoney)))


#     def get_expense_category_amount(Category,add_money):
#         quantity = 0 
#         filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
#         for item in filtered_by_category:
#             quantity+=item.quantity
#         return quantity

#     for x in addmoney:
#         for y in Category_list:
#             finalrep[y]= get_expense_category_amount(y,"Expense")

#     return JsonResponse({'expense_category_data': finalrep}, safe=False) 

def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date - datetime.timedelta(days=7)
    
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'error': 'User not logged in'}, status=401)

    user1 = User.objects.get(id=user_id)

    # ✅ Filter only last 7 days expenses
    addmoney = Addmoney_info.objects.filter(
        user=user1,
        Date__gte=one_week_ago,
        Date__lte=todays_date,
        add_money="Expense"  # Ensure only expense records
    )

    # If no data found
    if not addmoney.exists():
        return JsonResponse({'expense_category_data': {}}, safe=False)

    # ✅ Aggregate total expense per category
    expense_data = (
        addmoney.values('Category')
        .annotate(total_amount=Sum('quantity'))
        .order_by('Category')
    )

    # ✅ Convert queryset to dictionary
    finalrep = {item['Category']: item['total_amount'] for item in expense_data}

    return JsonResponse({'expense_category_data': finalrep}, safe=False)
    

def weekly(request):
    if request.session.get('is_logged'):
        todays_date = date.today()
        one_week_ago = todays_date - timedelta(days=7)

        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        addmoney_info = Addmoney_info.objects.filter(
            user=user1,
            Date__gte=one_week_ago,
            Date__lte=todays_date
        )

        total_expense = sum(
            abs(item.quantity) for item in addmoney_info if item.add_money == 'Expense'
        )

        total_income = sum(
            item.quantity for item in addmoney_info if item.add_money == 'Income'
        )

        saved_this_week = total_income - total_expense

        remaining_savings = user1.userprofile.Savings + saved_this_week

        return render(request, 'home/weekly.html', {
            'sum_expense': total_expense,
            'sum_income': total_income,
            'saved_this_week': saved_this_week,
            'remaining_savings': remaining_savings
        })

    return redirect('/login')
    
def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")

def info_year(request):
    import datetime
    from .models import Addmoney_info, User

    todays_date = datetime.date.today()
    one_year_ago = todays_date - datetime.timedelta(days=365)  # yearly
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user=user1, Date__gte=one_year_ago)

    # get unique categories
    categories = addmoney.values_list('Category', flat=True).distinct()

    finalrep = {}
    for category in categories:
        total = addmoney.filter(Category=category, add_money="Expense").aggregate(total=Sum('quantity'))['total'] or 0
        finalrep[category] = total

    return JsonResponse({'expense_category_data': finalrep})
def info(request):
    return render(request,'home/info.html')
    


def export_history_csv(request):
    if not request.session.has_key('is_logged'):
        return redirect('home')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)

    # Optional: handle date filtering if query params exist
    fromdate = request.GET.get('fromdate')
    todate = request.GET.get('todate')

    if fromdate and todate:
        transactions = Addmoney_info.objects.filter(user=user, Date__range=[fromdate, todate]).order_by('-Date')
    else:
        transactions = Addmoney_info.objects.filter(user=user).order_by('-Date')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['What you added', 'Amount', 'Category', 'Date'])

    for t in transactions:
        writer.writerow([t.add_money, t.quantity, t.Category, t.Date])

    return response    

#dashboard
# Dashboard view
def dashboard(request):
    user = request.user
    process_recurring_expenses(user)  # Add recurring transactions automatically

    # Get all transactions for the user
    transactions = Addmoney_info.objects.filter(user=user).order_by('-Date')

    # Pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Total Income & Expense
    total_income = transactions.filter(add_money='Income').aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Use Abs() to make expense positive
    total_expense = transactions.filter(add_money='Expense').aggregate(
        total=Sum(Abs('quantity'))
    )['total'] or 0

    # Current balance
    current_balance = total_income - total_expense

    # Weekly / Monthly / Yearly Expenses
    today = date.today()

    def expense_by_period(start_date):
        qs = transactions.filter(add_money='Expense', Date__gte=start_date)
        data = qs.values('Category').annotate(total=Sum(Abs('quantity')))
        return {item['Category']: item['total'] for item in data}

    weekly_expense_json = json.dumps(expense_by_period(today - timedelta(days=7)))
    monthly_expense_json = json.dumps(expense_by_period(today.replace(day=1)))
    yearly_expense_json = json.dumps(expense_by_period(today.replace(month=1, day=1)))

    context = {
        'page_obj': page_obj,
        'total_income': total_income,
        'total_expense': total_expense,        # This will now be positive
        'current_income': current_balance,
        'weekly_expense_json': weekly_expense_json,
        'monthly_expense_json': monthly_expense_json,
        'yearly_expense_json': yearly_expense_json,
    }

    return render(request, 'home/dashboard.html', context)
# def dashboard(request):
#     if not request.session.get('is_logged'):
#         return redirect('home')

#     user = User.objects.get(id=request.session['user_id'])
#     addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
#     paginator = Paginator(addmoney_info, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # Calculate total income, expense, balance
#     total_expense = sum([abs(x.quantity) for x in addmoney_info if x.add_money=='Expense'])
#     total_income = sum([x.quantity for x in addmoney_info if x.add_money=='Income'])
#     current_income = total_income - total_expense 

#     # Weekly
#     one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
#     weekly_data = addmoney_info.filter(Date__gte=one_week_ago, add_money='Expense')
#     weekly_expense = {}
#     for item in weekly_data:
#         weekly_expense[item.Category] = weekly_expense.get(item.Category, 0) + abs(item.quantity)

#     # Monthly
#     one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
#     monthly_data = addmoney_info.filter(Date__gte=one_month_ago, add_money='Expense')
#     monthly_expense = {}
#     for item in monthly_data:
#         monthly_expense[item.Category] = monthly_expense.get(item.Category, 0) + abs(item.quantity)

#     # Yearly
#     one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
#     yearly_data = addmoney_info.filter(Date__gte=one_year_ago, add_money='Expense')
#     yearly_expense = {}
#     for item in yearly_data:
#         yearly_expense[item.Category] = yearly_expense.get(item.Category, 0) + abs(item.quantity)

#     context = {
#         'page_obj': page_obj,
#         'total_expense': total_expense,
#         'total_income': total_income,
#         'current_income': current_income,
#         'weekly_expense_json': json.dumps(weekly_expense),
#         'monthly_expense_json': json.dumps(monthly_expense),
#         'yearly_expense_json': json.dumps(yearly_expense),
#     }

#     return render(request, 'home/dashboard.html', context)

#this is recurring expanse

from datetime import date, timedelta
from .models import Addmoney_info, RecurringExpense

def process_recurring_expenses(user):
    """
    Automatically add recurring transactions for the user if the next due date has arrived.
    """
    today = date.today()
    recurring_items = RecurringExpense.objects.filter(user=user)

    for item in recurring_items:
        if item.next_due_date <= today:
            # Determine if Income or Expense and fix the sign
            if item.category == 'Salary':
                add_money_type = 'Income'
                amount_to_add = item.amount  # Income stays positive
            else:
                add_money_type = 'Expense'
                amount_to_add = -abs(item.amount)  # Expenses stored as negative

            # Add transaction to Addmoney_info
            Addmoney_info.objects.create(
                user=user,
                add_money=add_money_type,
                quantity=amount_to_add,
                Category=item.category,
                Date=item.next_due_date
            )

            # Update next_due_date based on frequency
            if item.frequency == 'Daily':
                item.next_due_date += timedelta(days=1)
            elif item.frequency == 'Weekly':
                item.next_due_date += timedelta(weeks=1)
            elif item.frequency == 'Monthly':
                month = item.next_due_date.month + 1
                year = item.next_due_date.year
                day = item.next_due_date.day
                if month > 12:
                    month = 1
                    year += 1
                # Avoid invalid dates (like Feb 30)
                try:
                    item.next_due_date = date(year, month, day)
                except:
                    if month == 12:
                        item.next_due_date = date(year, 12, 31)
                    else:
                        item.next_due_date = date(year, month + 1, 1) - timedelta(days=1)
            elif item.frequency == 'Yearly':
                item.next_due_date = date(item.next_due_date.year + 1, item.next_due_date.month, item.next_due_date.day)

            item.save()

# add recuuring views.py
def add_recurring(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        RecurringExpense.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            amount=request.POST.get('amount'),
            category=request.POST.get('category'),
            frequency=request.POST.get('frequency'),
            next_due_date=request.POST.get('next_due_date')
        )
        return redirect('dashboard')

    return render(request, 'home/add_recurring.html')

# ============================================
# OCR BILL UPLOAD FUNCTION - FULLY CORRECTED
# ============================================
import pytesseract
from PIL import Image, ImageOps
import re
from datetime import datetime
from django.shortcuts import redirect
from .models import Addmoney_info, User

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_upload(request):
    # -----------------------------
    # CHECK USER LOGGED IN
    # -----------------------------
    if not request.session.get('is_logged'):
        return redirect('login')

    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    # -----------------------------
    # HANDLE IMAGE UPLOAD
    # -----------------------------
    if request.method == "POST" and request.FILES.get("bill_image"):
        image_file = request.FILES["bill_image"]

        try:
            # --- IMAGE PREPROCESSING ---
            img = Image.open(image_file)
            img = ImageOps.exif_transpose(img)  # fix rotation
            img = img.convert('L')               # grayscale
            img = img.resize((img.width * 2, img.height * 2))  # improve OCR

            # --- OCR ---
            text = pytesseract.image_to_string(img, config='--psm 3')
            print("OCR TEXT:\n", text)

        except Exception as e:
            print("❌ Image processing error:", e)
            return redirect('index')

        # -----------------------------
        # AMOUNT DETECTION
        # -----------------------------
        amount = 0
        try:
            lines = text.split('\n')
            # Look for total/amount paid/grand total first
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in ["total", "amount paid", "grand total"]):
                    nums = re.findall(r'\d+[.,]?\d*', line_lower)
                    if nums:
                        amount = float(nums[-1].replace(',', '.'))
                        break

            # Fallback: use the last valid number in the text
            if amount == 0:
                all_numbers = re.findall(r'\d+[.,]?\d*', text)
                valid_numbers = []
                for num in all_numbers:
                    try:
                        val = float(num.replace(',', '.'))
                        if 1 < val < 100000:
                            valid_numbers.append(val)
                    except:
                        continue
                if valid_numbers:
                    amount = valid_numbers[-1]  # take the last number assuming it's total
        except Exception as e:
            print("❌ Amount detection error:", e)
            amount = 0

        print("💰 Amount detected:", amount)

        # -----------------------------
        # DATE DETECTION
        # -----------------------------
        bill_date = datetime.today().date()  # default
        try:
            # Match numeric formats
            date_patterns = [
                r'\d{2}[/-]\d{2}[/-]\d{4}',  # 23/03/2026
                r'\d{2}[/-]\d{2}[/-]\d{2}',  # 23/03/26
                r'\d{4}[/-]\d{2}[/-]\d{2}',  # 2026-03-23
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                        try:
                            bill_date = datetime.strptime(match.group(), fmt).date()
                            break
                        except:
                            continue
                    break

            # Match month names like "March 23, 2026"
            if bill_date == datetime.today().date():
                date_match = re.search(
                    r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4})',
                    text, flags=re.IGNORECASE
                )
                if date_match:
                    try:
                        bill_date = datetime.strptime(date_match.group(), "%d %b %Y").date()
                    except:
                        try:
                            bill_date = datetime.strptime(date_match.group(), "%d %B %Y").date()
                        except:
                            pass
        except Exception as e:
            print("❌ Date detection error:", e)

        print("📅 Date detected:", bill_date)

        # -----------------------------
        # CATEGORY DETECTION
        # -----------------------------
        category = "Other"
        try:
            text_lower = text.lower()
            if any(word in text_lower for word in ["petrol", "fuel", "diesel", "gas"]):
                category = "Fuel"
            elif any(word in text_lower for word in ["bus", "ticket", "uber", "ola", "taxi",
                                                     "train", "flight", "airport", "travel",
                                                     "metro", "auto", "fare"]):
                category = "Travel"
            elif any(word in text_lower for word in ["tea", "coffee", "hotel", "restaurant", "food", "snack", "canteen"]):
                category = "Food"
            elif any(word in text_lower for word in ["medical", "pharmacy", "hospital", "doctor", "clinic"]):
                category = "Hospital"
            elif any(word in text_lower for word in ["purchase", "buy", "shop", "store", "supermarket"]):
                category = "Purchase"
            elif any(word in text_lower for word in ["fee", "tuition", "college", "school", "education"]):
                category = "Fees"
        except Exception as e:
            print("❌ Category detection error:", e)
            category = "Other"

        print("🏷️ Category detected:", category)

        # -----------------------------
        # SAVE TO DATABASE
        # -----------------------------
        try:
            Addmoney_info.objects.create(
                user=user,
                quantity=amount,
                add_money="Expense",
                Category=category,
                Date=bill_date
            )
            print("✅ Transaction saved successfully!")
        except Exception as e:
            print("❌ Database save error:", e)

    return redirect('index')