from django.shortcuts import render, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from . models import PasswordResetRequest
from django.contrib.auth.decorators import login_required
import django_rq
from . messaging import email_message


def login(request):
    context = {}

    if request.method == "POST":
        user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
        if user:
            dj_login(request, user)
            return HttpResponseRedirect(reverse('deals_app:base'))
        else:
            context = {
                'error': 'Bad username or password.'
            }
    return render(request, 'login_app/login.html', context)


def logout(request):
    dj_logout(request)
    return HttpResponseRedirect(reverse('deals_app:base'))


def request_password_reset(request):
    if request.method == "POST":
        user = None
        post_user = request.POST['email']
        try:
            user = User.objects.get(email=post_user)
        except: 
            messages.success(request, f"An email will be sent to {request.POST['email']} if an account exists. ") 
            print(f"Invalid password request: {post_user}")
            return HttpResponseRedirect(reverse('deals_app:base'))

        if user:
            prr = PasswordResetRequest()
            prr.user = user
            prr.save()
 
            django_rq.enqueue(email_message, {
               'token' : prr.token,
               'email' : prr.user.email,
            })
            #Print(prr)
            messages.success(request, f"An email will be sent to {prr.user.email} if an account exists. ") 
            print(f"Invalid password request: {post_user}")
            return HttpResponseRedirect(reverse('deals_app:base'))

    return render(request, 'login_app/request_password_reset.html')


def password_reset(request):
    if request.method == "POST":
        post_user = request.POST['user']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        token = request.POST['token']

        if password == confirm_password:
            try:
                prr = PasswordResetRequest.objects.get(token=token)
                prr.save()
            except:
                print("Invalid password reset attempt.")
                return render(request, 'login_app/password_reset.html')
                
            user = prr.user
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse('login_app:login'))

    return render(request, 'login_app/password_reset.html')


def register(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_name = request.POST['user']
        email = request.POST['email']
        if password == confirm_password:
            if User.objects.create_user(user_name, email, password):
                return HttpResponseRedirect(reverse('login_app:login'))
            else:
                context = {
                    'error': 'Could not create user account - please try again.'
                }
        else:
            context = {
                'error': 'Passwords did not match. Please try again.'
            }

    return render(request, 'login_app/register.html', context)

def edit_account(request):
    print('account view!')
    context = {}
    return render(request, 'login_app/edit.html', context)



@login_required
def delete_account(request):
    if request.method == "POST":
        if request.POST['confirm_deletion'] == "DELETE":            
            user = authenticate(request, username=request.user.username, password=request.POST['password'])
            if user:
                print(f"Deleting user {user}")
                user.delete()
                return HttpResponseRedirect(reverse('login_app:login'))
            else:
                print("fail delete")

    return render(request, 'login_app/delete_account.html')

