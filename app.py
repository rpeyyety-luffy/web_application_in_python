"""
A simple web application to learn APIs.

It shows two things:
  1. MAKING an API   -> the /api/books endpoints (we are the server)
  2. CALLING an API  -> the /api/weather endpoint calls Open-Meteo (we are the client)

Run it with:  python app.py   then open http://127.0.0.1:5000
"""

import requests                      # library for CALLING other APIs over HTTP
from flask import Flask, jsonify, request, render_template

# Create the Flask application. Think of `app` as our web server.
app = Flask(__name__)


# ---------------------------------------------------------------------------
# Our "database": just a Python list in memory.
# (Data is lost when the server restarts - a real app would use a database.)
# ---------------------------------------------------------------------------
books = [
    {"id": 1, "title": "Harry Potter", "author": "J.K. Rowling"},
    {"id": 2, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
]
next_id = 3  # the id we will give to the next new book


# ---------------------------------------------------------------------------
# The web page
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    # Sends templates/index.html to the browser.
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Practice routes: 3 URLs, 3 functions, 3 different messages
# ---------------------------------------------------------------------------
@app.route("/hello")                 # visit http://127.0.0.1:5000/hello
def hello():
    return "Hello! Welcome to my first Flask app."


@app.route("/about")                 # visit http://127.0.0.1:5000/about
def about():
    return "I am a student learning how to make and call APIs with Python."


@app.route("/bye")                   # visit http://127.0.0.1:5000/bye
def bye():
    return "Goodbye! Thanks for visiting."


# ===========================================================================
# PART A: MAKING OUR OWN API  (Book API)
# ===========================================================================
# @app.route(...) connects a URL + HTTP method to a Python function.
# When a request arrives at that URL, Flask runs the function and sends
# back whatever it returns as the response.

@app.route("/api/books", methods=["GET"])
def get_books():
    """GET /api/books  -> return ALL books."""
    # jsonify() turns a Python list/dict into a JSON response.
    # Status code 200 (OK) is the default.
    return jsonify(books)


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """GET /api/books/1  -> return ONE book. <int:book_id> is read from the URL."""
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)
    # Not found -> return an error message AND status code 404.
    return jsonify({"error": f"Book {book_id} not found"}), 404


@app.route("/api/books", methods=["POST"])
def add_book():
    """POST /api/books  with JSON body {"title": "...", "author": "..."}  -> create a book."""
    global next_id

    # request.get_json() reads the JSON the client sent in the request BODY.
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    # Always validate input! If something is missing -> 400 Bad Request.
    if not title or not author:
        return jsonify({"error": "Both 'title' and 'author' are required"}), 400

    new_book = {"id": next_id, "title": title, "author": author}
    books.append(new_book)
    next_id += 1

    # 201 Created = "I made a new thing for you".
    return jsonify(new_book), 201


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """DELETE /api/books/1  -> remove a book."""
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return jsonify({"message": f"Book {book_id} deleted"})
    return jsonify({"error": f"Book {book_id} not found"}), 404


# ===========================================================================
# PART B: CALLING SOMEONE ELSE'S API  (Open-Meteo weather, no API key needed)
# ===========================================================================
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@app.route("/api/weather", methods=["GET"])
def get_weather():
    """GET /api/weather?city=London  -> current weather for a city."""

    # 1) Read the query parameter (?city=...) from OUR request.
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please give a city, e.g. /api/weather?city=London"}), 400

    try:
        # 2) CALL #1: Geocoding API - turn the city name into latitude/longitude.
        #    `params` becomes the query string: ?name=London&count=1
        #    `timeout` stops us waiting forever if the other server is slow.
        geo_response = requests.get(
            GEOCODING_URL, params={"name": city, "count": 1}, timeout=10
        )
        geo_response.raise_for_status()   # raises an error if status is 4xx/5xx
        geo_data = geo_response.json()    # convert the JSON text into a Python dict

        # The API returns {"results": [...]} - or no "results" key if nothing matched.
        if not geo_data.get("results"):
            return jsonify({"error": f"City '{city}' not found"}), 404

        place = geo_data["results"][0]
        lat, lon = place["latitude"], place["longitude"]

        # 3) CALL #2: Forecast API - get the current weather at those coordinates.
        weather_response = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current = weather_data["current"]

    except requests.RequestException as error:
        # Network problem or the other API returned an error.
        # 502 Bad Gateway = "the server I depend on failed".
        return jsonify({"error": f"Could not reach weather service: {error}"}), 502

    # 4) Build our OWN simpler JSON from the big responses we got back.
    return jsonify({
        "city": place["name"],
        "country": place.get("country", ""),
        "temperature_c": current["temperature_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
    })


if __name__ == "__main__":
    # debug=True restarts the server automatically when you edit code
    # and shows helpful error pages. Never use debug=True in production.
    app.run(debug=True)
