from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
    #Django marka uu app-ka bilaabayo ayuu ready() shaqaysiiyaa.
        import users.signals
        #"Django, marka users app-ka load-gareyso, signals-kana soo geli."