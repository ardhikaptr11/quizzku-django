import asyncio
import json
import logging
import os
import re

import aiohttp
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import Learner, User

logger = logging.getLogger(__name__)

load_dotenv()


def validate_email(email):
    email_pattern = r"^[\w\-\.]+@(?:[\w-]+\.)+[\w-]{2,3}$"
    is_email_valid = bool(re.match(email_pattern, email))
    return is_email_valid


def validate_username(username):
    username_pattern = r"^[a-z0-9][a-zA-Z0-9_]{7,11}$"
    is_username_valid = bool(re.match(username_pattern, username))
    return is_username_valid


def validate_password(password):
    password_pattern = r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[\]:;<>,.?\\/~_+\-=|]).{8,32}$"
    is_password_valid = bool(re.match(password_pattern, password))
    return is_password_valid


def validate_user_data(email, username, password):
    is_email_valid = validate_email(email)
    is_username_valid = validate_username(username)
    is_password_valid = validate_password(password)

    all_data_valid = is_email_valid and is_username_valid and is_password_valid
    return all_data_valid


# Create your views here.
def registration_request(request: HttpRequest) -> HttpResponse:
    # Context is a dictionary that is passed to the template
    context = {}

    if request.method == "GET":
        return render(request, "getting_started.html", context)

    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("signUpEmail", "")
        username = data.get("signUpUsername", "")
        password = data.get("signUpPassword", "")
        confirmation_password = data.get("confirmationPassword", "")

        user_exist = False

        message = ["Registration failed"]

        required_fields = [email, username, password, confirmation_password]
        if any(field == "" for field in required_fields):
            message.append("Please fill in all the fields")
            return JsonResponse({"success": False, "message": message})

        if User.objects.filter(username=username).exists():
            user_exist = True
            message.append("Username is already exists")
            return JsonResponse({"success": False, "message": message})

        if User.objects.filter(email=email).exists():
            user_exist = True
            message.append("Email is already exists")
            return JsonResponse({"success": False, "message": message})

        if not user_exist:
            is_email_valid = validate_email(email)
            is_username_valid = validate_username(username)
            is_password_valid = validate_password(password)

            if password != confirmation_password:
                message.append("Password does not match")
                return JsonResponse({"success": False, "message": message})

            if not is_email_valid:
                message.append("Email is not in valid format")
                return JsonResponse({"success": False, "message": message})

            if not is_username_valid:
                message.append("Username is not in valid format")
                return JsonResponse({"success": False, "message": message})

            if not is_password_valid:
                message.append("Password does not meet our security standard")
                return JsonResponse({"success": False, "message": message})

            all_data_valid = validate_user_data(email=email, username=username, password=password)

            if all_data_valid:
                user = User.objects.create_user(email=email, username=username)
                user.set_password(password)
                user.save()

                login(request, user)

                profile_completion_url = reverse("account:complete_profile") + f"?username={user.username}"

                return JsonResponse({"success": True, "redirect_url": profile_completion_url})


def login_request(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    """
    Handle user login requests.
    This view function processes login requests. If the request method is POST, it attempts to
    authenticate the user with the provided username and password. If authentication is successful,
    the user is logged in and redirected to the index page. If authentication fails, an error message
    is added to the context and the login page is re-rendered. For GET requests, the login page is
    rendered without any context.
    Args:
        request (HttpRequest): The HTTP request object containing request data.
    Returns:
        HttpResponse: The HTTP response object with the rendered login page or a redirect to the index page.
    """

    expiry_duration = 15 * 60  # 15 minutes
    expiry_time = now() + timedelta(seconds=expiry_duration)

    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("loginEmail", "")
        password = data.get("loginPassword", "")

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)

            profile_completion_url = reverse("account:complete_profile") + f"?username={user.username}"

            if user.full_name:
                homepage_url = reverse("onlinecourse:index")
                return JsonResponse(
                    {"success": True, "redirect_url": homepage_url, "session_expiry": expiry_time.isoformat()}
                )

            return JsonResponse(
                {"success": True, "redirect_url": profile_completion_url, "session_expiry": expiry_time.isoformat()}
            )
        else:
            return JsonResponse({"success": False, "message": "Invalid login credentials"})

    return JsonResponse({"success": False, "message": "Invalid login credentials"})


