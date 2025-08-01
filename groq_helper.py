# groq_helper.py
from groq import Groq

def get_groq_response(api_key, model, messages, temperature=0.7):
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
