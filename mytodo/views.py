from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'mytodo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'mytodo/signupuser.html', {'form':UserCreationForm()})
    else:
        # Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], request.POST['password1'])
                user.set_password(request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError: # Error during save
                return render(request, 'mytodo/signupuser.html', {'form':UserCreationForm(), 'error':'Username is already been taken!! Choose a new user name'})
        else:
            # Mismatch error back to user
            return render(request, 'mytodo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match!'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'mytodo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'mytodo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username/Password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST': # Do not logout only if POST request - browser may do GET for <a> to improve load experience
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    #todos = Todo.objects.all() # Get for all users
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True) # only users
    return render(request, 'mytodo/currenttodos.html', {'todos':todos})


@login_required
def completedtodos(request):
    #todos = Todo.objects.all() # Get for all users
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted') # only users
    return render(request, 'mytodo/completedtodos.html', {'todos':todos})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'mytodo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False) # Create todo object but do not save in DB
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'mytodo/createtodo.html', {'form':TodoForm(), 'error':'Bad data, try again!'})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user) # only users
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'mytodo/viewtodo.html', {'form':form, 'todo':todo})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
        except ValueError:
            return render(request, 'mytodo/createtodo.html', {'form':TodoForm(), 'error':'Bad info'})
        return redirect('currenttodos')


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
