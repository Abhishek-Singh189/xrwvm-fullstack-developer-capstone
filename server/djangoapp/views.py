from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json

from .restapis import get_request, post_review, analyze_review_sentiments


def read_data(request):
    try:
        return json.loads(request.body or b"{}")
    except (ValueError, TypeError):
        return {}


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = read_data(request)
    username = data.get("userName") or data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        return JsonResponse({
            "userName": user.username,
            "status": "Authenticated",
            "firstName": user.first_name,
            "lastName": user.last_name
        })

    return JsonResponse({"status": "Invalid credentials"}, status=401)


@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"})


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = read_data(request)

    username = data.get("userName") or data.get("username")
    password = data.get("password")
    email = data.get("email")
    first_name = data.get("firstName") or data.get("first_name", "")
    last_name = data.get("lastName") or data.get("last_name", "")

    if not all([username, password, email]):
        return JsonResponse({"error": "Required fields missing"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )

    return JsonResponse({"status": "Registered", "userName": user.username})


def get_dealerships(request, state=None):
    endpoint = "/fetchDealers"
    if state:
        endpoint += "/" + state

    dealers = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealers": dealers if isinstance(dealers, list) else []
    })


def get_dealer_details(request, dealer_id):
    dealer = get_request("/fetchDealer/" + str(dealer_id))

    if not dealer or not isinstance(dealer, dict):
        return JsonResponse({"status": 404, "dealer": []}, status=404)

    return JsonResponse({"status": 200, "dealer": [dealer]})


def get_dealer_reviews(request, dealer_id):
    reviews = get_request("/fetchReviews/dealer/" + str(dealer_id))

    if not isinstance(reviews, list):
        reviews = []

    for review in reviews:
        review["sentiment"] = analyze_review_sentiments(
            review.get("review", "")
        )

    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)

    data = read_data(request)
    result = post_review(data)

    if result:
        return JsonResponse({"status": 200, "review": result})

    return JsonResponse({"status": 500, "error": "Review could not be saved"}, status=500)


def get_cars(request):
    cars = get_request("/fetchCars")
    if not isinstance(cars, dict):
        cars = {"CarModels": []}

    return JsonResponse(cars)


def analyze_text(request, text):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)
    return JsonResponse({
        "text": text,
        "sentiment": analyze_review_sentiments(text),
    })


def home(request):
    return render(request, "Home.html")
