import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()
API_BASE = os.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("LMSTUDIO_MODEL_NAME", "mistral-nemo-instruct-2407")

# Charger les questions depuis questions.json
with open("questions.json", "r", encoding="utf-8") as f:
    questions_data = json.load(f)

# Créer le dossier de sortie
Path("syntheses").mkdir(exist_ok=True)

# Fonction d'appel à LM Studio
def generer_synthese(question, theme=None):
    prompt = f"""
Tu es un assistant de recherche. Voici une question de recherche :

🧠 Question : "{question}"

Rédige une synthèse structurée (3 à 5 paragraphes) à partir des connaissances générales, en mettant en valeur les idées principales, enjeux, défis et opportunités liés à ce sujet.

Si pertinent, ajoute des exemples ou cas d'usage.
Réponds en français uniquement.
    """.strip()

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 1024
    }

    response = requests.post(f"{API_BASE}/chat/completions", json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# Boucle sur chaque question
for theme, questions in questions_data["themes"].items():
    for i, question in enumerate(questions, 1):
        print(f"🔍 Génération pour la question : {question[:60]}...")

        try:
            texte = generer_synthese(question, theme)
        except Exception as e:
            print(f"❌ Erreur : {e}")
            continue

        # Nettoyage du nom de fichier
        filename = f"{theme.replace(' ', '_')}_{i:02d}.md"
        filepath = Path("syntheses") / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {question}\n\n{texte}\n")

        print(f"✅ Sauvegardé dans {filepath}")