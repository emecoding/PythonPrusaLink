import json

def read_file_into_json(file_path):
    data = ""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

CONFIG = read_file_into_json("config.json")
