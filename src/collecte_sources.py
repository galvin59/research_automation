import os
import requests
import pandas as pd
import yaml
import json
from dotenv import load_dotenv

# === Chargement des configurations ===
load_dotenv()
CORE_API_KEY = os.getenv("CORE_API_KEY")

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

with open("questions.json", "r", encoding="utf-8") as f:
    questions_data = json.load(f)

SOURCES = config.get("sources", {})
RESULT_LIMIT = config.get("result_limit", 10)
AUTRES_LIENS_CSV = config.get("autres_liens_csv")
TOPIC = config.get("topic")

# === Fonctions de recherche ===

def search_semantic_scholar(query, limit=10):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,url"
    }
    r = requests.get(url, params=params)
    results = []
    if r.status_code == 200:
        for item in r.json().get("data", []):
            results.append({
                "url": item.get("url"),
                "title": item.get("title", "Titre inconnu"),
                "source": "Semantic Scholar"
            })
    return results

def search_openalex(query, limit=10):
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": limit}
    r = requests.get(url, params=params)
    results = []
    if r.status_code == 200:
        for item in r.json().get("results", []):
            results.append({
                "url": item.get("id"),
                "title": item.get("title", "Titre inconnu"),
                "source": "OpenAlex"
            })
    return results

def search_core(query, limit=10):
    url = f"https://core.ac.uk:443/api-v2/search/{query}"
    headers = {"Authorization": f"Bearer {CORE_API_KEY}"}
    params = {"page": 1, "pageSize": limit, "metadata": True}
    r = requests.get(url, headers=headers, params=params)
    results = []
    if r.status_code == 200:
        for item in r.json().get("data", []):
            urls = item.get("urls", [])
            results.append({
                "url": urls[0] if urls else "",
                "title": item.get("title", "Titre inconnu"),
                "source": "CORE"
            })
    return results

def read_autres_liens(csv_path, topic):
    if not os.path.exists(csv_path):
        print(f"⚠️  Fichier {csv_path} introuvable.")
        return []

    df = pd.read_csv(csv_path, header=None, names=["url"])
    results = []

    for link in df["url"]:
        results.append({
            "url": link,
            "title": "Lien depuis Perplexity",
            "source": "Perplexity",
            "question": topic,
            "theme": topic
        })
    return results

# === Script principal ===

def main():
    all_results = []

    print("🔍 Démarrage de la collecte par question...")
    for theme, questions in questions_data.get("themes", {}).items():
        for question in questions:
            print(f"\n📘 Recherche sur : {question}")

            if SOURCES.get("semantic_scholar", True):
                all_results += [
                    {**res, "question": question, "theme": theme}
                    for res in search_semantic_scholar(question, RESULT_LIMIT)
                ]

            if SOURCES.get("openalex", True):
                all_results += [
                    {**res, "question": question, "theme": theme}
                    for res in search_openalex(question, RESULT_LIMIT)
                ]

            if SOURCES.get("core", True):
                all_results += [
                    {**res, "question": question, "theme": theme}
                    for res in search_core(question, RESULT_LIMIT)
                ]

    # Ajout des liens manuels (autres_liens.csv)
    if AUTRES_LIENS_CSV and TOPIC:
        print(f"\n🔗 Ajout des liens Perplexity depuis {AUTRES_LIENS_CSV}")
        autres_liens = read_autres_liens(AUTRES_LIENS_CSV, TOPIC)
        all_results += autres_liens

    # Déduplication stricte par URL
    df = pd.DataFrame(all_results)
    df = df.drop_duplicates(subset=["url"])

    df.to_csv("sources_combinees_par_question.csv", index=False)
    print(f"\n✅ {len(df)} documents enregistrés dans sources_combinees_par_question.csv (sans doublons)")

if __name__ == "__main__":
    main()