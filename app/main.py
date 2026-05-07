import random
from flask import Flask, jsonify, request
from sqlalchemy import func

from app.db import SessionLocal, Drink, init_db
from app.services import CocktailAPI

def create_app():
    app = Flask(__name__)
    init_db()
    api = CocktailAPI()

    @app.get("/")
    def health():
        return {"status": "ok", "message": "Drinks API is running"}

    @app.get("/drink/<name>")
    def get_drink(name):
        session = SessionLocal()

        drink = session.query(Drink).filter(
            func.lower(Drink.name).like(f"%{name.lower()}%")
        ).first()

        if drink:
            session.close()
            return jsonify({
                "source": "database",
                "name": drink.name,
                "category": drink.category,
                "instructions": drink.instructions
            })

        drink_data = api.get_drink(name)

        if drink_data:
            new_drink = Drink(**drink_data)
            session.add(new_drink)
            try:
                session.commit()
            except:
                session.rollback()
            session.close()

            return jsonify({"source": "api", **drink_data})

        session.close()
        return jsonify({"error": "Drink not found"}), 404

    @app.get("/drinks/<int:n>")
    def get_n_drinks(n):
        session = SessionLocal()
        drinks = session.query(Drink).limit(n).all()
        session.close()

        return jsonify([{
            "name": d.name,
            "category": d.category,
            "instructions": d.instructions
        } for d in drinks])

    @app.get("/drink/random")
    def get_random_drink():
        session = SessionLocal()
        count = session.query(Drink).count()

        if count == 0:
            session.close()
            return jsonify({"error": "Database is empty"}), 404

        random_index = random.randint(0, count - 1)
        drink = session.query(Drink).offset(random_index).first()
        session.close()

        return jsonify({
            "name": drink.name,
            "category": drink.category,
            "instructions": drink.instructions
        })

    @app.post("/drink")
    def add_drink():
        session = SessionLocal()
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        name = data.get("name")
        category = data.get("category")
        instructions = data.get("instructions")

        if not name:
            return jsonify({"error": "Missing 'name'"}), 400

        existing = session.query(Drink).filter(
            func.lower(Drink.name) == name.lower()
        ).first()

        if existing:
            session.close()
            return jsonify({"error": "Drink already exists"}), 400

        new_drink = Drink(name=name, category=category, instructions=instructions)
        session.add(new_drink)

        try:
            session.commit()
        except:
            session.rollback()
            session.close()
            return jsonify({"error": "Database error while inserting"}), 500

        session.close()
        return jsonify({"message": "Drink added", "name": name}), 201

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)