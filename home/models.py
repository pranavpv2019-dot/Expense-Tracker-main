from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Category choices
SELECT_CATEGORY_CHOICES = [
    ("Food","Food"),
    ("Travel","Travel"),
    ("Shopping","Shopping"),
    ("Necessities","Necessities"),
    ("Salary","Salary"),
    ("Entertainment","Entertainment"),
    ("Other","Other")
]

# Expense/Income choices
ADD_EXPENSE_CHOICES = [
    ("Expense","Expense"),
    ("Income","Income")
]

# Profession choices
PROFESSION_CHOICES =[
    ("Employee","Employee"),
    ("Business","Business"),
    ("Student","Student"),
    ("Other","Other")
]

class Addmoney_info(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    add_money = models.CharField(max_length=10, choices=ADD_EXPENSE_CHOICES)
    quantity = models.BigIntegerField()
    Date = models.DateField(default=now)
    Category = models.CharField(max_length=20, choices=SELECT_CATEGORY_CHOICES, default='Food')

    class Meta:
        db_table = 'addmoney'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True)
    income = models.FloatField(default=0)
    Savings = models.FloatField(default=0)
    profile_image = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return self.user.username

class RecurringExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=50)

    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    ]

    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_due_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)  # ✅ fixed

    def __str__(self):
        return self.title
class BillOCR(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bills/')
    extracted_text = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    bill_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"