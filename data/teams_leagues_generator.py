import os
import random
import json
from PIL import Image
import shutil

# Each team will need:
# - Name
# - Starting strength
# - Logo image path
# - year created
# - Stadium name
# - League Name 

# Each league will need:
# - Name
# - logo image path
# - promotion (0 for A div, 3 for each B,C,D)
# - relegation (0 for D div, 3 for each A,B,C)

planets_names = ["Cryon", "Vorlis", "Zephyra", "Tauron", "Nerath", "Ecliptis", "Lyra", "Solara"]
league_names = {
    "Cryonese Primera": ["Cryonese Primera", "Cryonese Segunda", "Cryonese Tercera", "Cryonese Cuarta"],
    "Vorlis Liga": ["Vorlis Liga", "Vorlis National", "Vorlis Continental", "Vorlis Regional"],
    "Zephyra Pro": ["Zephyra Pro", "Zephyra Challenge", "Zephyra Series", "Zephyra B"],
    "Tauron Premier": ["Tauron Premier", "Tauron Elite", "Tauron Division 2", "Tauron Division 3"],
    "Nerathoul": ["Nerathoul", "Nerathoul Prime", "Nerathoul Ascend", "Nerathoul Minor"],
    "Ecliptus": ["Ecliptus", "Ecliptus B", "Ecliptus C", "Ecliptus D"],
    "Lyraxis": ["Lyraxis", "Lyraxis Nova", "Lyraxis Minor", "Lyraxis Rising"],
    "Solarion": ["Solarion", "Solarion 2", "Solarion 3", "Solarion 4"]
}

league_strengths = [
    1.60, 0.60, 1.45, 1.55, 1.35, 1.48, 1.25, 0.75, 0.70, 1.00,
    1.52, 1.58, 1.42, 1.30, 0.85, 1.50, 1.20, 1.62, 1.40, 0.80
]

logo_templates_path = "data/Logo Templates"
team_logos_path = "Images/Teams"
league_logos_path = "Images/Leagues"

# --- CLEAN PREVIOUS FILES & IMAGES ---
if os.path.exists("data/teams.json"):
    os.remove("data/teams.json")
if os.path.exists("data/leagues.json"):
    os.remove("data/leagues.json")

if os.path.exists(team_logos_path):
    shutil.rmtree(team_logos_path)
os.makedirs(team_logos_path, exist_ok=True)

# os.makedirs(league_logos_path, exist_ok=True)

