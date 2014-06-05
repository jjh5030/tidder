from datetime import datetime

from stories.models import Story, UserProfile, Comment
from stories.forms import StoryForm, UserForm, UserProfileForm, CommentForm

from django.core.urlresolvers import reverse

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

def top_stories(top=25, consider=1000):
	latest_stories = Story.objects.all().order_by('-created_at')[:consider]
	rank_stories = sorted([(score(story), story) for story in latest_stories], reverse=True)

	return [story for _, story in rank_stories][:top]

def page_stories(start_point=0, results=25, consider=1000):
	latest_stories = Story.objects.all().order_by('-created_at')[:consider]
	rank_stories = sorted([(score(story), story) for story in latest_stories], reverse=True)
	list_start = (int(start_point)*int(results))-int(results) + 1
	list_end = list_start+int(results)

	#print "results: %s %s" % (list_start, list_end)

	return [story for _, story in rank_stories][list_start:list_end]

def build_paginator(page_number, adjacent_pages=5):
	start_page = 1
	article_count = Story.objects.count()

	if article_count < 1000:
		end_page = (article_count//25) + 1
	else:
		end_page = 1000/25

	page_numbers = [n for n in range(start_page, end_page+1)]
	page_range_show = [n for n in range(page_number - adjacent_pages, page_number + adjacent_pages) if n in page_numbers]

	if page_number == 1:
		has_previous = False
	else:
		has_previous = True

	if page_number == end_page:
		has_next = False
	else:
		has_next = True

	paginator_results = {
		'start_page': start_page, 
		'end_page': end_page,
		'current_page': page_number,
		'page_numbers': page_numbers,
		'next': page_number + 1,
		'previous': page_number - 1,
		'has_next': has_next,
		'has_previous': has_previous,
		'page_range_show': page_range_show,
		'show_first': 1 not in page_numbers,
		'show_last': page_number not in page_numbers,
	}

	#print paginator_results
	return paginator_results

def index(request, page_number=1):
	if int(page_number) == 1:
		stories = top_stories(top=25)
	else:
		stories = page_stories(start_point=int(page_number))

	context_dict = {'stories': stories}
	context_dict['user'] = request.user

	if request.user.is_authenticated():
		liked_stories = request.user.liked_stories.filter(id__in=[story.id for story in stories])
	else:
		liked_stories = []

	context_dict['liked_stories'] = liked_stories
	context_dict['list_start'] = (int(page_number)*int(25))-int(25) + 1 
	context_dict['show_paginator'] = True
	context_dict['paginator_details'] = build_paginator(page_number=int(page_number))

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
	# check to make sure user already hasnt voted before saving, JIC
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
	
	if request.method == "POST":
		form = CommentForm(data=request.POST)

		if form.is_valid():
			temp = form.save(commit=False)
			parent = form['parent'].value()

			#print 'parent', parent
			
			if parent == '' or parent is None:
				#Set a blank path then save it to get an ID
				temp.path = ''
				temp.story_id = story
				temp.comment_moderator = request.user
				temp.save()
				temp.path = temp.id
			else:
				#Get the parent node
				node = Comment.objects.get(id=parent)

				#Max 5 levels deep
				if node.depth < 6:
					temp.depth = node.depth + 1
				else:
					temp.depth = 5

				temp.path = node.path
				temp.story_id = story
				temp.comment_moderator = request.user
				
				#Store parents path then apply comment ID
				temp.save()
				temp.path += ',' + str(temp.id)
				
			#Final save for parents and children
			temp.save()
			context_dict['form'] = form

			# After successful submission and processing of a web form
			return HttpResponseRedirect(reverse('story_detail', args=(story_id,)))

	else:
		context_dict['form'] = CommentForm()

	# may need to do the sorting in python since the database will treat the column as a string 
	# I believe, so 10 will come before 2

	try:
		comment_tree = Comment.objects.filter(story_id=story).order_by('path')
		context_dict['comment_tree'] = [comment for comment in comment_tree]

		#for comment in comment_tree:
		#	print comment.id, comment.path

	except:
		context_dict['comment_tree'] = []    

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