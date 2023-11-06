import openai
import os
import environ 
from decouple import Config, Csv

env = environ.Env()
environ.Env.read_env()
config = Config('/.env')

openai.api_key = os.getenv("OPENAI_API_KEY")


# Maintenant, vous pouvez utiliser OPEN_API_KEY dans votre code OpenAI

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are an expert in creating descriptions for fictional universes."},
    {"role": "user", "content": "Generate a description for the universe {universe_name}."}
  ]
)

print(completion.choices[0].message)
