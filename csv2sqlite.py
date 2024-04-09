import json
from app.dash_plotlys.global_stats import initiate_db, country_codes

#with open("country_codes.json", "r") as json_file:
#    country_codes = json.load(json_file)

country_names = list(country_codes.values())

initiate_db(country_names)
print(f"You wrote something down to be printed at the last line of csv2sqlite")