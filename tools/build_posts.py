"""Erzeugt posts.js aus dem Padlet-CSV-Export.
Aufruf: python3 tools/build_posts.py <posts.csv> <photos.json> <media-dir>"""
import csv, json, os, sys

# Gruppe pro Padlet-Beitragsnummer: family, old (Münster Girls), new (From home), aus (Gold Coast)
GROUP = {50: "family", 53: "family", 12: "family", 13: "family", 55: "family",
         37: "old", 81: "old", 82: "old", 14: "old", 15: "old", 2: "old", 22: "old", 33: "old", 47: "old", 49: "old", 54: "old", 25: "old",
         31: "close", 18: "close", 20: "close", 52: "close", 6: "close", 62: "close", 29: "close", 64: "close",
         24: "close", 26: "close", 27: "close", 28: "close", 19: "close", 66: "close", 67: "close", 68: "close",
         3: "aus", 69: "aus", 71: "aus", 10: "aus", 11: "aus", 16: "aus", 17: "aus", 23: "aus", 30: "aus",
         35: "aus", 36: "aus", 40: "aus", 41: "aus", 21: "aus", 72: "aus", 73: "aus", 74: "aus", 75: "aus", 76: "aus", 77: "aus", 79: "aus", 80: "aus"}
# Gold Coast unterteilt (Dirk 16.11.)
TEAM = {72: "Hockey", 17: "Hockey", 21: "Hockey", 11: "Hockey", 69: "Hockey", 71: "Hockey", 3: "School", 41: "School", 23: "School",
        10: "Padel", 30: "Padel", 16: "Padel", 36: "Padel", 35: "Padel", 40: "Padel", 73: "Friends",
        74: "School", 75: "School", 76: "Hockey", 77: "Hockey", 79: "Friends", 80: "School"}  # 72 Angie vorne bei Hockey, 73 Sim einfach Freundin (Dirk 20.11.)
# Reihenfolge innerhalb der Gruppen: Beitragsnummern zuerst in dieser Folge, Rest nach Eingang, LAST ganz ans Ende
ORDER = [50, 53, 12, 13, 55,
         72, 17, 21, 11, 69, 71, 76, 77, 901, 3, 41, 23, 74, 75, 80, 10, 36, 30, 16, 35, 40, 73, 79,
         37, 14, 15, 2, 22, 33, 47, 49, 54, 25, 81,
         # From home (Dirks Liste 16.11.); Platzhalter: Steffi & Hendrik Rinsche, Nicole & Jens Ritter nach 44
         31, 18, 52, 44, 67, 68, 28, 24, 27, 6, 70, 62, 26, 29, 64, 19, 56, 59, 34, 51, 42, 43, 38, 45, 66, 39, 60, 61,
         46, 65, 58, 4, 57, 7, 5, 48, 8, 9, 63, 32]
LAST = []
NAME = {10: "Lieke", 16: "Candice & Brent", 30: "Alex & Lex", 36: "Jess G", 2: "Sonja & Christian", 5: "Uwe", 12: "Die Viersener", 13: "Die Viersener", 15: "Ena",
        18: "Susi & Corinna", 20: "Susi & Corinna", 22: "Catherine", 23: "Kate", 24: "DEHNS",
        26: "Nicola", 28: "Eva + Eve + Carla & the Men", 33: "Catherine", 34: "Anna-Maria", 38: "Die Buddenbergs",
        47: "K-Ro", 49: "Verena", 50: "Mami & Papi", 53: "Katja, Christian, Julia & Alexander",
        54: "Suse", 55: "Viersen Brüses", 58: "Andrea & Geo", 59: "Nina",
        61: "Séchés & Kleins", 63: "Claudi", 65: "Lisa & Stefan", 66: "Katrin & Tim", 67: "Steffi & Hendrik", 69: "Conor & Nicky", 70: "Britta, Thorben & Charlotte", 73: "Sim", 74: "Kat & the Pearsons", 75: "Annie & John", 76: "Kerry", 77: "Camilla & Nic", 79: "Henrike & Masoud", 80: "Cheree"}
SKIP = {1}  # Export 17.11.: alter Beitrag 66 (Fotos Lisa & Stefan) gelöscht, Fotos liegen bei 65; 66 = Katrin & Tim
CITY = {2: "Gerresheim", 12: "Viersen", 13: "Viersen", 14: "Olching", 15: "Olching", 22: "Hamburg",
        24: "Oberkassel", 26: "Oberkassel", 27: "Oberkassel", 32: "Munich · Christchurch", 34: "Düsseldorf",
        8: "Cologne", 9: "Cologne", 37: "Hamburg", 31: "Düsseldorf", 29: "Düsseldorf", 6: "Düsseldorf",
        55: "Viersen", 50: "Krefeld", 53: "Krefeld", 45: "Düsseldorf", 60: "Düsseldorf",
        63: "Christchurch", 65: "Bonn"}


# Orte (Dirk 21.11.)
CITY.update({81: "Hamburg", 47: "Munich", 49: "Bonn", 54: "Stuttgart", 25: "Neuss", 31: "Meerbusch", 18: "Meerbusch", 52: "Düsseldorf", 62: "Benrath",
             44: "Düsseldorf", 67: "Düsseldorf", 68: "Meerbusch", 28: "Düsseldorf", 24: "Düsseldorf", 26: "Düsseldorf", 29: "Düsseldorf",
             64: "Düsseldorf", 19: "Düsseldorf", 59: "Düsseldorf", 51: "Düsseldorf", 42: "Düsseldorf", 43: "Düsseldorf", 38: "Düsseldorf",
             39: "Düsseldorf", 61: "Düsseldorf", 58: "Düsseldorf", 4: "Düsseldorf", 7: "Düsseldorf", 5: "Düsseldorf", 48: "Euskirchen",
             57: "Hamburg", 46: "Bonn", 66: "Meerbusch", 56: "Meerbusch", 70: "Meerbusch"})

