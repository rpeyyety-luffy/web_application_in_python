# web_application_in_python

A small Flask app for learning APIs:

- **Making an API**: `/api/books` (GET, POST, DELETE), stored in memory
- **Calling an API**: `/api/weather?city=London` calls the free [Open-Meteo](https://open-meteo.com) API (no key needed)

## Run it

```bash
python3 -m venv .venv          # create a virtual environment (once)
source .venv/bin/activate      # activate it (every new terminal)
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Try the API from the terminal

```bash
curl http://127.0.0.1:5000/api/books
curl http://127.0.0.1:5000/api/books/1
curl -X POST http://127.0.0.1:5000/api/books \
     -H "Content-Type: application/json" \
     -d '{"title": "Dune", "author": "Frank Herbert"}'
curl -X DELETE http://127.0.0.1:5000/api/books/1
curl "http://127.0.0.1:5000/api/weather?city=Mumbai"
```
