import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# === Chargement de l'environnement
load_dotenv()
API_BASE = os.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("LMSTUDIO_MODEL_NAME", "mistral-nemo-instruct-2407")
LIMITE_PROMPT = int(os.getenv("LIMITE_CARACTERES_PROMPT", 10000))

# === Préparation
synthese_dir = Path("syntheses")
fichiers = sorted(synthese_dir.glob("*.md"))

def lire_fichier(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def appel_llm(prompt: str, temperature: float = 0.5, max_tokens: int = 1500):
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(f"{API_BASE}/chat/completions", json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def resumer_recursive(text_list, titre="résumés", max_prompt_size=10000, groupe_size=5):
    def join_and_check_size(lst):
        return len("\n\n".join(lst))

    niveau = 1
    while join_and_check_size(text_list) > max_prompt_size:
        print(f"🌀 Résumé récursif niveau {niveau} ({len(text_list)} éléments)...")
        nouveaux_blocs = [text_list[i:i + groupe_size] for i in range(0, len(text_list), groupe_size)]
        nouveaux_resumes = []

        for i, bloc in enumerate(nouveaux_blocs, 1):
            print(f"📉 Résumé groupe {i}/{len(nouveaux_blocs)}...")
            prompt = f"Voici un ensemble de {titre}. Résume les idées principales :\n\n" + "\n\n".join(bloc)
            resume = appel_llm(prompt)
            nouveaux_resumes.append(resume)

        text_list = nouveaux_resumes
        niveau += 1

    print(f"✅ Résumé final sur {len(text_list)} blocs.")
    return appel_llm(f"Voici un ensemble de {titre} condensés. Rédige un résumé exécutif final structuré :\n\n" + "\n\n".join(text_list))

def resumer_par_blocs(synthese_str, bloc_taille=4000):
    # Découper les synthèses en blocs de paragraphes
    paragraphs = synthese_str.split("\n\n")
    blocs, bloc, current_length = [], [], 0

    for p in paragraphs:
        current_length += len(p)
        bloc.append(p)
        if current_length > bloc_taille:
            blocs.append("\n\n".join(bloc))
            bloc, current_length = [], 0
    if bloc:
        blocs.append("\n\n".join(bloc))

    # Résumer chaque bloc
    resumes = []
    for i, b in enumerate(blocs, 1):
        print(f"🪓 Résumé partiel {i}/{len(blocs)}...")
        resume = appel_llm(f"Voici un extrait de synthèses. Résume les points essentiels :\n\n{b}")
        resumes.append(resume)

    # Fusion récursive
    return resumer_recursive(resumes, titre="résumés partiels", max_prompt_size=LIMITE_PROMPT)

# === Assemblage du rapport

contenu = "# Rapport final – IA et environnement\n\n"
contenu += "## Table des matières\n\n"

# Générer la table des matières
for fichier in fichiers:
    titre = fichier.stem.replace("_", " ")
    ancre = titre.lower().replace(" ", "-")
    contenu += f"- [{titre}](#{ancre})\n"
contenu += "\n---\n\n"

# Ajouter toutes les synthèses
toutes_les_syntheses = ""
for fichier in fichiers:
    texte = lire_fichier(fichier)
    toutes_les_syntheses += texte + "\n\n"
    contenu += texte + "\n\n---\n\n"

# Résumé exécutif
print(f"📏 Taille à résumer : {len(toutes_les_syntheses)} caractères")
if len(toutes_les_syntheses) < LIMITE_PROMPT:
    print("🚀 Prompt court, résumé direct...")
    resume = appel_llm(
        f"Voici un ensemble de synthèses. Rédige un résumé exécutif clair et structuré en français :\n\n{toutes_les_syntheses}"
    )
else:
    print("🧠 Trop long, résumé par blocs avec réduction récursive...")
    resume = resumer_par_blocs(toutes_les_syntheses)

# Finaliser
contenu = "# Résumé exécutif\n\n" + resume + "\n\n---\n\n" + contenu

with open("rapport_final.md", "w", encoding="utf-8") as f:
    f.write(contenu)

print("✅ rapport_final.md généré.")

# Export PDF
print("📄 Conversion en PDF...")
os.system("pandoc rapport_final.md -o rapport_final.pdf")
print("✅ rapport_final.pdf généré.")