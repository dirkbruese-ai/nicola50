"""Teilt das Fotoalbum in öffentlich + nur Familie (Dirk 17.11.).
Aufruf: python3 tools/split_album.py <album-voll.js> <picks-ordner> <familien-passwort>
- Öffentlich: Kapitel "friends" komplett, Beitragsfotos (by) und die in der Auswahlseite getippten Fotos.
- Alle übrigen Fotos wandern nach img/<geheimer Ordner>/ und stehen nur verschlüsselt in fam.js.
Die volle Liste liegt außerhalb des Repos (/mnt/project-files/fotos/album-voll-*.js)."""
import base64, glob, json, os, secrets, shutil, sys, unicodedata
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
src, pdir, word = sys.argv[1:4]
s = open(src, encoding="utf-8").read(); A = json.loads(s[s.index("["):s.rindex("]") + 1])
pub = set()
for f in glob.glob(os.path.join(pdir, "*.json")):
    d = json.load(open(f)); d = d.get("data", d); pub |= {str(x) for x in d["ids"]}
isPub = lambda a: a["c"] == "friends" or a.get("by") or str(a["n"]) in pub
P = [a for a in A if isPub(a)]; F = [a for a in A if not isPub(a)]
# geheimer Ordner: vorhandenen weiterverwenden, sonst neu
old = [d for d in os.listdir("img") if d.startswith("f-")]
dirn = old[0] if old else "f-" + secrets.token_hex(8)
os.makedirs(f"img/{dirn}", exist_ok=True)
def move(n, a, b):
    for suf in ("", "s"):
        x, y = f"img/{a}/{n}{suf}.jpg", f"img/{b}/{n}{suf}.jpg"
        if os.path.exists(x): shutil.move(x, y)
for a in F: move(a["n"], "album", dirn)
for a in P: move(a["n"], dirn, "album")      # falls ein Foto wieder öffentlich wird
open("album.js", "w").write("// Öffentliche Fotos (Auswahl Dirk 17.11.); weitere nur mit Familien-Passwort (fam.js)\nconst ALBUM = "
                            + json.dumps(P, ensure_ascii=False, separators=(",", ":")) + ";\n")
norm = unicodedata.normalize("NFC", "".join(word.lower().split()))
salt, iv, it = os.urandom(16), os.urandom(12), 200000
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(norm.encode())
ct = AESGCM(key).encrypt(iv, json.dumps({"dir": f"img/{dirn}", "items": F}, separators=(",", ":")).encode(), None)
b = lambda x: base64.b64encode(x).decode()
open("fam.js", "w").write(f"// Familienfotos, verschlüsselt mit tools/split_album.py\nconst FAMALBUM = {{\"salt\":\"{b(salt)}\",\"iv\":\"{b(iv)}\",\"it\":{it},\"ct\":\"{b(ct)}\"}};\n")
print(len(P), "öffentlich,", len(F), "nur Familie")
