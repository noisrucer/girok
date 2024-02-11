file_path = "requirements.txt"
poetry_requirements_path = "new_requirements.txt"

new_requirements = ""
with open(file_path, "r") as f:
    while True:
        line = f.readline()[:-1]
        if not line:
            break
        name, version = line.split("==")
        new_line = name + f'="{version}"'
        with open(poetry_requirements_path, "a") as ft:
            ft.write(new_line + "\n")