teams = {
    "Emberfall Vipers": "Gate Cradle Realm",
    "Crimson Scorpions": "The Astral Core",
    "Ethereal Tigers": "The Run Bastion",
    "Runic Griffins": "The Stellar",
    "Celestial Guardians": "Cradle Sanctum",
    "Shadowborn Pioneers": "The Emerald Forge",
    "Shadow Phoenixes": "Nightflame Stadium",
    "Luminous Chargers": "The Arcane Halo",
    "Titanic Stingers": "Citadel Continuum",
    "Abyssal Centaurs": "The Lair Zenith",
    "Stormborn Eagles": "The Blazing Vault",
    "Golden Stallions": "The Aegis Drift Sanctum",
    "Nebular Sabers": "The Zephyr Sanctum",
    "Cobalt Stingers": "The Oblivion Eyrie",
    "Rune Blades": "The Obsidian Vortex",
    "Frostborn Falcons": "Astral Arena",
    "Radiant Vipers": "The Ember Continuum",
    "Phantom Blades": "The Pyre Spire",
    "Marble Bears": "The Eternal Sanctum",
    "Auric Djinn": "Goldveil Stadium",
    "Thorn Bears": "The Emerald Core",
    "Stormborn Titans": "Stellar Drift",
    "Oceanic Falcons": "Nova Eyrie",
    "Echo Tigers": "Cradle",
    "Glacial Dragons": "The Astral Continuum",
    "Inferno Wolves": "Stellar Forge",
    "Ecliptic Centaurs": "Lunar Celestial",
    "Nocturne Tigers": "Velvet Conflux",
    "Cobalt Dragons": "The Thunder Aether",
    "Eternal Hurricanes": "Nova Empyrean",
    "Velvet Raiders": "Oblivion Nexus",
    "Savage Leopards": "Halo",
    "Solar Chargers": "Stormborn Nucleus",
    "Zephyr Bulls": "Umbral Vault",
    "Runic Tigers": "The Solaris Gate",
    "Emerald Falcons": "Velvet Zenith",
    "Violet Vortex": "The Gate Arcane Zephyr",
    "Celestial Leviathans": "Starfall Colosseum",
    "Obsidian Chimera": "Blackfire Grounds",
    "Iron Lynx": "Titan Gate",
    "Steel Pioneers": "The Tempest Gate",
    "Hollow Titans": "The Sanctum Halo Sanctuary",
    "Golden Mavericks": "Eternal Forge",
    "Nocturne Dragons": "The Oblivion Gate",
    "Granite Dragons": "The Arcane Bastion",
    "Thunder Eagles": "The Stellar Obelisk",
    "Nebular Scorpions": "The Celestial Pinnacle",
    "Runic Bulls": "Emerald Forge",
    "Frost Mavericks": "The Nocturne Vault",
    "Violet Raiders": "The Tempest Aether",
    "Solaris Knights": "Horizon Spire",
    "Verdant Phoenixes": "Emerald Flame Stadium",
    "Auric Falcons": "Infernal Spire",
    "Stormborn Rhinos": "The Stone Forge",
    "Feral Raiders": "Titan Citadel Crystal",
    "Solaris Wolves": "The Frosted Spire",
    "Titanic Raptors": "Mystic Titan Arcane",
    "Emberfall Leopards": "Velvet Mystic",
    "Celestial Stingers": "Thunder Spire",
    "Rune Vortex": "The Ember Sanctum",
    "Radiant Lynx": "Celestial Eclipse",
    "Grove Knights": "The Stormborn Citadel",
    "Iron Chargers": "The Nova Continuum",
    "Iron Cobras": "The Arcane Drift",
    "Eternal Strikers": "Eternal Spire",
    "Obsidian Phoenixes": "Sanctuary Nova",
    "Inferno Cobras": "The Infernal Nucleus",
    "Ethereal Griffins": "Void Spire",
    "Twilight Djinn": "Gloamspire Coliseum",
    "Tempest Gargoyles": "Stormspire Arena",
    "Crimson Leopards": "Astral Temple",
    "Hollow Stingers": "The Sky Aegis",
    "Auric Stallions": "Nova Obelisk",
    "Oblivion Ravens": "Shadowspire Arena",
    "Silver Pioneers": "The Blazing Haven",
    "Zephyr Dragons": "Astral Vault",
    "Silver Dragons": "The Celestial Nucleus",
    "Crimson Krakens": "Red Tide Coliseum",
    "Frostborn Scorpions": "The Titan Gate",
    "Aether Rhinos": "The Continuum Oblivion",
    "Arcane Guardians": "The Nova Sphere",
    "Prismatic Vipers": "Umbral Gate",
    "Blazing Wolves": "Citadel Eclipse",
    "Marble Centaurs": "Umbral Granite",
    "Titanic Oozes": "Colossus Slime Grounds",
    "Nocturne Mavericks": "Bastion Sanctuary",
    "Ethereal Leopards": "Halo Runic",
    "Shadowborn Wolves": "Stone Spire",
    "Mystic Knights": "Zephyr Vault",
    "Solar Gorgons": "Sunfang Stadium",
    "Oceanic Pioneers": "Continuum Aegis",
    "Radiant Hawks": "Halo Spire",
    "Oceanic Hawks": "Core",
    "Crimson Mavericks": "Ember Nexus",
    "Glacial Blades": "Arcane Stellar",
    "Stormborn Vipers": "Spire Eternal",
    "Mystic Blades": "The Stellar Sanctum",
    "Glacial Eagles": "Nova Gate",
    "Solaris Stallions": "The Zephyr Starforge",
    "Solaris Griffins": "Hollow Aether Tempest",
    "Aether Eagles": "Arcane Eyrie",
    "Glacial Banshees": "Frostwail Stadium",
    "Crimson Eagles": "Blazing Crucible",
    "Golden Dragons": "The Eyrie Core",
    "Draconic Wolves": "The Nova Spire",
    "Stone Cougars": "Nocturne Sanctum",
    "Crimson Warthogs": "The Zephyr Citadel",
    "Auric Guardians": "The Ashen Vault",
    "Zephyr Lynx": "Dominion Continuum",
    "Luminous Spectres": "Glowveil Stadium",
    "Frostborn Dragons": "Velvet",
    "Voltaic Strikers": "The Oblivion Mystic",
    "Emberfall Phoenixes": "Empyrean Ember",
    "Voltaic Bears": "The Monolith Realm Prism",
    "Nocturne Pioneers": "The Astral Monolith",
    "Nocturne Bulls": "The Stellar Cathedral",
    "Prismatic Sharks": "Beacon Realm",
    "Scarlet Phoenixes": "Vault Bastion",
    "Velvet Rhinos": "The Empyrean Nova",
    "Blazing Dragons": "The Den Spire",
    "Celestial Rhinos": "The Runic Runic",
    "Onyx Blades": "Prism Granite Oblivion",
    "Runestone Lynx": "Cradle Vault",
    "Marble Wolves": "Citadel Arena",
    "Hollow Wolves": "Infernal Citadel",
    "Ethereal Stingers": "The Oblivion Crucible",
    "Storm Sabers": "The Arcane Dome",
    "Inferno Lynx": "The Runic Citadel",
    "Lunar Dragons": "The Astral Ascendant",
    "Gilded Griffons": "Golden Wing Arena",
    "Aurora Stallions": "Stellar Lunar",
    "Emerald Eagles": "Infernal Dominion",
    "Zephyr Vortex": "Oblivion Realm",
    "Solar Raptors": "The Crystal Tempest",
    "Frostborn Hurricanes": "The Mystic Monolith",
    "Radiant Sylphs": "Skygleam Field",
    "Emerald Chargers": "Granite Core",
    "Mythic Falcons": "Radiant",
    "Onyx Lynx": "Run Bastion",
    "Ecliptic Raptors": "The Den Gate",
    "Stormborn Tigers": "Spire Gate",
    "Eternal Bulls": "Oblivion Temple",
    "Auric Panthers": "The Celestial Cathedral",
    "Scarlet Blades": "Titan Sanctum",
    "Obsidian Stingers": "River Halo",
    "Abyssal Titans": "Tempest Core",
    "Stellar Cougars": "The Velvet Forge",
    "Blazing Leopards": "Cyclone Spire",
    "Silver Blades": "The Stellar Paradox",
    "Lunar Serpents": "Moonfang Field",
    "Solaris Raiders": "Infernal",
    "Feral Chargers": "Beacon Citadel",
    "Grove Bulls": "Citadel Vault",
    "Spectral Dragons": "Astral Conflux",
    "Rune Tigers": "The Oblivion Prism",
    "Ashen Wolves": "Radiant Halo Celestial",
    "Radiant Hurricanes": "Oblivion Citadel Cradle",
    "Runic Guardians": "Titan Monolith",
    "Auric Sabers": "Astral Halo",
    "Cosmic Stallions": "The Umbral Vortex",
    "Tempest Panthers": "Frosted Nexus",
    "Empyreal Tigers": "Oblivion Empyrean",
    "Mystic Phoenixes": "Celestial Ascension",
    "Celestial Raiders": "Infernal Forge",
    "Sable Leopards": "Oblivion Nucleus",
    "Mythic Scorpions": "Lair Spire",
    "Lunar Stingers": "The Stormborn Chasm",
    "Oceanic Leopards": "Hollow Forge",
    "Hollow Mavericks": "Zephyr Core",
    "Shadow Centaurs": "The Oblivion Core",
    "Storm Eagles": "Cyclone Bastion",
    "Voltaic Cougars": "Ember Prism",
    "Hollow Leopards": "The Stellar Horizon",
    "Oblivion Wolves": "Shadowclaw Stadium",
    "Sable Phoenixes": "Celestial Paradox",
    "Runic Strikers": "Iron Ember",
    "Spectral Cobras": "The Cyclone Forge",
    "Phantom Basilisks": "Ghostfang Arena",
    "Thunder Strikers": "The Umbral Halo",
    "Scarlet Dragons": "The Nest Forge",
    "Zephyr Rhinos": "The Run Forge",
    "Radiant Leopards": "The Celestial Crucible",
    "Aether Titans": "Emerald Sanctum",
    "Steel Titans": "Iron Realm",
    "Prismatic Hawks": "Arcane Pinnacle",
    "Oblivion Vortex": "Aether Drift",
    "Prismatic Falcons": "Arcane Cradle",
    "Aurora Rhinos": "Lunar Realm",
    "Phantom Bulls": "The Realm Zephyr",
    "Empyreal Knights": "The Runic",
    "Oceanic Scorpions": "Den Eclipse",
    "Emberfall Centaurs": "The Run Spire",
    "Mythic Vipers": "The Oblivion Arcane",
    "Tempest Vipers": "Frozen Aegis",
    "Aether Dragons": "Frozen Spire",
    "Storm Falcons": "The Crystal Forge",
    "Aurora Falcons": "Luminous Gate",
    "Verdant Wolves": "Nova Core",
    "Astral Raptors": "Starclaw Colosseum",
    "Grove Blades": "The Nova Haven",
    "Obsidian Krakens": "The Blacktide",
    "Empyreal Vortex": "Umbral Monolith",
    "Spectral Lynx": "Void Ascension",
    "Ember Cobras": "The Prism Arcane",
    "Cosmic Tigers": "Aether Cradle",
    "Abyssal Stallions": "The Obsidian Vault",
    "Titanic Scorpions": "Nova Sphere",
    "Thunder Raiders": "Eclipse Dominion",
    "Rune Hurricanes": "Crystal Gate",
    "Ember Hawks": "The Void Haven",
    "Arcane Tigers": "The Dominion Haven",
    "Ecliptic Sharks": "The Stellar Zenith",
    "Solar Phoenixes": "Iron Drift",
    "Tempest Cougars": "Titan Vault",
    "Cosmic Raptors": "Eternal Infernal",
    "Storm Griffins": "Thunder Vault",
    "Steel Dragons": "Aegis Spire",
    "Grove Stingers": "Celestial Dome",
    "Lunar Wolves": "Stellar Obelisk",
    "Luminous Blades": "The Solaris Pinnacle",
    "Stone Pioneers": "The Stormborn Sanctum",
    "Velvet Phoenixes": "The Gate Gate Granite",
    "Mythic Strikers": "Dominion Velvet Haven",
    "Feral Bulls": "Celestial Starforge",
    "Ecliptic Mavericks": "The Nova Chasm",
    "Blazing Hawks": "The Velvet Continuum",
    "Draconic Lynx": "Aegis Drift",
    "Abyssal Rhinos": "The Celestial Nexus",
    "Arcane Stallions": "Mystic Vault",
    "Sable Gargoyles": "Stonewing Arena",
    "Mythic Bears": "The Iron Aether Solaris",
    "Luminous Bulls": "The Ember Core",
    "Velvet Griffins": "Twilight Obelisk",
    "Abyssal Sabers": "Arcane Ascension",
    "Lunar Cobras": "The Gate Stellar",
    "Blazing Falcons": "Oblivion Gate",
    "Savage Rhinos": "The Thunderhold",
    "Sable Bulls": "Celestial Gate",
    "Nebula Warhounds": "Cosmic Kennel",
    "Verdant Stingers": "The Celestial Eclipse",
    "Verdant Rhinos": "The Crystal Crucible",
    "Stellar Bears": "The Stellar Pinnacle",
    "Oblivion Pioneers": "Granite Halo",
    "Violet Wolves": "The Stellar Vault",
    "Eternal Panthers": "Celestial Vortex",
    "Thorn Pioneers": "The Cyclone Monolith",
    "Phantom Ogres": "Ghoststone Field",
    "Inferno Mavericks": "The Stellar Forge",
    "Cobalt Manticores": "Azure Fang Stadium",
    "Ember Scorpions": "The Arcane Prism",
    "Granite Blades": "Radiant Spire",
    "Draconic Chargers": "The Celestial Realm",
    "Empyreal Raptors": "The Halo Iron",
    "Verdant Hydras": "Emerald Coil Stadium",
    "Nebular Hawks": "Empyrean Core",
    "Aether Warthogs": "The Oblivion Granite",
    "Silver Wolves": "Eternal Chasm",
    "Obsidian Leopards": "The Storm Citadel",
    "Stellar Titans": "The Tempest Temple",
    "Frost Revenants": "Iceshard Stadium",
    "Marble Guardians": "The Oblivion Aegis",
    "Thorn Dragons": "Arcane Nexus",
    "Savage Bulls": "Mystic Radiant",
    "Titanic Centaurs": "Monolith Iron",
    "Thorn Knights": "The Zephyr Void",
    "Phantom Falcons": "The Eclipse Vault",
    "Sable Cougars": "The Arcane Gate",
    "Stone Wolves": "Ashen Gate",
    "Empyreal Sabers": "Nova Ember Zephyr",
    "Thorn Chargers": "The Stellar Bastion",
    "Golden Sharks": "Arcane Forge",
    "Granite Knights": "Astral Forge",
    "Obsidian Panthers": "The Radiant Forge",
    "Oblivion Mavericks": "Granite",
    "Shadowborn Falcons": "Astral Empyrean",
    "Verdant Raiders": "The Infernal Vault",
    "Verdant Eagles": "The Glacial Sanctum",
    "Tempest Raiders": "The Crystal Beacon",
    "Shadowborn Cougars": "The Solaris Forge",
    "Phantom Sharks": "The Crystal Core",
    "Frostborn Pioneers": "Ember Cradle",
    "Grove Falcons": "The Bastion Bastion",
    "Marble Rhinos": "The Obsidian Drift",
    "Frostfang Wolves": "Icepaw Grounds",
    "Emberfall Rhinos": "Crystal Prism",
    "Draconic Dragons": "The Arcane Vault",
    "Cosmic Eagles": "Umbral Sanctum",
    "Voltaic Raiders": "Arcane Prism",
    "Phantom Pioneers": "Forge",
    "Echo Cobras": "The Nest Gate",
    "Solar Drakes": "Sunfire Grounds",
    "Spectral Mavericks": "The Ember Gate",
    "Emerald Titans": "Spire Sanctum",
    "Violet Gargoyles": "Amethyst Wing Stadium",
    "Luminous Wolves": "The Hollow Gate",
    "Stone Dragons": "River Forge",
    "Arcane Warthogs": "The Celestial Conflux",
    "Ember Mavericks": "The Oblivion Haven Celestial",
    "Arcane Rhinos": "Stellar Prism",
    "Cobalt Bears": "The Stellar Monolith",
    "Mystic Sharks": "The Silver Apex",
    "Shadowborn Scorpions": "Stellar Cathedral",
    "Oblivion Cougars": "The Nocturne Forge",
    "Spectral Hurricanes": "The Eclipse Haven",
    "Steel Sharks": "The Oblivion Vault",
    "Ashen Leopards": "Lair Sanctum",
    "Nebular Chargers": "Zephyr Citadel",
    "Draconic Centaurs": "The Tempest Nexus",
    "Nebular Eagles": "Ecliptic Domain",
    "Runestone Bulls": "Void Halo Infernal",
    "Titanic Vipers": "Runic Prism",
    "Golden Warthogs": "The Celestial Forge",
    "Thunder Manticores": "Stormclaw Grounds",
    "Feral Tigers": "Emberwatch Arena",
    "Dread Harpies": "Nightwind Field",
    "Stone Hawks": "Arcane",
    "Aurora Warthogs": "The Arcane Crown",
    "Voltaic Falcons": "Stellar Ascendant",
    "Ember Warthogs": "The Eternal Core",
    "Infernal Wyrms": "Blazespire Grounds",
    "Feral Vortex": "Hollow",
    "Cobalt Cougars": "The Obsidian Spire",
    "Mystic Eagles": "The Halo Forge",
    "Shadow Dragons": "Spire Void",
    "Glacial Raptors": "Continuum Hollow",
    "Steel Cobras": "Bastion Granite",
    "Violet Hawks": "The Stellar Realm",
    "Iron Drakes": "Steelspire Arena",
    "Savage Cougars": "Sky Vault",
    "Echo Strikers": "The Nova Halo",
    "Onyx Rhinos": "Arcane Monolith",
    "Shadow Knights": "The Mystic Runic",
    "Granite Hurricanes": "Celestial Sphere",
    "Echo Vortex": "Zephyr",
    "Runestone Leopards": "The Granite Vault",
    "Cobalt Strikers": "Citadel Mystic",
    "Frost Stallions": "Arena Infernal",
    "Onyx Sabers": "Oblivion Sanctuary",
    "Onyx Scorpions": "Spire",
    "Echo Falcons": "Run Gate",
    "Glacial Sabers": "The Eclipse Chasm",
    "Aurora Strikers": "Blazing Paradox",
    "Stellar Guardians": "Celestial Halo Granite",
    "Ashen Hurricanes": "The Astral Sanctum",
    "Runestone Cougars": "Haven Dominion",
    "Stellar Rhinos": "Eclipse",
    "Ashen Lynx": "Arcane Radiant",
    "Frost Sabers": "Frosted Forge",
    "Ashen Blades": "The Shadow Spire",
    "Frost Raiders": "The Obelisk Hollow",
    "Phoenix Vortex": "The Inferno Vault",
    "Emerald Panthers": "Nova Zenith",
    "Eternal Stingers": "The Astral Vortex",
    "Aurora Cobras": "Ember Crystal",
    "Shadow Wolves": "The Aegis Astral",
    "Golden Vipers": "Den Realm",
    "Solar Eagles": "Blazing Nucleus",
    "Emerald Scorpions": "The Emerald Eyrie",
    "Emerald Wolves": "Nova Continuum",
    "Eternal Wolves": "Sanctum Velvet Zephyr",
    "Stormy Dragons": "Dominion Gate Radiant",
    "Dusk Bulls": "Astral Haven",
    "Arcane Leopards": "The Oblivion Temple",
    "Stormy Raiders": "The Thunder Vault",
    "Emerald Cougars": "The River Citadel",
    "Stormbreak Falcons": "The Cyclone Vault",
    "Oceanic Titans": "The Ember Hollow",
    "Thunder Bears": "Nova Citadel",
    "Riverstone Stingers": "Realm",
    "Glacial Lynx": "Frostfall Arena",
    "Iron Bulls": "The Emerald Sanctum",
    "Violet Panthers": "The Sanctum",
    "Frost Bears": "Crystal Sanctuary",
    "Celestial Panthers": "Beacon Aether",
    "Shadow Scorpions": "The Void Spire",
    "Blazing Strikers": "The Nova Monolith",
    "Titanic Mavericks": "Radiant Stormborn",
    "Tempest Strikers": "The Luminous Vault",
    "Storm Reavers": "Tempest Hold",
    "Violet Hurricanes": "Titan",
    "Blazing Hurricanes": "Astral Sanctum",
    "Celestial Vipers": "Celestial Vault",
    "Dusk Pioneers": "The Solar Gate",
    "Silver Falcons": "Arcane Halo",
    "Radiant Bears": "Citadel Sanctum",
    "Inferno Blades": "The Halo Sanctuary",
    "Iron Tigers": "Arcane Starforge",
    "Violet Pioneers": "The Nova Citadel",
    "Aurora Stingers": "Zephyr Monolith",
    "Scarlet Bulls": "The Celestial Citadel",
    "Shadow Vortex": "Runic Spire",
    "Obsidian Lynx": "The Beacon Void",
    "Golden Knights": "Stellar Gate",
    "Scarlet Scorpions": "Gate Sanctum",
    "Solar Bulls": "Aether Citadel",
    "Cobalt Wolves": "Stellar Aether",
    "Ebon Phantoms": "Darkveil Grounds",
    "Steel Sabers": "Argent Bastion",
    "Solar Centaurs": "Sanctuary Infernal Granite",
    "Phoenix Raiders": "Velvet Astral Spire",
    "Violet Blades": "Void Realm",
    "Golden Bears": "Nest Spire",
    "Arcane Knights": "Arcane Haven Radiant",
    "Eternal Guardians": "The Oblivion Vortex",
    "Luminous Vipers": "The Empyrean Gate",
    "Iron Stallions": "The Stellar Starforge",
    "Riverstone Lynx": "The Arcane Obelisk",
    "Mystic Vortex": "Oblivion Core",
    "Glacial Tigers": "The Frosted Horizon",
    "Tempest Stingers": "Core Eternal",
    "Eternal Vortex": "Monolith Temple",
    "Dusk Cougars": "Temple Arena",
    "Savage Sabers": "The Astral Gate",
    "Phoenix Warthogs": "The Eternal Gate",
    "Solar Panthers": "Helios Bastion",
    "Celestial Wolves": "Arena Runic",
    "Thunder Leopards": "The Temple Umbral",
    "Celestial Cobras": "Solaris Core",
    "Sable Rhinos": "The Hollow Arena",
    "Crystal Drakes": "Shardspire Arena",
    "Stormy Scorpions": "Zephyr Ascension",
    "Twilight Ogres": "Gloamstone Coliseum",
    "Emerald Stallions": "Cradle Drift",
    "Glacial Cobras": "Crystal Spire",
    "Aurora Bears": "Arcane Horizon",
    "Aurora Vipers": "The Eternal Forge",
    "Riverstone Blades": "Iron Dome",
    "Sable Vortex": "The Solaris",
    "Crimson Hurricanes": "The Infernal Spire",
    "Silver Rhinos": "Halo Arcane",
    "Cobalt Sharks": "Nest Cradle",
    "Titanic Vortex": "Sanctuary Runic",
    "Inferno Rhinos": "The Astral Bastion",
    "Stormbreak Lynx": "The Celestial Halo",
    "Savage Phoenixes": "Haven Runic",
    "Titanic Lynx": "Titan Forge",
    "Oceanic Stallions": "Temple Cradle",
    "Stormbreak Blades": "Tempest Obelisk",
    "Radiant Sharks": "Zenith Vault",
    "Arcane Vipers": "The Velvet Sanctum",
    "Eternal Lynx": "Eyrie Runic Hollow",
    "Inferno Bulls": "Ember Bastion",
    "Mystic Scorpions": "Drift Dominion",
    "Titanic Bulls": "Granite Forge",
    "Stormbreak Mavericks": "Sky Gate",
    "Mystic Raptors": "Velvet Gate",
    "Scarlet Sharks": "The Solar Crucible",
    "Mystic Tigers": "The Eternal Dome",
    "Silver Scorpions": "The Nova Aether",
    "Luminous Griffins": "The Arcane Vortex",
    "Emerald Blades": "Nova Nexus",
    "Iron Mavericks": "Crystal Realm",
    "Crimson Panthers": "The Mystic",
    "Stormbreak Titans": "Halo Spire Realm",
    "Obsidian Tigers": "The Astral Drift",
    "Savage Vortex": "Eclipse Eyrie",
    "Obsidian Centaurs": "The Obsidian Core",
    "Skyline Phoenixes": "Celestial Chasm",
    "Vortex Minotaurs": "Whirlspire Field",
    "Savage Falcons": "The Nova Starforge",
    "Radiant Tigers": "The Beacon Citadel",
    "Riverstone Bulls": "Stone Gate",
    "Shadow Panthers": "Nocturne Spire",
    "Mystic Centaurs": "Arcane Spire",
    "Golden Cobras": "Continuum Aether",
    "Eternal Stallions": "Oblivion Obelisk",
    "Arcane Wraiths": "Mystic Hollow",
    "Tempest Scorpions": "Velvet Spire Halo",
    "Riverstone Cougars": "The Lunar Forge",
    "Golden Hawks": "The Thunder Cradle",
    "Silver Raptors": "Den Arena",
    "Aurora Pioneers": "Astral Crucible",
    "Scarlet Centaurs": "Celestial Halo",
    "Obsidian Guardians": "The Iron Nexus",
    "Stormfang Lions": "Thunderpaw Arena",
    "Radiant Guardians": "Celestial Temple",
    "Scarlet Stallions": "The Velvet Bastion",
    "Dusk Centaurs": "Nova Eclipse",
    "Celestial Strikers": "Celestial Eyrie",
    "Celestial Hurricanes": "The Stellar Crucible",
    "Dusk Scorpions": "The Nebula Gate",
    "Golden Bulls": "The Nova Empyrean",
    "Crimson Hawks": "The Pyre Sphere",
    "Skyline Knights": "The Azure Vault",
    "Celestial Lynx": "Starclaw Arena",
    "Glacial Griffins": "Crystal Aether",
    "Radiant Rhinos": "Celestial Crown",
    "Cobalt Leopards": "The Nest Sphere",
    "Riverstone Stallions": "The Granite Citadel",
    "Luminous Titans": "The Halo Eclipse",
    "Phoenix Dragons": "The Umbral",
    "Silver Stallions": "Arcane Zenith",
    "Golden Vortex": "The Arcane",
    "Inferno Phoenixes": "The Obsidian Sanctum",
    "Tempest Raptors": "Stormborn Vault",
    "Shadow Cobras": "The Nova Nucleus",
    "Radiant Strikers": "The Astral Halo",
    "Glacial Wolves": "The Hollow Spire",
    "Crimson Strikers": "The Stellar Arena",
    "Stormy Falcons": "Arena Sanctuary",
    "Celestial Bears": "The Halo Eyrie",
    "Blazing Titans": "Iron Gate",
    "Velvet Sharks": "Eternal Core",
    "Golden Falcons": "Eyrie Continuum",
    "Savage Cobras": "Cradle Bastion",
    "Golden Phoenixes": "The Radiant Summit",
    "Stormbreak Cobras": "Beacon Empyrean",
    "Eternal Raptors": "Dominion Hollow",
    "Frost Tigers": "The Frozen Sanctum",
    "Luminous Warthogs": "The Eternal Titan",
    "Tempest Falcons": "The Tempest Vortex",
    "Violet Titans": "Amethyst Core",
    "Ethereal Wyrms": "Cloudspire Arena",
    "Ebon Drakes": "Nightfire Colosseum",
    "Solar Lynx": "Sanctum Hollow",
    "Eclipse Seraphs": "Duskwing Field",
    "Sable Titans": "The Nova Cradle",
    "Tempest Centaurs": "Tempest Granite",
    "Frost Panthers": "Aegis Halo",
    "Skyline Mavericks": "The Astral Crown",
    "Aurora Blades": "Velvet Nexus",
    "Steel Warthogs": "The Ember Crucible",
    "Savage Vipers": "The Twilight Gate",
    "Tempest Chargers": "The Mystic Stormborn",
    "Stormbreak Stallions": "The Cyclone Spire",
    "Blazing Centaurs": "The Celestial Arena",
    "Emerald Bulls": "The Arcane Core",
    "Solar Pioneers": "The Ashen Drift",
    "Dusk Panthers": "Cradle Cradle",
    "Steel Stallions": "Aegis Prism",
    "Oceanic Centaurs": "The Umbral Nova",
    "Mystic Hawks": "The Celestial Prism",
    "Radiant Stingers": "The Haven",
    "Onyx Guardians": "Oblivion Crown",
    "Obsidian Dragons": "The Nocturne Sanctum",
    "Radiant Warthogs": "Aurora Gate",
    "Titanic Titans": "Nova Spire",
    "Celestial Scorpions": "The Stormborn Temple",
    "Frost Cobras": "Core Vault",
    "Arcane Raptors": "The Radiant Citadel",
    "Oceanic Warthogs": "Hollow Eternal",
    "Glacial Centaurs": "Astral Eyrie",
    "Onyx Sphinxes": "Shadowpaw Grounds",
    "Silver Strikers": "The Hollow Ascendant",
    "Riverstone Panthers": "The Nova Nexus",
    "Crimson Falcons": "The Blazing Core",
    "Iron Eagles": "The Iron Gate",
    "Blazing Knights": "Emberforge Arena",
    "Stormbreak Strikers": "Arcane Core",
    "Radiant Mavericks": "Celestial Dominion Stellar",
    "Luminous Eagles": "The Halo Gate",
    "Frost Strikers": "Umbral Arena",
    "Riverstone Dragons": "The Draconic Spire",
    "Frost Cougars": "Glacial Ascendant",
    "Obsidian Cobras": "Runic Stellar",
    "Arcane Hawks": "Celestial Realm",
    "Onyx Falcons": "The Nest Spire",
    "Phoenix Wolves": "Celestial Spire",
    "Thunder Blades": "Stormborn Horizon",
    "Velvet Panthers": "The Shadow Crucible",
    "Stormy Phoenixes": "Cyclone Core",
    "Nether Behemoths": "The Shadow",
    "Savage Stingers": "Astral Zephyr",
    "Sable Lynx": "The Den Arena",
    "Frost Phoenixes": "The Tempest Velvet Haven",
    "Mystic Mavericks": "The Nova Temple",
    "Steel Knights": "The Astral Obelisk",
    "Obsidian Scorpions": "The Celestial Core",
    "Dusk Knights": "Empyrean Void",
    "Aurora Sirens": "Skywave Arena",
    "Dusk Wolves": "Nova Forge",
    "Titanic Bears": "The Stormborn Runic",
    "Steel Leopards": "The Bastion Realm",
    "Emerald Cobras": "The Lunar Core",
    "Scarlet Falcons": "Run Core",
    "Radiant Falcons": "The Bastion Umbral",
    "Sable Wolves": "Ember Aegis Ember",
    "Golden Titans": "Stellar Crucible",
    "Emerald Raptors": "The Nova Crucible",
    "Shadow Raiders": "The Dusk Haven",
    "Titanic Pioneers": "Iron Spire",
    "Velvet Raptors": "The Ebon Forge",
    "Glacial Cougars": "Crystal Cathedral",
    "Titanic Tigers": "Obelisk Eyrie Titan",
    "Emerald Sabers": "The Emerald Vault",
    "Thunder Pioneers": "The Obelisk Ember",
    "Silver Vortex": "The Astral Crucible",
    "Aurora Basilisks": "Radiant Fang Stadium",
    "Crimson Cobras": "Ember Spire",
    "Skyline Warthogs": "Oblivion Drift",
    "Riverstone Phoenixes": "Gate Radiant",
    "Obsidian Chargers": "Aether Radiant Iron",
    "Savage Lynx": "Stellar Citadel",
    "Arcane Strikers": "The Nova Pinnacle",
    "Aurora Griffins": "The Dawnbreak Citadel",
    "Celestial Phoenixes": "The Continuum Solaris",
    "Titanic Sharks": "The Realm Crystal",
    "Velvet Cobras": "The Velvet Gate",
    "Violet Sabers": "The Celestial Zenith",
    "Velvet Bears": "The Mystic Core",
    "Arcane Leviathans": "Mystic Wave Coliseum",
    "Iron Phoenixes": "The Titan Crucible",
    "Stormy Titans": "Continuum Sanctuary Umbral",
    "Emerald Hawks": "Stone Vault",
    "Stormbreak Stingers": "The Crystal Vault",
    "Savage Titans": "The Stellar Ascendant",
    "Shadow Rhinos": "Dusk Monolith",
    "Radiant Pioneers": "The Radiant Horizon",
    "Scarlet Knights": "Stormborn Arena",
    "Stormbreak Scorpions": "The Empyrean Nova Tempest",
    "Phoenix Cougars": "Nova Bastion",
    "Velvet Hawks": "The Velvet Ascendant",
    "Savage Griffins": "Eyrie Eyrie",
    "Emerald Knights": "The River Nexus",
    "Violet Stingers": "The Frigid Spire",
    "Scarlet Vortex": "The Nebular Spire",
    "Emerald Dragons": "Granite Sanctum",
    "Shadow Chargers": "Oblivion Halo",
    "Aurora Phoenixes": "Arena Monolith",
    "Thunder Hurricanes": "Stormborn Core",
    "Cobalt Griffins": "Eyrie Dome",
    "Skyline Eagles": "Lunar Mystic",
    "Titanic Leopards": "River Crown",
    "Skyline Bulls": "Eyrie Runic",
    "Steel Panthers": "Stellar Paradox",
    "Velvet Wolves": "Velvet Vault",
    "Phoenix Vipers": "Arcane Ascendant",
    "Stormy Vortex": "Tempest Citadel",
    "Feral Krakens": "Tidebreaker Arena",
    "Solar Titans": "The Runic Sanctum",
    "Onyx Eagles": "The Iron Sanctum",
    "Luminous Guardians": "Radiant Eclipse",
    "Blazing Bulls": "Lair Vault",
    "Infernal Jackals": "Blazeward Arena",
    "Skyline Hawks": "Prism Tempest",
    "Scarlet Rhinos": "Celestial Continuum",
    "Stormy Bears": "Sanctum Continuum",
    "Steel Phoenixes": "The Radiant Crucible",
    "Thunder Vipers": "The Sky Pinnacle",
    "Tempest Tigers": "Mystic Void",
}

