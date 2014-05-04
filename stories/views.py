from datetime import datetime

from stories.models import Story, UserProfile
from stories.forms import StoryForm, UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.timezone import utc


def score(story, gravity=1.8, timebase=120):
	points = (story.points - 1)**0.8
	now = datetime.utcnow().replace(tzinfo=utc)
	age = int((now - story.created_at).total_seconds())/60

	return points/(age+timebase)**gravity

def top_stories(top=180, consider=1000):
	latest_stories = Story.objects.all().order_by('-created_at')[:consider]
	rank_stories = sorted([(score(story), story) for story in latest_stories], reverse=True)

	return [story for _, story in rank_stories][:top]

def index(request):
	stories = top_stories(top=50)
	context_dict = {'stories': stories}
	context_dict['user'] = request.user

	if request.user.is_authenticated():
		liked_stories = request.user.liked_stories.filter(id__in=[story.id for story in stories])
	else:
		liked_stories = []

	context_dict['liked_stories'] = liked_stories

	return render(request, 'tidder/index.html', context_dict)

@login_required
def story(request):
	if request.method == "POST":
		form = StoryForm(request.POST)
		if form.is_valid():
			story = form.save(commit=False)
			story.moderator = request.user
			story.save()
			return HttpResponseRedirect('/')
	else:
		form = StoryForm()

	return render(request, 'tidder/story.html', {'form': form})

def user_login(request):
	context = RequestContext(request)
	context_dict = {}

	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				context_dict['disabled_account'] = True
				return render_to_response('tidder/login.html', {}, context)
		else:
			print "invalid login: {0}, {1}".format(username,password)
			context_dict['bad_details'] = True
			return render_to_response('tidder/login.html', context_dict, context)
	else:
		return render_to_response('tidder/login.html', context_dict, context)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')

def register(request):
	context = RequestContext(request)
	registered = False
	context_dict = {}

	if request.method == "POST":
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True
			return HttpResponseRedirect('/login/')
		else:
			print user_form.errors, profile_form.errors
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	context_dict['user_form'] = user_form
	context_dict['profile_form'] = profile_form
	context_dict['registered'] = registered

	return render_to_response('tidder/register.html', context_dict, context)

@login_required
def vote(request):
	# check to make sure user already hasnt voted before saving
	story = get_object_or_404(Story, pk=request.POST.get('story'))
	story.points += 1
	story.save()
	user = request.user
	user.liked_stories.add(story)
	user.save()
	return HttpResponse()

def story_detail(request, story_id):
	context_dict = {}
	context_dict['user'] = request.user

	story = get_object_or_404(Story, pk=story_id)
	context_dict['story'] = story

	return render(request, 'tidder/detail.html', context_dict)

@login_required
def user_profile(request, user):
	context_dict = {}

	u = User.objects.get(username=user)

	try:
		up = UserProfile.objects.get(user=u)
	except:
		up = None
	
	context_dict['user_profile'] = u
	context_dict['user_profile_info'] = up

	return render(request, 'tidder/profile.html', context_dict)