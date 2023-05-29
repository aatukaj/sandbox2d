import json

# read file
with open('tile_data.json', 'r') as f:
    data=f.read()

# parse file
obj = json.loads(data)

# show values
print(obj)