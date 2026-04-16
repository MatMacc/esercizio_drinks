import requests
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

Base.metadata.create_all(engine) #crea la cartella

class CocktailAPI:
    def __init__(self):
        self.url = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

    def get_drink(self,name):
        response = requests.get(self.url, params={"s": name})
        if response. status_code == 200:
            data = response.json()
            if data["drinks"]:
                drink = data["drinks"][0]

                return {
                    "name": drink["strDrink"],
                    "category": drink["strCategory"],
                    "instructions": drink["strInstructions"]
                }
        return None


class DrinkDB:
    def __init__(self):
        self.session = SessionLocal()

    def get_drinks(self, name): #cerca il drink nel db
        return self.session.query(Drink).filter(
            func.lower(Drink.name) == name.lower()
        ).first()


    def add_drink(self, drink_data): #questo salva il drink nel db
        drink = Drink(
            name = drink_data["name"],
            category = drink_data["category"],
            instructions = drink_data["instructions"]
        )

        self.session.add(drink)

        try:
            self.session.commit()
        except:
            self.session.rollback() #se c'è un erroe butta tutto nell'immondizia

    def close(self):
        self.session.close()


if __name__ == "__main__":

    api = CocktailAPI()
    db = DrinkDB()

    drink_name = input("Inserisci il  nome del drink: ")

    drink = db.get_drinks(drink_name)

    if drink:
        print("Preso dal database!")
        print(drink_name)
        print(drink.category)
        print(drink.instructions)

    else:

        print("Non l'ho trovato nel database, chiamo API...")

        drink_data = api.get_drink(drink_name)
        if drink_data:
            db.add_drink(drink_data)

            print("L'ho preso dall' API sto cocktail...")
            print(drink_data["name"])
            print(drink_data["category"])
            print(drink_data["instructions"])
        else:
            print("Drink non trovato! =(")

    db.close()