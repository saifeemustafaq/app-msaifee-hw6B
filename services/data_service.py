import json

def load_data():
    with open('sample_data.json', 'r') as file:
        return json.load(file) 