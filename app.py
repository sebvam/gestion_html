import os
import sys
import configparser
import webview
import shutil
import json
import traceback
from tkinter import filedialog, Tk

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
INI_PATH = os.path.join(CONFIG_DIR, "config.ini")
FILES_JSON = os.path.join(CONFIG_DIR, "files.json")
INDEX_HTML = os.path.join(TEMPLATES_DIR, "index.html")

# ---------------------------
# Util: asegurar directorios y archivos
# ---------------------------
def ensure_dirs_and_files():
    try:
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # default config.ini
        if not os.path.exists(INI_PATH):
            cfg = configparser.ConfigParser()
            cfg['window'] = {
                'title': 'Sistema de Gestión',
                'width': '1024',
                'height': '768',
                'start_page': 'templates/index.html'
            }
            cfg['preferences'] = {
                'theme': 'light',
                'font_size': 'normal',
                'zoom': '1.0'
            }
            with open(INI_PATH, 'w', encoding='utf-8') as f:
                cfg.write(f)
            print(f"[init] Creado: {INI_PATH}")
        # files.json
        if not os.path.exists(FILES_JSON):
            with open(FILES_JSON, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print(f"[init] Creado: {FILES_JSON}")
        # index.html placeholder si falta (para evitar crash)
        if not os.path.exists(INDEX_HTML):
            with open(INDEX_HTML, 'w', encoding='utf-8') as f:
                f.write("<!doctype html><html><body><h2>index.html no encontrado</h2></body></html>")
            print(f"[init] Creado placeholder: {INDEX_HTML}")
    except Exception as e:
        print("[ERROR] al crear dirs/archivos:", e)
        traceback.print_exc()

# ---------------------------
# Manejo persistente de la lista
# ---------------------------
def load_file_list():
    try:
        with open(FILES_JSON, 'r', encoding='utf-8') as f:
            arr = json.load(f)
        # filtrar entradas que no existen (para evitar huérfanos)
        filtered = [x for x in arr if os.path.exists(os.path.join(TEMPLATES_DIR, x))]
        if len(filtered) != len(arr):
            save_file_list(filtered)
        filtered.sort(key=lambda s: s.lower())
        return filtered
    except Exception as e:
        print("[ERROR] load_file_list:", e)
        traceback.print_exc()
        return []

def save_file_list(arr):
    try:
        with open(FILES_JSON, 'w', encoding='utf-8') as f:
            json.dump(arr, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[ERROR] save_file_list:", e)
        traceback.print_exc()

# ---------------------------
# API expuesta a la UI
# ---------------------------
class Api:
    def __init__(self):
        self._tk = None

    def _ensure_tk(self):
        if self._tk is None:
            self._tk = Tk()
            self._tk.withdraw()
            try:
                self._tk.wm_attributes("-topmost", 1)
            except Exception:
                pass

    def list_files(self):
        try:
            files = load_file_list()
            print(f"[api] list_files -> {files}")
            return files
        except Exception as e:
            print("[ERROR] api.list_files:", e)
            traceback.print_exc()
            return []

    def abrir_archivo(self, nombre):
        try:
            path = os.path.join(TEMPLATES_DIR, nombre)
            if os.path.exists(path):
                uri = 'file:///' + os.path.abspath(path).replace('\\', '/')
                print(f"[api] abrir_archivo -> {uri}")
                return uri
            print(f"[api] abrir_archivo: no existe {path}")
            return None
        except Exception as e:
            print("[ERROR] api.abrir_archivo:", e)
            traceback.print_exc()
            return None

    def upload_file(self):
        try:
            self._ensure_tk()
            path = filedialog.askopenfilename(title="Seleccionar archivo HTML", filetypes=[("HTML files", "*.html")])
            if not path:
                print("[api] upload_file: cancelled")
                return "cancelled"
            src = path
            dest_name = os.path.basename(src)
            dest = os.path.join(TEMPLATES_DIR, dest_name)

            # si existe, añadir sufijo incremental
            if os.path.exists(dest):
                base, ext = os.path.splitext(dest)
                i = 1
                while True:
                    candidate = f"{base}_{i}{ext}"
                    if not os.path.exists(candidate):
                        dest = candidate
                        dest_name = os.path.basename(dest)
                        break
                    i += 1

            shutil.copy2(src, dest)
            print(f"[api] upload_file: copiado {src} -> {dest}")

            # actualizar files.json
            files = load_file_list()
            if dest_name not in files:
                files.append(dest_name)
                save_file_list(files)
                print(f"[api] upload_file: guardado en files.json -> {dest_name}")
            else:
                print(f"[api] upload_file: ya existía en files.json -> {dest_name}")

            return "ok"
        except Exception as e:
            print("[ERROR] api.upload_file:", e)
            traceback.print_exc()
            return {"error": str(e)}
        finally:
            try:
                if self._tk:
                    self._tk.destroy()
                    self._tk = None
            except Exception:
                pass

    def delete_file(self, name):
        try:
            files = load_file_list()
            if name in files:
                files = [f for f in files if f != name]
                save_file_list(files)
                print(f"[api] delete_file: removido de files.json -> {name} (archivo físico NO borrado)")
                return "ok"
            else:
                print(f"[api] delete_file: no estaba en files.json -> {name}")
                return "noexist"
        except Exception as e:
            print("[ERROR] api.delete_file:", e)
            traceback.print_exc()
            return {"error": str(e)}

    def refresh(self):
        try:
            window = webview.windows[0]
            window.load_url('file:///' + os.path.abspath(INDEX_HTML).replace('\\', '/'))
            return "ok"
        except Exception as e:
            print("[ERROR] api.refresh:", e)
            traceback.print_exc()
            return {"error": str(e)}

    # --------------------------
    # Preferencias: theme y zoom
    # --------------------------
    def get_prefs(self):
        try:
            cfg = configparser.ConfigParser()
            cfg.read(INI_PATH, encoding='utf-8')
            theme = cfg.get('preferences', 'theme', fallback='light')
            zoom = cfg.get('preferences', 'zoom', fallback='1.0')
            print(f"[api] get_prefs -> theme={theme}, zoom={zoom}")
            return {"theme": theme, "zoom": zoom}
        except Exception as e:
            print("[ERROR] api.get_prefs:", e)
            traceback.print_exc()
            return {"theme": "light", "zoom": "1.0"}

    def set_prefs(self, theme, zoom):
        try:
            cfg = configparser.ConfigParser()
            if os.path.exists(INI_PATH):
                cfg.read(INI_PATH, encoding='utf-8')
            if 'preferences' not in cfg:
                cfg['preferences'] = {}
            cfg['preferences']['theme'] = theme
            cfg['preferences']['zoom'] = str(zoom)
            with open(INI_PATH, 'w', encoding='utf-8') as f:
                cfg.write(f)
            print(f"[api] set_prefs saved -> theme={theme}, zoom={zoom}")
            return "ok"
        except Exception as e:
            print("[ERROR] api.set_prefs:", e)
            traceback.print_exc()
            return {"error": str(e)}

# ---------------------------
# Inicio app
# ---------------------------
def main():
    ensure_dirs_and_files()

    cfg = configparser.ConfigParser()
    cfg.read(INI_PATH, encoding='utf-8')
    title = cfg.get('window', 'title', fallback='Sistema de Gestión')
    width = cfg.getint('window', 'width', fallback=1024)
    height = cfg.getint('window', 'height', fallback=768)
    start_page = cfg.get('window', 'start_page', fallback=INDEX_HTML)
    if not os.path.isabs(start_page):
        start_page = os.path.join(BASE_DIR, start_page)

    api = Api()
    start_url = 'file:///' + os.path.abspath(start_page).replace('\\', '/')
    print(f"[main] start_url={start_url}")
    window = webview.create_window(title, start_url, width=width, height=height, js_api=api)
    webview.start()

if __name__ == '__main__':
    main()