teams = dict(sorted(teams.items()))

PLACEHOLDER_COLOR = (15, 234, 234) # #0feaea
# --- HELPER FUNCTIONS ---
def replace_color(img_path, new_color, save_path):
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == PLACEHOLDER_COLOR:
            new_data.append(new_color + (item[3],))
        else:
            new_data.append(item)
    img.putdata(new_data)
    img.save(save_path)

# Create per-division strength lists
league_strength_dict = {}
for league, divisions in league_names.items():
    for div in divisions:
        league_strength_dict[div] = league_strengths.copy()

all_divisions_ordered = list(league_strength_dict.keys())

# --- CREATE A POOL OF 16 COLORS FOR EACH TEMPLATE (fixed & faster) ---
template_colors = {}
vibrant_colors = [
    (220, 38, 38),    # Strong Red
    (0, 123, 255),    # Bright Blue
    (0, 184, 148),    # Teal Green
    (255, 159, 28),   # Warm Orange
    (255, 193, 7),    # Golden Yellow
    (156, 39, 176),   # Vivid Purple
    (0, 200, 83),     # Emerald Green
    (233, 30, 99),    # Pinkish Red
    (255, 87, 34),    # Deep Orange
    (63, 81, 181),    # Indigo Blue
    (3, 169, 244),    # Sky Blue
    (98, 104, 189),   # Light Purple
    (255, 111, 0),    # Orange Accent
    (171, 71, 188),   # Bright Violet
    (205, 220, 57),   # Lime Yellow
    (255, 64, 129),   # Vibrant Pink
]

