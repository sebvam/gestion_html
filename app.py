
import os, sys, configparser, webview, xml.etree.ElementTree as ET
import shutil
from tkinter import filedialog, Tk

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
INI_PATH = os.path.join(CONFIG_DIR, "config.ini")
INDEX_HTML = os.path.join(TEMPLATES_DIR, "index.html")

def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(INI_PATH):
        cfg = configparser.ConfigParser()
        cfg['window'] = {'title': 'Sistema de Gestión', 'width': '1024', 'height': '768', 'start_page': 'templates/index.html'}
        cfg['preferences'] = {'theme': 'light', 'font_size': 'normal'}
        with open(INI_PATH, 'w', encoding='utf-8') as f:
            cfg.write(f)

def read_prefs():
    cfg = configparser.ConfigParser()
    cfg.read(INI_PATH, encoding='utf-8')
    theme = cfg.get('preferences', 'theme', fallback='light')
    font = cfg.get('preferences', 'font_size', fallback='normal')
    return {'theme': theme, 'font_size': font}

def write_prefs(theme, font_size):
    cfg = configparser.ConfigParser()
    if os.path.exists(INI_PATH):
        cfg.read(INI_PATH, encoding='utf-8')
    if 'preferences' not in cfg:
        cfg['preferences'] = {}
    cfg['preferences']['theme'] = theme
    cfg['preferences']['font_size'] = font_size
    with open(INI_PATH, 'w', encoding='utf-8') as f:
        cfg.write(f)

class Api:
    def upload_file(self):
        root = Tk(); root.withdraw()
        path = filedialog.askopenfilename(title="Seleccionar archivo HTML", filetypes=[("HTML files", "*.html")])
        if not path:
            root.destroy(); return "cancelled"
        dest = os.path.join(TEMPLATES_DIR, os.path.basename(path))
        try:
            shutil.copy2(path, dest)
            root.destroy()
            return "ok"
        except Exception as e:
            root.destroy()
            return {"error": str(e)}

    def delete_file(self, name):
        path = os.path.join(TEMPLATES_DIR, name)
        if os.path.exists(path) and name != 'index.html':
            try:
                os.remove(path)
                return "ok"
            except Exception as e:
                return {"error": str(e)}
        return "noexist"

    def list_files(self):
        try:
            files = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.html') and f != 'index.html']
            files.sort(key=lambda s: s.lower())
            return files
        except Exception as e:
            return []

    def abrir_archivo(self, nombre):
        path = os.path.join(TEMPLATES_DIR, nombre)
        if os.path.exists(path):
            window = webview.windows[0]
            window.load_url('file:///' + os.path.abspath(path).replace('\\\\','/'))
            return "ok"
        return "noexist"

    def refresh(self):
        window = webview.windows[0]
        window.load_url('file:///' + os.path.abspath(INDEX_HTML).replace('\\\\','/'))
        return "ok"

    def get_prefs(self):
        return read_prefs()

    def set_prefs(self, theme, font_size):
        write_prefs(theme, font_size)
        return "ok"

    # convenience for HTML: guardar tema (kept for compatibility)
    def guardar_tema(self, tema):
        prefs = read_prefs()
        write_prefs(tema, prefs.get('font_size', 'normal'))
        return "ok"

def main():
    ensure_config()
    cfg = configparser.ConfigParser()
    cfg.read(INI_PATH, encoding='utf-8')
    title = cfg.get('window','title', fallback='Sistema de Gestión')
    width = cfg.getint('window','width', fallback=1024)
    height = cfg.getint('window','height', fallback=768)
    start_page = cfg.get('window','start_page', fallback=INDEX_HTML)
    if not os.path.isabs(start_page):
        start_page = os.path.join(BASE_DIR, start_page)

    api = Api()
    start_url = 'file:///' + os.path.abspath(start_page).replace('\\\\','/')
    window = webview.create_window(title, start_url, width=width, height=height, js_api=api)
    webview.start()

if __name__ == '__main__':
    main()
