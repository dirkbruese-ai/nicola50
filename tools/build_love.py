"""Verschlüsselt den Inhalt der geheimen Herz-Seite (nur für Nici) nach love.js.
Aufruf: python3 tools/build_love.py <inhalt.json> <codewort>
Der Klartext gehört NICHT ins Repo; im Repo liegt nur die verschlüsselte Fassung.
Codewort wird klein geschrieben, ohne Leerzeichen verglichen (siehe normalize in index.html)."""
import base64, json, os, sys, unicodedata
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, word = sys.argv[1], sys.argv[2]
norm = unicodedata.normalize("NFC", "".join(word.lower().split()))
data = json.load(open(src, encoding="utf-8")); data.pop("_hinweis", None)
salt, iv, it = os.urandom(16), os.urandom(12), 200000
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(norm.encode())
ct = AESGCM(key).encrypt(iv, json.dumps(data, ensure_ascii=False).encode(), None)
b = lambda x: base64.b64encode(x).decode()
open("love.js", "w").write("// Verschlüsselt mit tools/build_love.py (nur Nici kennt das Codewort)\n"
                           f"const LOVE = {{\"salt\":\"{b(salt)}\",\"iv\":\"{b(iv)}\",\"it\":{it},\"ct\":\"{b(ct)}\"}};\n")
print("love.js geschrieben,", len(ct), "Bytes")
