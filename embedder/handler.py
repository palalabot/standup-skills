"""RunPod serverless embedding worker (sentence-transformers)."""
import os

MODEL_NAME = os.environ.get("MODEL_NAME", "all-MiniLM-L6-v2")
MAX_TEXTS = 64
MAX_CHARS = 8000

model = None  # loaded in __main__ so tests can import without the model


def validate(inp):
    """Return (action, payload) or raise ValueError."""
    if not isinstance(inp, dict):
        raise ValueError("input must be an object")
    action = inp.get("action")
    if action == "embed":
        texts = inp.get("texts")
        if not isinstance(texts, list) or not texts or len(texts) > MAX_TEXTS:
            raise ValueError(f"texts must be a list of 1-{MAX_TEXTS} strings")
        if not all(isinstance(t, str) and len(t) <= MAX_CHARS for t in texts):
            raise ValueError(f"each text must be a string of <= {MAX_CHARS} chars")
        return action, texts
    if action == "similarity":
        a, b = inp.get("a"), inp.get("b")
        if not all(isinstance(t, str) and 0 < len(t) <= MAX_CHARS for t in (a, b)):
            raise ValueError(f"a and b must be non-empty strings of <= {MAX_CHARS} chars")
        return action, [a, b]
    raise ValueError("action must be 'embed' or 'similarity'")


def handler(job):
    try:
        action, texts = validate(job.get("input"))
    except ValueError as e:
        return {"error": str(e)}
    # normalized vectors: cosine similarity == dot product, also for search in Vercel
    vecs = model.encode(texts, normalize_embeddings=True)
    if action == "embed":
        return {"model": MODEL_NAME, "embeddings": vecs.tolist()}
    return {"model": MODEL_NAME, "score": float(vecs[0] @ vecs[1])}  # cosine, -1..1


if __name__ == "__main__":
    import runpod
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    runpod.serverless.start({"handler": handler})
