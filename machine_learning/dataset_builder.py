# Plan:
# For each game in the games-transfermarkt csv, get the url and scrape transfermartk for the lineups as before
# For each player, check if they exist in the players csv for the current season.
# If yes, add attributes
# If no, use google search library to search the player name + sofifa + season
# Scrape the first url for the attributes as before and add them to the dataset
# Add new game to the final_dataset.