def classify_vector(vector, classifier) -> dict:
    """
    vector: csr_matrix del vectorizer
    classifier: MLPClassifier ya cargado (desde app.state)
    returns: dict con label y scores
    """
    label = classifier.predict(vector)[0]
    probas = classifier.predict_proba(vector)[0]
    classes = list(classifier.classes_)

    def get_score(name):
        return float(probas[classes.index(name)]) if name in classes else 0.0

    return {
        "label":       label,
        "score_alta":  get_score("Alta"),
        "score_media": get_score("Media"),
        "score_baja":  get_score("Baja"),
    }
