"""
    Data preprocessing script. Formats the raw JSON into compact CSV format.
"""

import json
import ast

REVIEW_FILE = "australian_user_reviews.json"
ITEM_FILE = "australian_users_items.json"
META_FILE = "steam_games.json"

# Create a set of unique user ID's who left reviews, and unique game ID's which were reviewed
print("Retrieve nodes.")
users = set()
items = set()
with open(REVIEW_FILE, "r", encoding="utf8") as input_file:
    for line in input_file:
        review = json.loads(json.dumps(ast.literal_eval(line)))
        users.add("u" + review["user_id"])
        for i in review["reviews"]:
            items.add("i" + i["item_id"])

with (
        open(ITEM_FILE, "r", encoding="utf8") as input_file,
        open("user_nodes.csv", "w") as user_file
    ):
    user_file.write("id:ID,:LABEL,games_owned:int\n")
    for line in input_file:
        user = json.loads(json.dumps(ast.literal_eval(line)))
        if f"u{user['user_id']}" in users:
            user_file.write(f"u{user['user_id']},UserID,{user['items_count']}\n")

with open("item_nodes.csv", "w") as item_file:
    item_file.write("id:ID,:LABEL\n")
    for item in items:
        item_file.write(f"{item},GameID\n")

# For each review, connect the user to the game with TRUE/FALSE recommendation relationships
print("Retrieve review relations between nodes.")
with (
        open(REVIEW_FILE, "r", encoding="utf8") as input_file,
        open("review_relations.csv", "w") as output_file
    ):
    #output_file.write(f":START_ID,:END_ID,:TYPE,recommends:bool\n") ***neo4j ne comprend pas nativement le type "bool"
    output_file.write(f":START_ID,:END_ID,:TYPE,recommends,date_posted,helpfulness\n")
    for line in input_file:
        review = json.loads(json.dumps(ast.literal_eval(line)))
        user = f"u{review['user_id']}"
        for i in review["reviews"]:
                item = f"i{i['item_id']}"
                recommend = i["recommend"]
                date = i["posted"]
                date = str(date)[0:-1].replace(",", "")
                helpful = i["helpful"]
                helpful = str(helpful).replace(",", "")
                output_file.write(f"{user},{item},RECOMMENDS,{recommend},{date},{helpful}\n")

# Connect each user to the games they played with total_playtime relationships
# Only if user AND game are found in the reviews file
print("Retrieve item relations between nodes.")
with (
        open(ITEM_FILE, "r", encoding="utf8") as input_file,
        open("item_relations.csv", "w") as output_file
    ):
    output_file.write(f":START_ID,:END_ID,:TYPE,playtime:int\n")
    for line in input_file:
        catalog = json.loads(json.dumps(ast.literal_eval(line)))
        if f"u{catalog['user_id']}" in users:
            user = f"u{catalog['user_id']}"
            for i in catalog["items"]:
                if f"i{i['item_id']}" in items:
                    item = f"i{i['item_id']}"
                    playtime = i["playtime_forever"]
                    output_file.write(f"{user},{item},PLAYED,{playtime}\n")

print("Retrieve item metadata.")
with (
        open(META_FILE, "r", encoding="utf8") as input_file,
        open("item_metadata.csv", "w", encoding="utf8") as output_file
    ):
    output_file.write(f"GameID|title|release|sentiment|metascore|price\n")
    for line in input_file:
        i = json.loads(json.dumps(ast.literal_eval(line)))
        if "id" not in i:
            continue
        if f"i{i['id']}" in items:
            item = f"i{i['id']}"
            title = i.get("title", "")
            title = str(title).replace("&amp;", "&")
            date = i.get("release_date", "")
            if len(date) == 8:
                date = f'{date[-4:]}-{date[0:3]}'
            sentiment = i.get("sentiment", "")
            score = i.get("metascore", "")
            score = str(score).replace("NA", "")
            price = i.get("price", "")
            if any(val in str(price) for val in ["Free", "Demo", "Install", "Third-party"]):
                price = 0.00
            output_file.write(f"{item}|{title}|{date}|{sentiment}|{score}|{price}\n")
