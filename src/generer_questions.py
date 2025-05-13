import os
import json
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("LMSTUDIO_MODEL_NAME", "mistral-nemo-instruct-2407")
CONFIG_PATH = "config.yaml"
OUTPUT_PATH = "questions.json"

def generate_questions_from_topic(topic):
    prompt = f"""
You are helping with a research study on the topic: "{topic}".

Generate 10 to 15 well-formulated, in-depth research questions **in English**, organized into 2 to 5 coherent themes. Each question must be clearly related to the topic and avoid vague or generic phrasing.

Only output valid JSON in the following format (nothing before or after it):

{{
  "themes": {{
    "Theme 1": ["Question 1", "Question 2", "..."],
    "Theme 2": ["Question 3", "Question 4", "..."]
  }}
}}
""".strip()

    print("\n📨 Prompt envoyé au LLM :\n" + prompt)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(f"{API_BASE}/chat/completions", json=payload)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à LM Studio : {e}")
        return None

    print("\n🛰️ Réponse JSON brute :")
    print(response.text)

    if response.status_code != 200:
        raise Exception(f"❌ Erreur HTTP {response.status_code} : {response.text}")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Erreur lors de l'extraction du message.")
        raise e

    if not content:
        print("⚠️ Le contenu retourné est vide.")
        return None

    print("\n📄 Contenu texte retourné :")
    print(content)

    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("❌ Erreur de décodage JSON.")
        raise e

def main():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    topic = config.get("topic")
    if not topic:
        print("❌ Aucun sujet (topic) défini dans config.yaml.")
        return

    print(f"🧠 Génération des questions à partir du sujet : {topic}")
    questions_data = generate_questions_from_topic(topic)

    if questions_data is None:
        print("❌ Aucune donnée à enregistrer.")
        return

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Questions enregistrées dans {OUTPUT_PATH}")

if __name__ == "__main__":
    main()