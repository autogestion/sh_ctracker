from random import randint
from random import sample
from string import ascii_lowercase

from django.core.management.base import BaseCommand

from socialhome.users.models import Profile
from ctracker.models import Claim, Organization


class Command(BaseCommand):
    help = 'Randomly fill organizations with claims'

    def handle(self, *args, **options):

        broadcaster = Profile.objects.get(user__username='acts')
        orgs = Organization.objects.all()
        for org in orgs:
            for x in range(randint(0,9)):
                claim = Claim(
                    organization=org,
                    servant=''.join(sample(ascii_lowercase,randint(5,10))).capitalize(),
                    text=''.join(sample(ascii_lowercase + ' ',randint(5,25))).capitalize(),
                    author=broadcaster
                )
                claim.save()
