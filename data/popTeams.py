import os
import random
import json

images_folder = 'Images/Teams'

# List of random stadium names
stadium_names = [
    "The Forge",
    "Striker's Arena",
    "Horizon Park",
    "SThe Hive",
    "Frostguard Citadel",
    "Coliseum",
    "The Den Stadium",
    "Bay Arena",
    "Dragon's Lair",
    "Bladefire Stadium",
    "Bearclaw Grounds",
    "Vortex Arena",
    "Shadow Dome",
    "Edge Stadium",
    "The Nest",
    "Solaris Stadium",
    "Maverick's Forge",
    "Stormbreak Field",
    "Thunder Grounds",
    "The Eye Arena"
]

# Create a list of levels from 200 to 162 with a step of 2
levels = list(range(200, 160, -2))

# List to store team data
teams_data = []

# Iterate over the files in the images folder
for i, filename in enumerate(os.listdir(images_folder)):
    if filename.endswith('.png'):
        team_name = os.path.splitext(filename)[0]
        image_path = os.path.join(images_folder, filename)
        year_created = random.randint(1900, 1950)
        stadium = stadium_names[i]

        # Randomly select a level from the list and remove it
        level = random.choice(levels)
        levels.remove(level)

        team_data = {
            "name": team_name,
            "level": level,
            "image_path": image_path,
            "year_created": year_created,
            "stadium": stadium
        }

        teams_data.append(team_data)

# Define the path to the output JSON file
output_file = 'data/teams.json'

# Write the teams data to the JSON file
with open(output_file, 'w') as f:
    json.dump(teams_data, f, indent=4)