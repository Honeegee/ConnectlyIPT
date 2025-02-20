from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = 'Creates the Admin group and optionally assigns users to it'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='*', type=str, help='Usernames to add to Admin group')

    def handle(self, *args, **options):
        # Create Admin group if it doesn't exist
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Admin group'))
        else:
            self.stdout.write('Admin group already exists')

        # Add specified users to Admin group
        for username in options['usernames']:
            try:
                user = User.objects.get(username=username)
                user.groups.add(admin_group)
                self.stdout.write(self.style.SUCCESS(f'Added {username} to Admin group'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