def getting_started(request: HttpRequest) -> HttpResponse:
    """
    Handle both user registration and login requests in one view.
    If the request is GET, it renders the registration/login page.
    If the request is POST, it handles either user registration or login based on the form submitted.
    Redirect authenticated users away from the login/signup page.
    """

    # context = {}

    if request.method == "GET":
        return render(request, template_name="getting_started.html")

    if request.method == "POST":
        if "signup" in request.POST:
            registration_request(request)

        elif "login" in request.POST:
            login_request(request)


def complete_profile(request: HttpRequest) -> HttpResponse:
    """
    Handle user profile completion requests.
    This view function processes requests to complete user profiles. If the request method is POST, it updates the user
    profile with the provided data. If the request method is GET, it renders the user profile completion page.
    Args:
        request (HttpRequest): The HTTP request object containing request data.
    Returns:
        HttpResponse: The HTTP response object with the rendered user profile completion page or a redirect to the index page.
    """

    user = request.user
    username = request.GET.get("username")

    if request.method == "GET" and username == user.username:
        fullname = user.full_name

        if fullname:
            return HttpResponse("You have already completed your profile.")

        context = {
            "username": username,
        }

        return render(request, template_name="complete_profile.html", context=context)
    return redirect(to="onlinecourse:index")


def submit_form(request: HttpRequest) -> HttpResponse:
    """
    Handle user profile completion requests.
    This view function processes requests to complete user profiles. If the request method is POST, it updates the user
    profile with the provided data. If the request method is GET, it renders the user profile completion page.
    Args:
        request (HttpRequest): The HTTP request object containing request data.
    Returns:
        HttpResponse: The HTTP response object with the rendered user profile completion page or a redirect to the index page.
    """

    user = request.user

    data = json.loads(request.body)
    fullname = data.get("full_name", "")
    nickname = data.get("nickname", "")
    gender = data.get("gender", "")
    phone_number = data.get("phone_number", "")
    field_of_interest = data.get("field_of_interest", "")
    birth_date = data.get("birth_date", "")

    phone_number = re.sub(r"\D", "", phone_number)
    phone_number = f"0{phone_number}"

    user.full_name = fullname
    user.nickname = nickname
    user.gender = gender
    user.phone_number = phone_number
    user.birth_date = birth_date
    user.save()

    learner, _ = Learner.objects.get_or_create(user=user)
    learner.field_of_interest = field_of_interest
    learner.save()

    request.session["from_registration"] = True
    redirect_url = reverse("onlinecourse:index")

    return JsonResponse({"success": True, "homepage_url": redirect_url})


@csrf_exempt
def logout_request(request: HttpRequest) -> HttpResponseRedirect:
    """
    Handle the user logout request.
    This view function logs out the current user and redirects them to the index page of the online course application.
    Args:
        request (HttpRequest): The HTTP request object that triggered this view.
    Returns:
        HttpResponseRedirect: A redirect response to the index page of the online course application.
    """

    logout(request)
    return redirect(to="onlinecourse:index")