for template_file in os.listdir(logo_templates_path):
    if template_file.lower().endswith((".png", ".jpg", ".jpeg")):
        # Make a copy of the palette for each template so they don't share the same list
        template_colors[template_file] = vibrant_colors.copy()  # [CHANGED]

# Build a list of (template_file, color) pairs (exactly one pair per logo you want)
assignment_pairs = []
for tfile, colors in template_colors.items():
    for color in colors:
        assignment_pairs.append((tfile, color))

# If there are more teams than pairs, repeat the pairs (shouldn't be needed if 40*16 == 640)
num_teams = len(teams)
if len(assignment_pairs) < num_teams:
    import math
    reps = math.ceil(num_teams / len(assignment_pairs))
    assignment_pairs = (assignment_pairs * reps)[:num_teams]  # [CHANGED]

random.shuffle(assignment_pairs)  # shuffle assignments so templates/colors are distributed  # [CHANGED]

# Preload each template image to avoid opening it repeatedly
template_images = {}
for tfile in template_colors.keys():
    path = os.path.join(logo_templates_path, tfile)
    template_images[tfile] = Image.open(path).convert("RGBA")  # [CHANGED]

# --- ASSIGN TEAMS (replace the previous while-loop approach) ---
teams_json = []
division_index = 0

for team_name, stadium in teams.items():
    # League assignment in order
    division = all_divisions_ordered[division_index % len(all_divisions_ordered)]
    division_index += 1
    
    # Strength assignment
    strength_list = league_strength_dict[division]
    strength = random.choice(strength_list)
    strength_list.remove(strength)
    
    # Take the next (template, color) pair (no searching/removals)
    template_file, color = assignment_pairs.pop()  # [CHANGED]
    
    # Work on an in-memory copy of the preloaded template (avoid reopening file)
    img = template_images[template_file].copy()  # [CHANGED]
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == PLACEHOLDER_COLOR:
            new_data.append(color + (item[3],))
        else:
            new_data.append(item)
    img.putdata(new_data)
    
    logo_save_path = os.path.join(team_logos_path, f"{team_name.replace(' ', '_')}.png")
    img.save(logo_save_path)
    
    # Year created
    year_created = random.randint(1950, 2010)
    
    team_entry = {
        "name": team_name,
        "strength": strength,
        "logo": logo_save_path,
        "year_created": year_created,
        "stadium": stadium,
        "league": division
    }
    
    teams_json.append(team_entry)

# Close preloaded images
for im in template_images.values():
    try:
        im.close()
    except Exception:
        pass

# --- CREATE LEAGUES JSON ---
leagues_json = []
for league, divisions in league_names.items():
    first_division = divisions[0]
    league_logo_path = os.path.join(league_logos_path, f"{first_division.replace(' ', '_')}.png")
    
    for i, division in enumerate(divisions):
        promotion = 0 if i == 0 else 3
        relegation = 0 if i == 3 else 3

        league_above = divisions[i - 1] if i - 1 >= 0 else None
        league_below = divisions[i + 1] if i + 1 < len(divisions) else None

        league_entry = {
            "name": division,
            "logo": league_logo_path,  # just take the first division logo
            "promotion": promotion,
            "relegation": relegation,
            "league_above": league_above,
            "league_below": league_below
        }
        leagues_json.append(league_entry)

# --- SAVE JSON FILES ---
with open("data/teams.json", "w") as f:
    json.dump(teams_json, f, indent=4)

with open("data/leagues.json", "w") as f:
    json.dump(leagues_json, f, indent=4)

print("✅ Generated teams.json and leagues.json with logos, cleaned old files and images.")