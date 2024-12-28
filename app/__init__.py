from dotenv import load_dotenv
import os

load_dotenv()

for key, value in os.environ.items():
    globals()[key] = value