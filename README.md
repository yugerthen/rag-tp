# RAG - ChromaDB + sentence-transformers + Groq

Un RAG minimal en 3 briques : base vectorielle persistante, agent moderateur, orchestration RAG.
Corpus : 200 phrases absurdes sur le village fictif de Villebrume-les-Cuillieres.

## Installation

1. Cloner le depot : git clone https://github.com/yugerthen/rag-tp.git
2. Creer et activer un environnement virtuel : python -m venv venv puis .\\venv\\Scripts\\Activate.ps1
3. Installer les dependances : pip install -r requirements.txt
4. Copier le contenu de .env.example dans un fichier .env et renseigner votre cle API Groq (console.groq.com)

## Usage

python rag.py

## Architecture

* vectordb.py : base vectorielle ChromaDB persistante (creation, rechargement, recherche)
* moderator.py : agent moderateur anti prompt injection (sortie JSON via Groq)
* rag.py : orchestration complete (moderation puis retrieval puis generation)
* config.py : constantes centralisees (modeles, chemins)
* prompt\_rag.txt / prompt\_moderator.txt : prompts systeme externalises

## Reponses aux questions du sujet

### Bug silencieux evite par le stockage du modele dans les metadonnees de la collection

Si le modele d'embedding change dans la config sans que la base soit reindexee, les vecteurs stockes
et les vecteurs des nouvelles questions ne seraient plus dans le meme espace geometrique. La recherche
donnerait des resultats incoherents sans qu'aucune erreur ne soit levee. Stocker le nom du modele dans
la collection garantit qu'on recharge toujours le bon modele, quelle que soit la config du jour.

### Pourquoi un modele dedie pour la moderation plutot qu'une instruction dans le prompt du RAG

Un modele specialise dans la classification de securite est entraine specifiquement pour detecter les
tentatives de detournement, ce qui le rend plus fiable qu'une simple instruction textuelle noyee dans
un prompt deja charge d'autres consignes. Cela separe aussi les responsabilites : le RAG se concentre
sur la reponse, le moderateur sur la securite, et l'appel au LLM principal n'a lieu qu'apres validation.

### Section 6 - Mise a l'epreuve

1. Qui intercepte : la classe Moderator, appelee en premier dans answer\_question(), avant tout retrieval et tout appel au LLM principal.
2. Sans moderateur : le contenu factuel reste globalement correct grace au prompt systeme strict, mais le ton derape (digressions fantaisistes) : preuve que l'injection influence quand meme le comportement du modele.
3. Question hors corpus : le systeme respecte la consigne et dit qu'il ne trouve pas la reponse, sans inventer.
4. Affirmation fausse : le systeme signale la contradiction et donne la version correcte issue de l'extrait, en citant la source.

