import json

PROFILE_PATH = "profile.json"

with open(PROFILE_PATH, "r") as file:
    USER_PROFILE = json.load(file)