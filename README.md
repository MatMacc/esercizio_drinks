# Drinks API — Flask + SQLAlchemy + External API caching

Simple REST API that fetches cocktail details from **TheCocktailDB** and caches results into a database.

## Features
- `GET /drink/<name>`: returns a drink from DB if present, otherwise fetches from external API and stores it
- `GET /drinks/<n>`: returns first `n` drinks stored
- `GET /drink/random`: returns a random stored drink
- `POST /drink`: manually insert a drink into the DB

## Quickstart (local)
```bash
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./drinks.db"
python -m app.main
```
Open: http://localhost:8000

## Quickstart (Docker)
```bash
docker build -t drinks-api .
docker run --rm -p 8000:8000 drinks-api
```

## Example requests
```bash
curl http://localhost:8000/drink/margarita
curl http://localhost:8000/drink/random
curl http://localhost:8000/drinks/5

curl -X POST http://localhost:8000/drink \
  -H "Content-Type: application/json" \
  -d '{"name":"MyDrink","category":"Test","instructions":"Shake and serve."}'
```
