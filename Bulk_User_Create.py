from __future__ import print_function

# Setup the Django environment so we can access our models
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tidder.settings')

import sys

from django.utils.timezone import utc
from django.contrib.auth.models import User

from stories.models import Story

def main():
	users = []

	for i in range(100):
		user = User(username='user%d' % i,
					email='user%d@mydomain.com' % i,
					password='hashedPasswordStringPastedHereFromStep1!')
		users.append(user)

	User.objects.bulk_create(users)

if __name__ == '__main__':
    main()
