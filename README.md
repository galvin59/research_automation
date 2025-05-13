
# 🧠 Outil automatisé de recherche documentaire (IA)

Ce projet permet de lancer une **recherche documentaire automatisée** sur n’importe quel sujet, en combinant des outils d’intelligence artificielle et des sources académiques. Il produit en sortie une **synthèse structurée** et un **rapport HTML final**.

---

## 🗂 Structure du projet

```
research_automation/
├── main.py                       # Script principal (optionnel)
├── config.yaml                   # Configuration générale (API, sources, topic, etc.)
├── autres_liens.csv              # Liens Perplexity exportés manuellement (un lien par ligne)
├── questions.json                # Questions générées automatiquement à partir du topic
├── sources_combinees_par_question.csv  # Résultat consolidé des sources collectées
├── requirements.txt              # Dépendances Python
├── .env                          # Clés API (CORE)
└── src/
    ├── generer_questions.py      # Étape 0 : Génération automatique des questions
    ├── collecte_sources.py       # Étape 1 : Collecte des sources depuis APIs et autres_liens.csv
    ├── generer_synthese.py       # Étape 2 : Génération de synthèse par question
    └── generer_rapport.py        # Étape 3 : Consolidation en rapport HTML
```

---

## ⚙️ Prérequis

- Python 3.10+
- Un fichier `.env` contenant la variable `CORE_API_KEY` (voir `.env.example`)
- Installation des dépendances :

```bash
pip install -r requirements.txt
```

---

## 🧩 Étapes du pipeline de recherche

### 🔁 Étape 0 — Générer les questions à partir du topic

```bash
python src/generer_questions.py
```

- À partir du champ `topic` dans `config.yaml`, génère des questions pertinentes dans `questions.json`.

---

### 🔍 Étape 1 — Collecte automatique de sources

```bash
python src/collecte_sources.py
```

- Utilise les APIs **Semantic Scholar**, **OpenAlex**, et **CORE** 
- Ajoute les liens contenus dans `autres_liens.csv` (export manuel depuis Perplexity ou autre outil non api-sé, un lien par ligne).
- Résultat dédupliqué dans `sources_combinees_par_question.csv`.

---

### 🧠 Étape 2 — Générer une synthèse par question

```bash
python src/generer_synthese.py
```

- Utilise soit OpenAI (si configuré), soit un modèle local (par ex. via **LM Studio**) en HTTP pour résumer les sources par question.

🔧 Pour LM Studio :
- Activer un serveur local (ex: `localhost:1234`) avec un modèle LLM compatible ChatML (Mistral, LLaMA, etc.).
- Indiquer l'URL dans `config.yaml` (champ `llm_endpoint`).

---

### 🧾 Étape 3 — Générer un rapport HTML complet

```bash
python src/generer_rapport.py
```

- Regroupe toutes les synthèses dans un fichier HTML lisible (`rapport_final.html`).
- Le rapport peut être enrichi automatiquement avec table des matières, titres, et séparateurs.

---

## 🧪 Exemple de fichier `config.yaml`

```yaml
topic: "Artificial Intelligence and environmental impact"
autres_liens_csv: "autres_liens.csv"
result_limit: 10
sources:
  semantic_scholar: true
  openalex: true
  core: true
llm:
  provider: "openai"  # ou "local"
  openai_api_key: "sk-..."  # requis si provider = openai
  llm_endpoint: "http://localhost:1234/v1/chat/completions"  # si provider = local
```

---

## 🔐 Exemple de `.env`

```
CORE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✨ Résultat final

Le rapport est généré automatiquement en HTML avec une synthèse par question. Il peut être ouvert directement dans un navigateur.

---

## 📌 À propos

Ce projet est conçu pour faciliter les recherches documentaires rigoureuses à l’aide de l’IA. Il peut s’adapter à tout sujet : environnement, droit, médecine, sociologie, etc.

