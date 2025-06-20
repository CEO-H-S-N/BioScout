import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_knowledge_snippets(folder_path):
    """
    Loads text snippets from .txt files in the folder,
    returns dict of {filename: snippet_text}
    """
    snippets = {}
    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                snippets[file] = f.read()
    return snippets

def get_top_snippet(query, snippets_dict, return_score=False, threshold=0.35):
    """
    Returns the most relevant snippet based on semantic similarity,
    and falls back to keyword match if all scores are too low.
    
    Params:
        query (str): The user's question
        snippets_dict (dict): filename -> snippet text
        return_score (bool): Whether to return the score along with the snippet
        threshold (float): Minimum similarity to accept a semantic match

    Returns:
        str or (str, float): Top snippet, optionally with its similarity score
    """
    snippets = list(snippets_dict.values())
    snippet_embeddings = model.encode(snippets)
    query_embedding = model.encode([query])[0]

    scores = cosine_similarity([query_embedding], snippet_embeddings)[0]
    top_idx = scores.argmax()
    top_snippet = snippets[top_idx]
    top_score = scores[top_idx]

    # Fallback: keyword match if similarity is low
    if top_score < threshold:
        for snippet in snippets:
            if any(word.lower() in snippet.lower() for word in query.lower().split()):
                top_snippet = snippet
                break  # take the first matching keyword-based snippet

    return (top_snippet, top_score) if return_score else top_snippet
