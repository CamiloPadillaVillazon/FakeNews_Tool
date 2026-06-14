def vectorize_text(text: str, vectorizer) -> object:
    """
    text: str limpio
    vectorizer: TfidfVectorizer ya cargado (desde app.state)
    returns: scipy.sparse.csr_matrix
    """
    return vectorizer.transform([text])
