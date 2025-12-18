from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as a_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from .models import LoanApplication
from ai_model import predict_loan_status,explain_result

User = get_user_model()


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')

        a_login(request, user)
        return redirect("home")

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "register.html")


def home(request):
    result = None
    reasons = None  
    if request.method == "POST" and "loan_form" in request.POST:
        try:
            input_data = {
                'Gender': request.POST.get('Gender'),
                'Married': request.POST.get('Married'),
                'Dependents': request.POST.get('Dependents'),
                'Education': request.POST.get('Education'),
                'Self_Employed': request.POST.get('Self_Employed'),
                'ApplicantIncome': float(request.POST.get('ApplicantIncome', 0)),
                'CoapplicantIncome': float(request.POST.get('CoapplicantIncome', 0)),
                'LoanAmount': float(request.POST.get('LoanAmount', 0))/1000,
                'Loan_Amount_Term': float(request.POST.get('Loan_Amount_Term', 360)),
                'Credit_History': float(request.POST.get('Credit_History', 1)),
                'Property_Area': request.POST.get('Property_Area')
            }

            result = predict_loan_status(input_data)
            reasons = explain_result(input_data)
            
            LoanApplication.objects.create(
                user=request.user,
                applicant_income=input_data['ApplicantIncome'],
                coapplicant_income=input_data['CoapplicantIncome'],
                loan_amount=input_data['LoanAmount'],
                credit_history=input_data['Credit_History'],
                property_area=input_data['Property_Area'],
                education=input_data['Education'],
                employment=input_data['Self_Employed'],
                prediction=result
            )

        except Exception as e:
            result = f"Error: {e}"

    users = User.objects.all()

    loans = LoanApplication.objects.filter(user=request.user).order_by("-created_at")

    total_users = User.objects.count()
    total_loans = LoanApplication.objects.count()
    approved = LoanApplication.objects.filter(prediction="Approved").count()
    rejected = LoanApplication.objects.filter(prediction="Rejected").count()

    return render(request, "home.html", {
        "result": result,
        "reasons":reasons,
        "users": users,
        "loans": loans,
        "total_users": total_users,
        "total_loans": total_loans,
        "approved": approved,
        "rejected": rejected,
    })


def edit_user(request, id):
    user_obj = get_object_or_404(User, id=id)

    if request.method == "POST":
        user_obj.username = request.POST.get("username")
        user_obj.email = request.POST.get("email")
        user_obj.save()

        messages.success(request, "User updated successfully!")
        return redirect("home")

    return render(request, "edit_user.html", {"user_obj": user_obj})

def delete_user(request, id):
    user_obj = get_object_or_404(User, id=id)
    user_obj.delete()

    messages.success(request, "User deleted successfully!")
    return redirect("home")


def logout(request):
    auth_logout(request)
    return redirect("login")


@login_required
def loan_prediction_view(request):
    result = None
    
    if request.method == 'POST':
        try:
            input_data = {
                'Gender': request.POST.get('Gender'),
                'Married': request.POST.get('Married'),
                'Dependents': request.POST.get('Dependents'),
                'Education': request.POST.get('Education'),
                'Self_Employed': request.POST.get('Self_Employed'),
                'ApplicantIncome': float(request.POST.get('ApplicantIncome', 0)),
                'CoapplicantIncome': float(request.POST.get('CoapplicantIncome', 0)),
                'LoanAmount': float(request.POST.get('LoanAmount', 0)),
                'Loan_Amount_Term': float(request.POST.get('Loan_Amount_Term', 1)),
                'Credit_History': float(request.POST.get('Credit_History', 1)),
                'Property_Area': request.POST.get('Property_Area')
            }

            result = predict_loan_status(input_data)
        except Exception as e:
            result = f"Error: {e}"

    return render(request, 'loan_prediction.html', {"result": result})

@login_required
def dashboard(request):
    total_users = User.objects.count()
    total_loans = LoanApplication.objects.count()

    approved = LoanApplication.objects.filter(prediction="Approved").count()
    rejected = LoanApplication.objects.filter(prediction="Rejected").count()

    return render(request, "dashboard.html", {
        "total_users": total_users,
        "total_loans": total_loans,
        "approved": approved,
        "rejected": rejected,
    })

@login_required
def history(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "history.html", {
        "loans": loans
    })

@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, "users_list.html", {"users": users})