async def get_social_profile_name(social_link: str):
    API_KEY = os.getenv("API_KEY")

    if "https://" in social_link and "www" not in social_link:
        splitted_link = social_link.split("//")
        social_link = f"https://www.{splitted_link[-1]}"
    elif "https://www" not in social_link:
        social_link = f"https://{social_link}"

    async with aiohttp.ClientSession() as session:
        async with session.get(social_link) as response:
            html_content = await response.text()

    soup = BeautifulSoup(html_content, "html.parser")

    if "instagram.com" in social_link:
        content = soup.find("meta", property="og:title")

        # Get content from the meta tag
        splitted_content = content.get("content", None).split(" ")[:2]
        profile_name = " ".join(splitted_content)
        
        if "@" in splitted_content[-1]:
            profile_name = splitted_content[0]
        
        cache_key = f"instagram_profile_name:{social_link}"
        cached_name = cache.get(cache_key)
        
        if cached_name:
            return cached_name
        
        cache.set(cache_key, profile_name, timeout=30 * 24 * 60 * 60)
        
        return profile_name

    if "facebook.com" in social_link:
        content = soup.find("meta", property="og:title")

        # Get content from the meta tag
        splitted_content = content.get("content", None).split(" ")[:3]
        profile_name = " ".join(splitted_content)
        
        cache_key = f"facebook_profile_name:{social_link}"
        cached_name = cache.get(cache_key)
        
        if cached_name:
            return cached_name
        
        cache.set(cache_key, profile_name, timeout=30 * 24 * 60 * 60)

        return profile_name
    
    if "github.com" in social_link:
        name_tag = soup.find("span", class_="p-name vcard-fullname d-block overflow-hidden")
        profile_name = name_tag.get_text(strip=True)
        
        cache_key = f"github_profile_name:{social_link}"
        cached_name = cache.get(cache_key)
        
        if cached_name:
            return cached_name
        
        cache.set(cache_key, profile_name, timeout=30 * 24 * 60 * 60)
        
        return profile_name

    if "linkedin.com" in social_link:
        url = "https://li-data-scraper.p.rapidapi.com/get-profile-data-by-url"
        querystring = {"url": social_link}
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "li-data-scraper.p.rapidapi.com",
        }

        cache_key = f"linkedin_profile_name:{social_link}"
        cached_name = cache.get(cache_key)

        if cached_name:
            return cached_name

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            response_data = response.json()
            profile_name = f"{response_data['firstName']} {response_data['lastName']}"
            cache.set(cache_key, profile_name, timeout=30 * 24 * 60 * 60)  # 30 days
            return profile_name

    if "x.com" in social_link:
        url = "https://twitter-api47.p.rapidapi.com/v2/user/by-username"
        username = social_link.split("/")[-1]

        querystring = {"username": username}

        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "twitter-api47.p.rapidapi.com",
        }

        cache_key = f"twitter_profile_name:{username}"
        cached_name = cache.get(cache_key)

        if cached_name:
            return cached_name

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            response_data = response.json()
            profile_name = response_data["legacy"]["name"]
            cache.set(cache_key, profile_name, timeout=30 * 24 * 60 * 60)
            return profile_name

    return "Unknown User"


def view_profile(request: HttpRequest) -> HttpResponse:
    user = request.user

    if request.method == "GET":
        if user.is_authenticated:
            learner = Learner.objects.get(user=user)

            field_of_interest = learner.field_of_interest
            profession = learner.profession
            social_link = learner.social_link

            completion_percentage = user.completion_percentage()
            social_profile_name = asyncio.run(get_social_profile_name(social_link)) if social_link else None

            learner_data = {
                "field_of_interest": field_of_interest,
                "profession": profession,
                "social_link": social_link,
                "social_profile_name": social_profile_name
            }

            context = {"user": user, "learner_data": learner_data, "completion_percentage": completion_percentage}

            return render(request, "profile-page.html", context)

        return redirect(to="account:logout")


def update_profile(request):
    if request.method == "POST":
        user = request.user

        try:
            # It uses "request.method.get()" instead of "data.get()" because it contains image object that can't be read by json.loads()
            profile_image = request.FILES.get("imageFile")
            nickname = request.POST.get("nickname")
            email = request.POST.get("email")
            address = request.POST.get("address")
            phone_number = request.POST.get("phone")
            profession = request.POST.get("profession")
            institution = request.POST.get("institution")
            social_link = request.POST.get("social")
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return JsonResponse({"success": False, "message": "An error occurred while updating your profile."})

        if profile_image:
            extension = os.path.splitext(profile_image.name)[1]
            new_format = f"quizzku_{user.username}{extension}"
            profile_image.name = new_format
            user.profile_image = profile_image
        else:
            profile_image = request.POST.get("imageFile")
            if profile_image != "":
                user.profile_image = None
            else:
                pass

        if nickname:
            user.nickname = nickname

        if email:
            emails = User.objects.all().values_list("email", flat=True)
            if email in emails:
                return JsonResponse({"success": False, "message": "Email is used by another user."})
            user.email = email

        if address:
            user.address = address

        if phone_number:
            user.phone_number = phone_number

        if profession:
            learner = Learner.objects.get(user=user)
            learner.profession = profession
            learner.save()

        if institution:
            user.institution = institution

        if social_link:
            learner = Learner.objects.get(user=user)
            learner.social_link = social_link
            learner.save()

        user.save()
        return JsonResponse({"success": True, "message": "Profile updated successfully."})
