from django.apps import AppConfig

# Define the onlinecourse app configuration
class OnlinecourseConfig(AppConfig):
    """
    OnlinecourseConfig is a configuration class for the 'onlinecourse' application.
    This class inherits from Django's AppConfig and is used to configure the 
    'onlinecourse' application.
    Attributes:
        name (str): The name of the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onlinecourse'

    def ready(self):
        import onlinecourse.signals