import requests

class CocktailAPI:
    def __init__(self):
        self.url = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

    def get_drink(self, name: str):
        response = requests.get(self.url, params={"s": name}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("drinks"):
                drink = data["drinks"][0]
                return {
                    "name": drink["strDrink"],
                    "category": drink["strCategory"],
                    "instructions": drink["strInstructions"]
                }
        return None