import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("backend_url", "http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050/"
)


def _read_json(name):
    path = Path(__file__).resolve().parent.parent / "database" / "data" / name
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _get_local_fallback(endpoint):
    if endpoint == "/fetchDealers":
        return _read_json("dealerships.json").get("dealerships", [])
    if endpoint.startswith("/fetchDealers/"):
        state = endpoint.rsplit("/", 1)[-1]
        dealerships = _read_json("dealerships.json").get("dealerships", [])
        if state.lower() == "all":
            return dealerships
        return [
            dealer for dealer in dealerships
            if dealer.get("state", "").lower() == state.lower()
        ]
    if endpoint.startswith("/fetchDealer/"):
        dealer_id = int(endpoint.rsplit("/", 1)[-1])
        dealers = _read_json("dealerships.json").get("dealerships", [])
        return next((dealer for dealer in dealers if dealer.get("id") == dealer_id), None)
    if endpoint.startswith("/fetchReviews/dealer/"):
        dealer_id = int(endpoint.rsplit("/", 1)[-1])
        reviews = _read_json("reviews.json").get("reviews", [])
        return [review for review in reviews if review.get("dealership") == dealer_id]
    if endpoint == "/fetchCars":
        cars = _read_json("car_records.json").get("cars", [])
        unique = {}
        for car in cars:
            key = f"{car['make']}-{car['model']}"
            unique[key] = {
                "CarMake": car["make"],
                "CarModel": car["model"],
            }
        return {"CarModels": list(unique.values())}
    return None


def get_request(endpoint, **kwargs):
    local_data = _get_local_fallback(endpoint)
    if local_data is not None:
        return local_data

    try:
        response = requests.get(
            backend_url + endpoint,
            params=kwargs,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Backend GET error:", error)
        return []

def analyze_review_sentiments(text):
    words = str(text).lower()
    positive_words = ("excellent", "fantastic", "great", "good", "love", "helpful", "amazing")
    negative_words = ("terrible", "bad", "worst", "awful", "hate", "poor", "disappointing")
    positive = any(word in words for word in positive_words)
    negative = any(word in words for word in negative_words)
    if positive and not negative:
        return "positive"
    if negative and not positive:
        return "negative"
    if positive and negative:
        return "neutral"

    try:
        response = requests.get(
            sentiment_analyzer_url.rstrip("/") +
            "/analyze/" + requests.utils.quote(text, safe=""),
            timeout=5
        )
        response.raise_for_status()
        return response.json().get("sentiment", "neutral")
    except requests.RequestException:
        return "neutral"

def post_review(data_dict):
    try:
        response = requests.post(
            backend_url + "/insert_review",
            json=data_dict,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Backend POST error:", error)
        path = Path(__file__).resolve().parent.parent / "database" / "data" / "reviews.json"
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        reviews = payload.get("reviews", [])
        ids = [review.get("id", 0) for review in reviews]
        review = {
            "id": max(ids, default=0) + 1,
            "name": data_dict.get("name", ""),
            "dealership": int(data_dict.get("dealership", 0)),
            "review": data_dict.get("review", ""),
            "purchase": data_dict.get("purchase", True),
            "purchase_date": data_dict.get("purchase_date", ""),
            "car_make": data_dict.get("car_make", ""),
            "car_model": data_dict.get("car_model", ""),
            "car_year": int(data_dict.get("car_year", 0)),
        }
        reviews.append(review)
        payload["reviews"] = reviews
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)
        return review
