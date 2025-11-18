import json
import base64
import os
import mimetypes
import tempfile
import shutil

JSON_FILE = "quizdatabase.json"
PWD = os.getcwd()

# Debug iniziale
print(f"PWD: {PWD}")
print(f"JSON target: {os.path.join(PWD, JSON_FILE)}")

# 1) Carica il JSON
if not os.path.exists(JSON_FILE):
    print(f"❌ JSON non trovato: {JSON_FILE}")
    raise SystemExit(1)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
        print("✔ JSON caricato")
    except Exception as e:
        print(f"❌ Errore nel parsing JSON: {e}")
        raise

# 2) Utility: conversione immagine → data URI
def img_to_data_uri(path):
    with open(path, "rb") as img_f:
        b64 = base64.b64encode(img_f.read()).decode("utf-8")
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        # fallback ragionevole
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"

# 3) Normalizza percorso relativo a $PWD rimuovendo lo slash iniziale
def normalize_web_path(p):
    if not isinstance(p, str):
        return None
    p = p.strip()
    if p.startswith("/"):
        p = p[1:]
    return os.path.join(PWD, p)

# 4) Visita ricorsiva della struttura JSON e converte i campi "img"
converted_count = 0
missing_count = 0

def process_node(node, idx_path=""):
    global converted_count, missing_count

    if isinstance(node, dict):
        # Se c'è un campo "img", prova a convertirlo
        if "img" in node and isinstance(node["img"], str):
            raw_path = node["img"]
            fs_path = normalize_web_path(raw_path)
            print(f"{idx_path} IMG: {raw_path} → {fs_path}")
            if fs_path and os.path.exists(fs_path):
                print(f"{idx_path}   ✔ trovato, converto…")
                try:
                    node["img"] = img_to_data_uri(fs_path)
                    converted_count += 1
                except Exception as e:
                    print(f"{idx_path}   ❌ errore conversione: {e}")
            else:
                print(f"{idx_path}   ⚠️ NON TROVATO: {fs_path}")
                missing_count += 1

        # Continua la visita per altri campi
        for k, v in node.items():
            process_node(v, idx_path=f"{idx_path}.{k}" if idx_path else k)

    elif isinstance(node, list):
        for i, item in enumerate(node):
            process_node(item, idx_path=f"{idx_path}[{i}]")

    else:
        # valori semplici: niente da fare
        return

# Esegui la conversione
process_node(data)

print(f"▶ Conversioni effettuate: {converted_count}")
print(f"▶ Immagini mancanti: {missing_count}")

# 5) Backup e scrittura atomica
backup_file = JSON_FILE + ".bak"
tmp_fd, tmp_path = tempfile.mkstemp(prefix="json_tmp_", suffix=".json", dir=PWD)
os.close(tmp_fd)  # useremo open con encoding

try:
    # Backup
    shutil.copy2(JSON_FILE, backup_file)
    print(f"✔ Backup creato: {backup_file}")

    # Scrivi su file temporaneo
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    print(f"✔ JSON scritto su temp: {tmp_path}")

    # Rimpiazza in modo atomico
    os.replace(tmp_path, JSON_FILE)
    print(f"✅ Sostituzione atomica completata: {JSON_FILE}")

except Exception as e:
    print(f"❌ Errore in scrittura/sostituzione: {e}")
    # se qualcosa va storto, lascia il backup intatto
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    raise


# import json
# import base64
# import os
# import mimetypes
# import tempfile
# import shutil
#
# JSON_FILE = "quizdatabase.json"
# PWD = os.getcwd()
#
# # Debug iniziale
# print(f"PWD: {PWD}")
# print(f"JSON target: {os.path.join(PWD, JSON_FILE)}")
#
# # 1) Carica il JSON
# if not os.path.exists(JSON_FILE):
#     print(f"❌ JSON non trovato: {JSON_FILE}")
#     raise SystemExit(1)
#
# with open(JSON_FILE, "r", encoding="utf-8") as f:
#     try:
#         data = json.load(f)
#         print("✔ JSON caricato")
#     except Exception as e:
#         print(f"❌ Errore nel parsing JSON: {e}")
#         raise
#
# # 2) Utility: conversione immagine → data URI
# def img_to_data_uri(path):
#     with open(path, "rb") as img_f:
#         b64 = base64.b64encode(img_f.read()).decode("utf-8")
#     mime, _ = mimetypes.guess_type(path)
#     if mime is None:
#         # fallback ragionevole
#         ext = os.path.splitext(path)[1].lower()
#         mime = "image/png" if ext == ".png" else "image/jpeg"
#     return f"data:{mime};base64,{b64}"
#
# # 3) Normalizza percorso relativo a $PWD rimuovendo lo slash iniziale
# def normalize_web_path(p):
#     if not isinstance(p, str):
#         return None
#     p = p.strip()
#     if p.startswith("/"):
#         p = p[1:]
#     return os.path.join(PWD, p)
#
# # 4) Visita ricorsiva della struttura JSON e converte i campi "img"
# converted_count = 0
# missing_count = 0
#
# def process_node(node, idx_path=""):
#     global converted_count, missing_count
#
#     if isinstance(node, dict):
#         # Se c'è un campo "img", prova a convertirlo
#         if "img" in node and isinstance(node["img"], str):
#             raw_path = node["img"]
#             fs_path = normalize_web_path(raw_path)
#             print(f"{idx_path} IMG: {raw_path} → {fs_path}")
#             if fs_path and os.path.exists(fs_path):
#                 print(f"{idx_path}   ✔ trovato, converto…")
#                 try:
#                     node["img"] = img_to_data_uri(fs_path)
#                     converted_count += 1
#                 except Exception as e:
#                     print(f"{idx_path}   ❌ errore conversione: {e}")
#             else:
#                 print(f"{idx_path}   ⚠️ NON TROVATO: {fs_path}")
#                 missing_count += 1
#
#         # Continua la visita per altri campi
#         for k, v in node.items():
#             process_node(v, idx_path=f"{idx_path}.{k}" if idx_path else k)
#
#     elif isinstance(node, list):
#         for i, item in enumerate(node):
#             process_node(item, idx_path=f"{idx_path}[{i}]")
#
#     else:
#         # valori semplici: niente da fare
#         return
#
# # Esegui la conversione
# process_node(data)
#
# print(f"▶ Conversioni effettuate: {converted_count}")
# print(f"▶ Immagini mancanti: {missing_count}")
#
# # 5) Backup e scrittura atomica
# backup_file = JSON_FILE + ".bak"
# tmp_fd, tmp_path = tempfile.mkstemp(prefix="json_tmp_", suffix=".json", dir=PWD)
# os.close(tmp_fd)  # useremo open con encoding
#
# try:
#     # Backup
#     shutil.copy2(JSON_FILE, backup_file)
#     print(f"✔ Backup creato: {backup_file}")
#
#     # Scrivi su file temporaneo
#     with open(tmp_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#         f.flush()
#         os.fsync(f.fileno())
#     print(f"✔ JSON scritto su temp: {tmp_path}")
#
#     # Rimpiazza in modo atomico
#     os.replace(tmp_path, JSON_FILE)
#     print(f"✅ Sostituzione atomica completata: {JSON_FILE}")
#
# except Exception as e:
#     print(f"❌ Errore in scrittura/sostituzione: {e}")
#     # se qualcosa va storto, lascia il backup intatto
#     if os.path.exists(tmp_path):
#         os.remove(tmp_path)
#     raise
