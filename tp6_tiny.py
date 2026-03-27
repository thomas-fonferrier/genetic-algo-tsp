import requests

data = requests.get("https://tsp-sra0.onrender.com/instances/regions")
data.raise_for_status()
cities = data.json()["cities"]
print(cities)


