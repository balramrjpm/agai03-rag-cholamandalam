import os
import json

from dotenv import load_dotenv

load_dotenv()

RAW_DIR = os.getenv("RAW_DIR")
if RAW_DIR is None:
    raise EnvironmentError("RAW_DIR environment variable must be set")

PROCESSED_DIR = os.getenv(
    "PROCESSED_DIR",
    "data/processed"
)

MAX_CONTENT_LENGTH = int(
    os.getenv("MAX_CONTENT_LENGTH", 2000)
)

os.makedirs(PROCESSED_DIR, exist_ok=True)

for file in os.listdir(RAW_DIR):

    path = os.path.join(
        RAW_DIR,
        file
    )

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    cleaned_content = data["content"][
        :MAX_CONTENT_LENGTH
    ]

    output = {
        "url": data["url"],
        "title": data["title"],
        "content": cleaned_content
    }

    output_path = os.path.join(
        PROCESSED_DIR,
        file
    )

    with open(output_path, "w", encoding="utf-8") as out:

        json.dump(
            output,
            out,
            indent=4,
            ensure_ascii=False
        )

print("Preprocessing Completed")
