from django.contrib import admin
from stories.models import Story, UserProfile

class StoryAdmin(admin.ModelAdmin):
	fieldsets = [
		('Story', {'fields': ['title','url','points','description']
			}),
		('Moderator', {
			'classes': ['collapse'],
			'fields': ['moderator']
			}),
		('Change History', {
			'classes': ['collapse'],
			'fields': ['created_at','updated_at']
			}), 
		('Voters', {
			'classes': ['collapse'],
			'fields': ['voters']
			})
	]

	readonly_fields = ('created_at','updated_at','voters')

	list_display = ['__unicode__','domain','moderator','created_at','updated_at']
	list_filter = ['created_at','updated_at']
	search_fields = ['title','moderator__username','moderator__first_name','moderator__last_name']

admin.site.register(Story, StoryAdmin)
admin.site.register(UserProfile)