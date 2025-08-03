from groq import Groq

def get_groq_response(api_key: str, model: str, messages: list, temperature: float = 0.7) -> str:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
