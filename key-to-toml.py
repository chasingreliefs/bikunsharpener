import json
import os  # Tambahkan import modul os
import toml

output_file = ".streamlit/secrets.toml"

# Pastikan folder .streamlit ada
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

with open("firestore-key.json") as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open(output_file, "w") as target:
    target.write(toml_config)
