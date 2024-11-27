"""
    Data preprocessing script. Formats the raw JSON into compact CSV format.
"""

import json
import ast

REVIEW_FILE = "australian_user_reviews.json"
ITEM_FILE = "australian_users_items.json"

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

with open("user_nodes.csv", "w") as user_file:
    user_file.write("id:ID,:LABEL\n")
    for user in users:
        user_file.write(f"{user},UserID\n")

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
    output_file.write(f":START_ID,:END_ID,:TYPE,recommends\n")
    for line in input_file:
        review = json.loads(json.dumps(ast.literal_eval(line)))
        #if f"u{review["user_id"]}" in users:
        user = f"u{review["user_id"]}"
        for i in review["reviews"]:
                #if f"i{i["item_id"]}" in items:
                item = f"i{i["item_id"]}"
                recommend = i["recommend"]
                output_file.write(f"{user},{item},RECOMMENDS,{recommend}\n")

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
        if f"u{catalog["user_id"]}" in users:
            user = f"u{catalog["user_id"]}"
            for i in catalog["items"]:
                if f"i{i["item_id"]}" in items:
                    item = f"i{i["item_id"]}"
                    playtime = i["playtime_forever"]
                    output_file.write(f"{user},{item},PLAYED,{playtime}\n")
