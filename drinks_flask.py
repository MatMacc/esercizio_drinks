import random

import requests
from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker



database_url = "mysql+mysqlconnector://user:userpass@127.0.0.1:3306/mydb"
engine = create_engine(database_url, echo=False) #connessione al db
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base() #classe delle tabelle



class Drink(Base):
    __tablename__ = "drinks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    category = Column(String(255))
    instructions = Column(Text)

Base.metadata.create_all(engine) #crea la tabella del db

class CocktailAPI:
    def __init__(self):
        self.url = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

    def get_drink(self,name):
        response = requests.get(self.url, params={"s": name})
        if response.status_code == 200:
            data = response.json()
            if data["drinks"]:
                drink = data["drinks"][0]

                return {
                    "name": drink["strDrink"],
                    "category": drink["strCategory"],
                    "instructions": drink["strInstructions"]
                }
        return None

#------
#FLASK
#------

app = Flask(__name__)


#endpoint1
@app.route("/drink/<name>", methods=["GET"])
def get_drink(name):
    session = SessionLocal()
    api = CocktailAPI()

    drink = session.query(Drink).filter(
        Drink.name.ilike(f"%{name}%")
    ).first()

    if drink:
        session.close()
        return jsonify({
            "source": "database",
            "name": drink.name,
            "category": drink.category,
            "instructions": drink.instructions
        })

    drink_data = api.get_drink(name) #chiama api se non lo trova nel db

    #crea oggetto orm e inserisce nel db se non ci sono errori
    if drink_data:
        new_drink = Drink(
            name = drink_data["name"],
            category = drink_data["category"],
            instructions = drink_data["instructions"]
        )

        session.add(new_drink)

        try:
            session.commit()
        except:
            session.rollback()

        session.close()

        return jsonify({
            "source": "api",
            **drink_data
        })

    session.close()
    return jsonify({"errore": "Drink non trovato!"}), 404


#endpoint2
@app.route("/drinks/<int:n>", methods=["GET"])
def get_n_drinks(n):
    session = SessionLocal()

    drinks = session.query(Drink).limit(n).all()
    session.close()

    result = []
    for d in drinks:
        result.append({
            "name": d.name,
            "category": d.category,
            "instructions": d.instructions
        })
    return jsonify(result)


#endpoint3
@app.route("/drink/random", methods=["GET"])
def get_random_drink():
    session = SessionLocal()
    count = session.query(Drink).count()

    if count == 0:
        session.close()
        return jsonify({"errore" : "Database vuoto"}), 404

    random_index = random.randint(0,count-1)

    drink = session.query(Drink).offset(random_index).first()

    session.close()

    return jsonify({
        "name": drink.name,
        "category": drink.category,
        "instructions": drink.instructions
    })


if __name__ == "__main__":
    app.run(debug=True)



