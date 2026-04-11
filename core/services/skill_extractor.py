"""
Skill extractor using keyword matching + optional spaCy NLP.
Falls back gracefully if spaCy model is not installed.
"""
import re
from typing import List, Set

SKILL_DICTIONARY = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
        "php", "swift", "kotlin", "go", "golang", "rust", "scala", "r", "dart",
        "lua", "perl", "haskell", "elixir", "matlab",
    ],
    "web_frontend": [
        "html", "css", "react", "reactjs", "angular", "angularjs", "vue", "vuejs",
        "nextjs", "svelte", "jquery", "bootstrap", "tailwind", "tailwindcss",
        "sass", "scss", "redux", "webpack", "vite",
    ],
    "web_backend": [
        "django", "flask", "fastapi", "express", "expressjs", "nodejs", "node.js",
        "spring", "spring boot", "laravel", "rails", "asp.net", "nestjs",
        "graphql", "rest api", "restful", "websocket",
    ],
    "databases": [
        "mongodb", "mysql", "postgresql", "postgres", "redis", "sqlite",
        "cassandra", "elasticsearch", "firebase", "dynamodb", "oracle",
        "mariadb", "neo4j", "mssql", "sql server", "sql",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "git", "github", "gitlab",
        "ci/cd", "devops", "linux", "nginx", "apache", "heroku", "vercel",
    ],
    "data_ai_ml": [
        "machine learning", "deep learning", "data science", "tensorflow",
        "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
        "matplotlib", "seaborn", "opencv", "nlp", "natural language processing",
        "computer vision", "neural network", "data analysis", "power bi",
        "tableau", "spark", "hadoop", "mlops", "airflow",
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "xamarin",
    ],
    "tools_version_control": [
        "git", "github", "gitlab", "bitbucket", "jira", "postman", "figma",
        "jupyter", "vs code", "bash", "linux", "selenium", "jest",
    ],
}

# Flat set for fast lookup
KNOWN_SKILLS: Set[str] = {skill for skills in SKILL_DICTIONARY.values() for skill in skills}


def extract_skills_keyword(text: str) -> List[str]:
    """Fast keyword-matching skill extraction."""
    text_lower = text.lower()
    found: Set[str] = set()
    for skill in KNOWN_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)


def extract_skills_spacy(text: str) -> List[str]:
    """Use spaCy for NER + keyword matching."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return extract_skills_keyword(text)

        doc = nlp(text)
        found: Set[str] = set()
        text_lower = text.lower()

        for skill in KNOWN_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if chunk_text in KNOWN_SKILLS:
                found.add(chunk_text)

        return sorted(found)
    except ImportError:
        return extract_skills_keyword(text)


def extract_skills(text: str) -> List[str]:
    """Main entry point: extract skills from any text."""
    if not text:
        return []
    return extract_skills_spacy(text)
