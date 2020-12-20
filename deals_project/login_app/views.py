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
            return HttpResponseRedirect(reverse('login_app:password_reset'))

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
            print(f"Valid password request: {post_user}")
            return HttpResponseRedirect(reverse('login_app:password_reset'))

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
                messages.error(request, f"Invalid password reset attempt.") 
                return render(request, 'login_app/password_reset.html')
                
            user = prr.user
            user.set_password(password)
            user.save()
            messages.success(request, f"Password successfully reset.") 
            return HttpResponseRedirect(reverse('login_app:login'))
        else:
            print("Passwords not matching.")
            messages.error(request, f"Passwords did not match.") 
            return render(request, 'login_app/password_reset.html')

    return render(request, 'login_app/password_reset.html')


@login_required
def password_change(request):
    if request.method == "POST":
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']

        if old_password != new_password:
            try:
                user = Users.objects.get(user=request.user)
            except:
                print("Invalid password reset attempt.")
                messages.error(request, f"Invalid password reset attempt.") 
                return HttpResponseRedirect(reverse('login_app:edit_account'))
                
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password successfully changed.") 
            return HttpResponseRedirect(reverse('login_app:edit_account'))
        else:
            print("Same passwords.")
            messages.error(request, "Password cannot be the same as the current.") 
            return HttpResponseRedirect(reverse('login_app:edit_account'))


@login_required
def email_change(request):
    return HttpResponseRedirect(reverse('login_app:edit_account'))


def register(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_name = request.POST['user']
        email = request.POST['email']
        if password == confirm_password:
            if User.objects.filter(username=user_name).exists():
                context = {
                    'error': 'User already exists'
                }
                return render(request, 'login_app/register.html', context)

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


@login_required
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
                messages.success(request, "User successfully deleted.") 
                return HttpResponseRedirect(reverse('login_app:login'))
            else:
                print("fail delete")
                messages.error(request, "Could not delete user, please try again.") 
        else:
            print("fail delete")
            messages.error(request, "Please type DELETE to confirm as prompted.") 

    return HttpResponseRedirect(reverse('login_app:edit_account'))

