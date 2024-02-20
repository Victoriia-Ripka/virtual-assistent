from openai import OpenAI

api_key = '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'
client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)

# 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