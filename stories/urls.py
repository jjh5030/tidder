from django.conf.urls import patterns, include, url
from stories import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^post/$', views.story, name='story'),
	url(r'^login/', views.user_login, name='login'),
	url(r'^logout/', views.user_logout, name='logout'),
	url(r'^register/', views.register, name='register'),
	url(r'^vote/', views.vote, name='vote'),
	url(r'^post/(?P<story_id>\d+)/$', views.story_detail, name='story_detail'),
	url(r'^user_profile/(?P<user>\w+)/$', views.user_profile, name='user_profile'),
	url(r'^results_page/(?P<page_number>\d+)/$', views.index, name='index'),
)
