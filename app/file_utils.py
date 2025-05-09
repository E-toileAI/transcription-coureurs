import csv
from pathlib import Path

# Emplacement des fichiers CSV
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def list_transcripts(query: str = "") -> list[Path]:
    """Liste les .csv du dossier outputs, triés par date, filtrés par query."""
    files = [p for p in OUTPUT_DIR.glob("*.csv")]
    if query:
        files = [p for p in files if query.lower() in p.name.lower()]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def write_csv(path: Path, rows: list[list], header: list[str] | None = None):
    """
    Ecrit les rows dans le CSV : si le fichier n'existe pas, écrit l'en‑tête.
    """
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new and header:
            writer.writerow(header)
        writer.writerows(rows)


def rename_file(old_path: Path, new_name: str) -> Path:
    """Renomme un fichier dans OUTPUT_DIR."""
    new_path = old_path.with_name(new_name)
    old_path.rename(new_path)
    return new_path