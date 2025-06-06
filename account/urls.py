from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path(route="getting-started/", view=views.getting_started, name="getting_started"),
    path(route="getting-started/login/", view=views.login_request, name="login"),
    path(route="getting-started/registration/", view=views.registration_request, name="registration"),
    path(route="logout/", view=views.logout_request, name="logout"),
    path(route="registration/complete-user-profile/", view=views.complete_profile, name="complete_profile"),
    path(route="registration/complete-user-profile/submit", view=views.submit_form, name="submit_form"),
    path(route="profile/", view=views.view_profile, name="profile"),
    path(route="profile/update/", view=views.update_profile, name="update_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
