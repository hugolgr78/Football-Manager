APP_SIZE = (1200, 700)
DARK_GREY = "#3b3b3b"
TKINTER_BACKGROUND = "#2b2b2b"
GREY = "#73696c"
GREY_BACKGROUND = "#333333"

APP_BLUE = "#443de1"

APP_FONT = "Arial"
APP_FONT_BOLD = "Arial Bold"

Europe = [
    "Albania", "Andorra", "Austria", "Belgium", 
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czech Republic", "Denmark", 
    "Estonia", "Finland", "France", "Germany", "Greece", 
    "Hungary", "Iceland", "Ireland", "Italy", "Latvia", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Montenegro", 
    "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", 
    "Romania", "Serbia", "Slovakia", "Slovenia", "Spain", 
    "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom"
]

Africa = [
    "Algeria", "Cameroon", "Egypt", "Ethiopia", "Ghana", 
    "Ivory Coast", "Kenya", "Morocco", "Nigeria", "South Africa"
]

Americas = [
    "Argentina", "Brazil", "Bolivia", "Canada", "Chile", 
    "Colombia", "Ecuador", "Mexico", "Peru", "United States", 
    "Uruguay", "Venezuela"
]

Asia = [
    "China", "India", "Indonesia", "Iran", "Japan", 
    "Malaysia", "Saudi Arabia", "South Korea", "Thailand", "Vietnam",
    "Philippines"
]

continents = [Europe, Africa, Americas, Asia]
continentWeights = {"Europe": 0.7, "Africa": 0.05, "North/South America": 0.2, "Asia": 0.05}

mainCountries = ["France", "Germany", "Italy", "Netherlands", "Spain", "United Kingdom"]
westernEurope = ["Austria", "Belgium", "Denmark", "Finland", "Ireland", "Norway", "Portugal", "Sweden", "Switzerland"]
smallCountries = ["Andorra", "Luxembourg", "Malta", "Iceland"]
europeWeights = {
    country: 0.6 if country in mainCountries else (0.2 if country in westernEurope else (0.1 if country in smallCountries else 0.1))
    for country in Europe
}
africaWeights = {country: 0.1 for country in Africa}
americasWeights = {country: 0.083 for country in Americas}
asiaWeights = {country: 0.091 for country in Asia}

# Combining everything
COUNTRIES = {
    "Europe": (continentWeights["Europe"], europeWeights),
    "Africa": (continentWeights["Africa"], africaWeights),
    "North/South America": (continentWeights["North/South America"], americasWeights),
    "Asia": (continentWeights["Asia"], asiaWeights)
}


