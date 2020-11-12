from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .signals import profile_update_signal
from .forms import RegisterForm, UserUpdateForm, ProfileForm, SearchForm
from .models import Profile
from facebook.apps.posts.models import Post


def register_view(request):
	context = {}
	template_name = "accounts/register.html"
	if request.method == "POST":
		print(request.POST)
		data = request.POST.copy()
		username = data.pop('username')[0]
		email = data.pop('email')[0]
		password1 = data.pop('password1')[0]
		password2 = data.pop('password2')[0]

		if User.objects.filter(username= username):
			context['error'] = 'Username already exists'
			return render(request, template_name, context)
		elif User.objects.filter(email= email):
			context['error'] = 'Email already registered'
			return render(request, template_name, context)
		elif password1 != password2:
			context['error'] = 'Password mismatch'
			return render(request, template_name, context)
		else:
			new_user = User.objects.create(username=username, email = email)
			new_user.set_password(password1)
			new_user.save()
			create_profile(new_user)
			messages.success(request, "Account successfully created!")
			return redirect("login")

	else:
		register_form = RegisterForm()

	context["form"] = register_form
	return render(request, template_name, context)

def create_profile(user):
	p = Profile(user=user)
	p.save()

@login_required
def profile_view(request):
	template_name = "accounts/profile.html"
	context = get_posts(False, request.user)
	context["content"] = True
	return render(request, template_name, context)

@login_required
def display_profile(request, user_id):
	template_name = "accounts/profile.html"
	user = User.objects.get(pk=user_id)
	context = get_posts(False, user)
	if user.pk == request.user.pk:
		return redirect("profile")
	else:
		context["content"] = False
		context["user"] = user
		return render(request, template_name, context)


@login_required
def profile_archived_view(request):
	template_name = "accounts/profile-archived.html"
	context = get_posts(True, request.user)
	return render(request, template_name, context)

def get_posts(status, user):
	posts = Post.objects.get_posts(status)
	posts = posts.filter(user=user)
	liked = []
	like_no = []

	for post in posts:
		liked.append(check_like(user, post)[0])
		like_no.append(check_like(user, post)[1])

	master_list = zip(posts, liked, like_no)
	context = {
		"master":master_list
	}
	return context

def check_like(user, post):
	likes = post.likes
	if user in likes.all():
		return True, len(likes.all())
	return False, len(likes.all())

@login_required
def update_view(request):
	if request.method == "POST":
		# old_img = request.user.profile.image
		user_form = UserUpdateForm(request.POST, instance=request.user)

		profile_form = ProfileForm(
			request.POST,
			request.FILES,
			instance=request.user.profile
		)

		if user_form.is_valid() and profile_form.is_valid():

			user_form.save()
			profile_form.save()

			# new_img = request.user.profile.image

			# profile_update_signal.send(
			# 	sender=Profile,
			# 	old_img=old_img,
			# 	new_img=new_img
			# )
			messages.success(request, "Your profile has been updated.")
			return redirect("profile")
	else:
		user_form = UserUpdateForm(instance=request.user)
		profile_form = ProfileForm(instance=request.user.profile)

	template_name = "accounts/update.html"
	context = {
		"user_form":user_form,
		"profile_form":profile_form
	}
	return render(request, template_name, context)

@login_required
def delete_view(request):
	if request.method == "POST":
		username = request.user.username
		user = User.objects.get(username=username)
		user.delete()
		messages.error(request, f"{user.username}'s account has been deleted.")
		return redirect("register")
	template_name = "accounts/delete.html"
	context = {}
	return render(request, template_name, context)

@login_required
def search_users_view(request):
	template_name = "accounts/search.html"
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data["name"]
			users = User.objects.filter(username__icontains=username)
			context={
				"form": form,
				"users": users
			}
			return render(request, template_name, context)
	else:
		form = SearchForm()
		context={
			"form": form
		}
		return render(request, template_name, context)

