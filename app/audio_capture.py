import tempfile
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write

# Paramètres par défaut
DURATION = 5    # secondes
FS = 16000      # Hz


def record_chunk(duration: int = DURATION, fs: int = FS) -> Path:
    """
    Enregistre une tranche audio de `duration` secondes et renvoie
    le chemin temporaire du fichier .wav enregistré.
    """
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait() 
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(tmp.name, fs, audio)
    return Path(tmp.name)