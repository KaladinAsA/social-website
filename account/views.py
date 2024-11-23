from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action

# Views for managing user accounts and actions.

def user_login(request):
    """
    Handle user login functionality.
    Authenticate the user with provided username and password.
    If successful, log the user in and redirect accordingly.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                login(request, user)
                if user.is_active:
                    return HttpResponse('Login successful')
                else:
                    return HttpResponse('Sorry your account is not activated')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def dashboard(request):
    """
    Render the user dashboard showing recent actions.
    Actions are filtered to include only those from followed users.
    """
    # Exclude current user's actions
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # Filter actions from followed users
        actions = actions.filter(user_id__in=following_ids)
    # Optimize query performance
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html', {'section': "dashboard", 'actions': actions})

def register(request):
    """
    Handle user registration.
    Create a new user account and associated profile upon successful registration.
    """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Save the new user
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            # Create a profile for the new user
            Profile.objects.create(user=new_user)
            # Log the action
            create_action(new_user, 'has created an account')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def edit(request):
    """
    Handle profile editing for logged-in users.
    Allows users to update their personal details and profile picture.
    """
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def user_list(request):
    """
    Display a list of active users on the platform.
    """
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})

@login_required
def user_detail(request, username):
    """
    Display details of a specific user.
    """
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})

@require_POST
@login_required
def user_follow(request):
    """
    Handle follow/unfollow actions for users.
    """
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
