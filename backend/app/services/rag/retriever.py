from pathlib import Path
import re

class RunbookRetriever:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[4] / "runbooks")

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        tokens = set(re.findall(r"[a-z0-9_]+", query.lower()))
        results = []
        for path in self.root.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            score = sum(1 for token in tokens if token in text.lower())
            if score:
                results.append({"source": path.name, "score": score, "content": text[:5000]})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
