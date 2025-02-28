from transformers import pipeline

generator = pipeline("text-generation", model="facebook/opt-1.3b")

def generate_cold_message(name, company):
    prompt = f"Write a cold email to {name} at {company} introducing our web development services."
    response = generator(prompt, max_length=150, do_sample=True)
    return response[0]['generated_text']
