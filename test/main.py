options = {
    'windows': {
        "Customizations": "customization.json",
        "Development": "development.json",
        "Drivers": "drivers.json",
        "Essentials": "essentials.json",
        "Games": "games.json",
        "Screen": "screen.json",
        "TI Tools": "ti_tools.json"
        },
    'linux': {
        "Development": "development.json",
        "Drivers": "drivers.json",
        "Essentials": "essentials.json",
        "Games": "games.json",
        "Screen": "screen.json",
        "Servers": "server.json"
    },
    'macos': {
        "Development": "development.json",
        "Essentials": "essentials.json",
        "Screen": "screen.json",
    }
}

data = options["windows"]
list_name = []
list_file = []
for item in data:
    list_name.append(item)
    list_file.append(data[item])

print(list_name)
print(list_file)