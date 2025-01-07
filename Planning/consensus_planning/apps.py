from django.apps import AppConfig


class ConsensusPlanningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consensus_planning'

    def ready(self):
        from django.contrib.auth.models import Group  # Import the Group model inside ready()
        
        # Create 'Uploader', 'Editor', and 'ViewPage' groups if they don't exist
        Group.objects.get_or_create(name='Uploader')
        Group.objects.get_or_create(name='Editor')
        Group.objects.get_or_create(name='ViewPage')
