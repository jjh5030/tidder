from urlparse import urlparse

from django.db import models
from django.contrib.auth.models import User

class Story(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	url = models.URLField()
	points = models.IntegerField(default=1)
	moderator = models.ForeignKey(User, related_name='moderated_stories')
	voters = models.ManyToManyField(User, related_name='liked_stories')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@property
	def domain(self):
		return urlparse(self.url).netloc

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name_plural = "Stories"