csv_path, photos_path, media = sys.argv[1:4]
photos = json.load(open(photos_path))
dur = lambda f: os.path.exists(f) and float(os.popen(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"').read() or 0)
mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
out = []
for r in csv.DictReader(open(csv_path, encoding="utf-8-sig")):
    n = int(r["Post number"])
    if n in SKIP: continue
    clean = lambda k: r[k].strip()
    p = {"n": n, "name": NAME.get(n) or clean("Your (Nick-) Name:") or clean("Author"),
         "group": GROUP.get(n, "new")}
    for key, col in [("title", "Subject"), ("note", "Body"), ("isFor", "Nici is for me..."),
                     ("moment", "My special moment with her..."), ("wish", "I wish Nici...")]:
        if clean(col): p[key] = clean(col)
    if p.get("title") == p.get("note"): p.pop("title")
    if n == 5: p.pop("note", None)
    if n in CITY: p["city"] = CITY[n]
    elif p["group"] == "aus": p["city"] = "Gold Coast"
    if n in TEAM: p["team"] = TEAM[n]
    if str(n) in photos: p["imgs"] = photos[str(n)]
    v, a = f"{media}/v{n}.mp4", f"{media}/a{n}.mp3"
    if os.path.exists(v): p["clip"] = f"v{n}"; p["video"] = mmss(dur(v))
    if os.path.exists(a): p["audio"] = f"a{n}"; p["voice"] = mmss(dur(a))
    out.append(p)
# Beitrag außerhalb des Padlets (Dirk 21.11.): Claire, Hockey, Text vom Foto abgeschrieben
out.append({"n": 901, "name": "Claire", "group": "aus", "city": "Gold Coast", "team": "Hockey", "title": "Ode to Nicola",
            "note": open("tools/letter-claire.txt", encoding="utf-8").read().strip()})
# Beiträge zusammenlegen: Quelle -> Ziel (Texte angehängt, Fotos/Medien übernommen)
# KEEP_TEXT: Ziel behält nur seine eigenen Texte (Dirk 17.11.)
MERGE = {20: 18, 15: 14, 33: 22, 27: 24, 78: 37, 82: 81}  # 78: Video von Elisa & Sylvie zu Sylvie (Dirk 21.11.)
KEEP_TEXT = {15, 33, 27, 78}
byn = {p["n"]: p for p in out}
for src, dst in MERGE.items():
    a, b = byn.get(src), byn.get(dst)
    if not a or not b: continue
    for k in ("note", "isFor", "moment", "wish"):
        if src in KEEP_TEXT: break
        if a.get(k) and a[k] != b.get(k): b[k] = (b[k] + ("\n\n" if k == "note" else " · ") + a[k]) if b.get(k) else a[k]
    for k in ("imgs", "clip", "video", "audio", "voice", "city", "title"):
        if a.get(k) and not b.get(k): b[k] = a[k]
    out.remove(a)
# Nach dem Zusammenlegen (Dirk 17.11.): DEHNS-Videos 24+27 hintereinander geschnitten
FIX = {14: {"name": "Ena & Esa"}, 24: {"title": "From OBK to Down Under", "clip": "v-dehns", "video": mmss(dur(f"{media}/v-dehns.mp4"))}, 59: {"name": "Nina & Lars"}, 70: {"title": "Mit Hecheln fing es an – für Nicola"}, 80: {"note": open("tools/letter-80.txt", encoding="utf-8").read().strip()}}
for n, f in FIX.items():
    if n in byn: byn[n].update(f)
# Startbild (Dirk 21.11.): bei Nicole das 6. Foto zuerst
for n, k in {68: 6}.items():
    if n in byn and len(byn[n].get("imgs", [])) >= k: im = byn[n]["imgs"]; im.insert(0, im.pop(k - 1))
# Eigene Beiträge außerhalb des Padlets (Dirk 17.11.: Strandvideo als letzter Family-Beitrag, danach nur die Herz-Karte)
# Dirks eigener Beitrag liegt seit 21.11. auf der geschützten Herz-Seite hinter dem Brief
EXTRA = [{"n": "outtakes", "name": "Moritz, Philip & Dirk", "group": "family", "after": True, "city": "Gold Coast", "title": "Outtakes: Happy Birthday, Mama! (Take 1 to 8)", "clip": "v-outtakes", "video": "0:44"}]
BEFORE = {}
key = lambda n: ORDER.index(n) if n in ORDER else 1000 + LAST.index(n) if n in LAST else 100 + n
out.sort(key=lambda p: key(BEFORE[p["n"]]) - 0.5 if p["n"] in BEFORE else key(p["n"]))
last_fam = max(i for i, p in enumerate(out) if p.get("group") == "family")
out = out[:last_fam + 1] + EXTRA + out[last_fam + 1:]
open("posts.js", "w").write("// Erzeugt mit tools/build_posts.py aus dem Padlet-Export\nconst friends = " +
                            json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(out), "Beiträge")
