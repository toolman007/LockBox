import customtkinter as ctk
import sqlite3
import os
import csv
import json
import sys
import shutil
import threading
import ctypes  # 核心库：用于调用 Windows API
from cryptography.fernet import Fernet
import pyperclip
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
import pystray

# ================= 🌍 国际化资源 (i18n) =================
DEFAULT_LANG = "CN"

TRANSLATIONS = {
    "CN": {
        "app_title": "LOCKBOX",
        "version_text": "v6.4 HD Stable",
        "btn_new_file": "新建记录...",
        "btn_new_memo": "新建便签...",
        "label_explorer": "资源管理器",
        "nav_cred": "> 密码库",
        "nav_memo": "> 便签本",
        "btn_manage": "⚙ 设置",
        "btn_exit": "➜ 退出",
        "title_pwd_view": "🔐 密码保险箱",
        "title_memo_view": "📝 私密备忘录",
        "search_placeholder": "搜索...",
        "btn_go": "搜索",
        "header_name": "名称",
        "header_user": "账号/预览",
        "header_tags": "标签",
        "header_hits": "热度",
        "header_action": "操作",
        "btn_copy": "复制",
        "btn_del": "删除",
        "menu_edit_tags": "修改标签",
        "menu_delete": "删除记录",
        "placeholder_no_tags": "--",
        "title_new_cred": "新增账号",
        "title_new_memo": "新增便签",
        "ph_site": "平台名称 (如: Github)",
        "ph_user": "用户名 / 账号",
        "ph_pwd": "密码",
        "ph_tags": "标签 (回车添加)",
        "ph_memo_title": "标题 (如: Wifi密码)",
        "label_tags_manage": "标签管理",
        "label_tags_hint": "添加新标签或移除现有标签:",
        "btn_save": "保存",
        "btn_update": "更新",
        "btn_cancel": "取消",
        "title_settings": "设置",
        "group_appearance": "外观 / Theme",
        "group_language": "语言 / Language",
        "group_path": "存储路径 / Storage",
        "btn_change_path": "更改目录...",
        "group_data": "数据管理 / Data",
        "btn_export": "导出 CSV",
        "btn_import": "导入 CSV",
        "warn_export": "* 导出文件包含明文密码，请妥善保管！",
        "msg_restart_lang": "语言已切换。\n请重启软件以生效。",
        "toast_copied": "已复制",
        "toast_saved": "已保存",
        "toast_updated": "已更新",
        "toast_import_ok": "导入完成",
        "msg_confirm_del": "确定要删除这条记录吗？",
        "msg_confirm_migrate": "是否将旧数据迁移到新目录？\n\n(选择'否'将在新目录开始全新的空白库)",
        "msg_path_changed": "存储路径已更新。\n程序将关闭，请重新启动。",
        "err_fields": "所有字段不能为空",
        "report_import": "导入报告:\n\n✅ 成功添加: {}\n⏭️ 跳过重复: {}",
        "first_run_title": "初始化设置",
        "first_run_msg": "欢迎使用 LockBox！\n\n这是您第一次运行，请选择一个文件夹用于存放加密数据。\n建议选择非系统盘（如 D盘）。"
    },
    "EN": {
        "app_title": "LOCKBOX",
        "version_text": "v6.4 HD Stable",
        "btn_new_file": "New File...",
        "btn_new_memo": "New Memo...",
        "label_explorer": "EXPLORER",
        "nav_cred": "> Credentials",
        "nav_memo": "> Memos",
        "btn_manage": "⚙ Manage",
        "btn_exit": "➜ Exit",
        "title_pwd_view": "🔐 Password Vault",
        "title_memo_view": "📝 Secure Memos",
        "path_pwd": "src > main > passwords",
        "path_memo": "src > main > memos",
        "search_placeholder": "Search...",
        "btn_go": "Go",
        "header_name": "NAME",
        "header_user": "USER/PREVIEW",
        "header_tags": "TAGS",
        "header_hits": "HITS",
        "header_action": "ACTION",
        "btn_copy": "Copy",
        "btn_del": "Del",
        "menu_edit_tags": "Edit Tags",
        "menu_delete": "Delete",
        "placeholder_no_tags": "--",
        "title_new_cred": "New Credential",
        "title_new_memo": "New Memo",
        "ph_site": "Platform (e.g. Github)",
        "ph_user": "Username",
        "ph_pwd": "Password",
        "ph_tags": "Tags (Enter to add)",
        "ph_memo_title": "Title (e.g. Wifi)",
        "label_tags_manage": "Manage Tags",
        "label_tags_hint": "Add new or remove existing tags:",
        "btn_save": "Save",
        "btn_update": "Update",
        "btn_cancel": "Cancel",
        "title_settings": "Settings",
        "group_appearance": "Appearance",
        "group_language": "Language",
        "group_path": "Storage Location",
        "btn_change_path": "Change Folder...",
        "group_data": "Data Management",
        "btn_export": "Export CSV",
        "btn_import": "Import CSV",
        "warn_export": "* Export includes raw passwords!",
        "msg_restart_lang": "Language changed.\nPlease restart application.",
        "toast_copied": "Copied",
        "toast_saved": "Saved",
        "toast_updated": "Updated",
        "toast_import_ok": "Import Finished",
        "msg_confirm_del": "Delete this record?",
        "msg_confirm_migrate": "Migrate existing data to new folder?\n\n(Select 'No' to start fresh)",
        "msg_path_changed": "Path updated.\nApp will close. Please restart.",
        "err_fields": "Fields cannot be empty",
        "report_import": "Import Report:\n\n✅ Added: {}\n⏭️ Skipped: {}",
        "first_run_title": "First Run Setup",
        "first_run_msg": "Welcome to LockBox!\n\nPlease select a folder to store your secure data."
    }
}

T = TRANSLATIONS[DEFAULT_LANG]

# ================= 🎨 调色板 =================
COLOR_SIDEBAR_BG = ("#2B2D31", "#181818")
COLOR_SIDEBAR_TEXT = ("#FFFFFF", "#FFFFFF")
COLOR_MAIN_BG = ("#FFFFFF", "#1E1E1E")
COLOR_HEADER_TEXT = ("#374151", "#CCCCCC")
COLOR_CARD_BG = ("#F8F9FA", "#252526")
COLOR_CARD_BORDER = ("#E5E7EB", "#2D2D2D")
COLOR_STATUS_BAR = "#007ACC"
COLOR_PRIMARY = "#007ACC"
COLOR_TAG_CHIP = ("#E2E8F0", "#37373D")
COLOR_BTN_HOVER = ("#D1D5DB", "#333333")
COLOR_TITLE_TEXT = ("#1F2937", "#FFFFFF")

# ================= 📏 对齐常量 =================
PAD_TEXT_X = 10
PAD_FRAME_X = 17


# ================= 核心工具：环境与路径 =================
class EnvManager:
    def __init__(self):
        self.config_filename = "lockbox_config.json"
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.app_dir, self.config_filename)
        self.data_dir = None
        self.db_path = None
        self.key_path = None

    def load_or_setup_paths(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.data_dir = config.get("data_dir")
            except:
                pass

        if not self.data_dir or not os.path.exists(self.data_dir):
            return self._prompt_for_setup()

        self._set_full_paths()
        return True

    def _prompt_for_setup(self):
        root = ctk.CTk()
        root.withdraw()
        messagebox.showinfo(T["first_run_title"], T["first_run_msg"])
        selected_dir = filedialog.askdirectory(title="Select Data Storage Folder")
        if not selected_dir:
            root.destroy()
            return False
        self.update_data_dir(selected_dir)
        root.destroy()
        return True

    def update_data_dir(self, new_dir):
        self.data_dir = new_dir
        self._set_full_paths()
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"data_dir": self.data_dir}, f)
        except Exception as e:
            print(f"Config Save Error: {e}")

    def _set_full_paths(self):
        self.db_path = os.path.join(self.data_dir, "local_passwords.db")
        self.key_path = os.path.join(self.data_dir, "secret.key")


ENV = EnvManager()


# ================= 核心工具 =================
def center_window(child, parent, width, height):
    parent.update_idletasks()
    x_parent = parent.winfo_x()
    y_parent = parent.winfo_y()
    w_parent = parent.winfo_width()
    h_parent = parent.winfo_height()
    x = x_parent + (w_parent // 2) - (width // 2)
    y = y_parent + (h_parent // 2) - (height // 2)
    child.geometry(f"{width}x{height}+{x}+{y}")


def create_app_icon():
    width = 64;
    height = 64
    color1 = "#007ACC";
    color2 = "white"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=color2)
    return image


class SelectableLabel(ctk.CTkEntry):
    def __init__(self, master, text, font=None, text_color=None, **kwargs):
        super().__init__(master, border_width=0, fg_color="transparent", **kwargs)
        if font: self.configure(font=font)
        if text_color: self.configure(text_color=text_color)
        self.insert(0, str(text))
        self.configure(state="readonly", cursor="arrow")


class TagInputWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.tags = []
        self.entry = ctk.CTkEntry(self, placeholder_text=T["ph_tags"], width=300)
        self.entry.pack(fill="x", pady=(0, 5))
        self.entry.bind("<Return>", self._add_tag_event)
        self.entry.bind("<comma>", self._add_tag_event_comma)
        self.tags_frame = ctk.CTkScrollableFrame(self, orientation="horizontal", height=40, fg_color="transparent")
        self.tags_frame.pack(fill="x")

    def _add_tag_event(self, event):
        text = self.entry.get().strip()
        if text: self.add_tag(text)
        self.entry.delete(0, 'end')

    def _add_tag_event_comma(self, event):
        self.after(10, self._add_tag_event, None)

    def add_tag(self, text):
        clean_text = text.replace("，", ",").split(",")
        for t in clean_text:
            t = t.strip()
            if t and t not in self.tags:
                self.tags.append(t)
                self._create_tag_chip(t)

    def _create_tag_chip(self, text):
        chip = ctk.CTkFrame(self.tags_frame, fg_color=COLOR_TAG_CHIP, corner_radius=5)
        chip.pack(side="left", padx=2, pady=2)
        lbl = ctk.CTkLabel(chip, text=text, font=("Consolas", 12))
        lbl.pack(side="left", padx=(8, 4), pady=2)
        btn_del = ctk.CTkButton(chip, text="×", width=15, height=15,
                                fg_color="transparent", hover_color="#ef4444", text_color="gray",
                                font=("Arial", 12, "bold"), command=lambda: self._remove_tag(chip, text))
        btn_del.pack(side="left", padx=(0, 4), pady=2)

    def _remove_tag(self, widget, text):
        if text in self.tags: self.tags.remove(text)
        widget.destroy()

    def get_tags_string(self):
        return ",".join(self.tags)


# ================= 后端逻辑 =================
class SecurityManager:
    def __init__(self):
        self.key_file = ENV.key_path
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
        return key

    def encrypt_password(self, password):
        return self.cipher.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        return self.cipher.decrypt(encrypted_password.encode()).decode()


class DatabaseManager:
    def __init__(self):
        self.db_file = ENV.db_path
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS credentials (id INTEGER PRIMARY KEY AUTOINCREMENT, site_name TEXT NOT NULL, username TEXT NOT NULL, encrypted_password TEXT NOT NULL, copy_count INTEGER DEFAULT 0, tags TEXT DEFAULT '')''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, copy_count INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)''')
        try:
            self.cursor.execute("SELECT copy_count FROM notes LIMIT 1")
        except sqlite3.OperationalError:
            try:
                self.cursor.execute("ALTER TABLE notes ADD COLUMN copy_count INTEGER DEFAULT 0")
                self.conn.commit()
            except:
                pass
        self.conn.commit()

    def add_credential(self, site, user, enc_pwd, tags=""):
        self.cursor.execute(
            'INSERT INTO credentials (site_name, username, encrypted_password, tags, copy_count) VALUES (?, ?, ?, ?, 0)',
            (site, user, enc_pwd, tags))
        self.conn.commit()

    def delete_credential(self, cred_id):
        self.cursor.execute('DELETE FROM credentials WHERE id = ?', (cred_id,))
        self.conn.commit()

    def update_tags(self, cred_id, new_tags):
        self.cursor.execute('UPDATE credentials SET tags = ? WHERE id = ?', (new_tags, cred_id))
        self.conn.commit()

    def increment_copy_count(self, cred_id):
        self.cursor.execute('UPDATE credentials SET copy_count = copy_count + 1 WHERE id = ?', (cred_id,))
        self.conn.commit()

    def get_credentials(self, search_query=""):
        if not search_query:
            sql = 'SELECT * FROM credentials ORDER BY copy_count DESC, id DESC'
        else:
            sql = 'SELECT * FROM credentials WHERE site_name LIKE ? OR username LIKE ? OR tags LIKE ? ORDER BY copy_count DESC, id DESC'
        params = (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%") if search_query else ()
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def credential_exists(self, site, user):
        self.cursor.execute('SELECT id FROM credentials WHERE site_name = ? AND username = ?', (site, user))
        return self.cursor.fetchone() is not None

    def add_note(self, title, content):
        self.cursor.execute('INSERT INTO notes (title, content, copy_count) VALUES (?, ?, 0)', (title, content))
        self.conn.commit()

    def delete_note(self, note_id):
        self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()

    def increment_note_copy(self, note_id):
        self.cursor.execute('UPDATE notes SET copy_count = copy_count + 1 WHERE id = ?', (note_id,))
        self.conn.commit()

    def get_notes(self, search_query=""):
        if not search_query:
            sql = 'SELECT * FROM notes ORDER BY copy_count DESC, id DESC'
        else:
            sql = 'SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY copy_count DESC, id DESC'
        params = (f"%{search_query}%", f"%{search_query}%") if search_query else ()
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def set_config(self, key, value):
        self.cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def get_config(self, key, default=None):
        self.cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def close(self):
        self.conn.close()


# ================= 弹窗们 =================
class AddRecordDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title(T["title_new_cred"])
        self.configure(fg_color=COLOR_MAIN_BG)
        center_window(self, parent, 420, 450)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text=T["title_new_cred"], font=("Microsoft YaHei", 18, "bold")).pack(pady=(20, 15))
        self.entry_site = ctk.CTkEntry(self, placeholder_text=T["ph_site"], width=320, height=35)
        self.entry_site.pack(pady=8)
        self.entry_user = ctk.CTkEntry(self, placeholder_text=T["ph_user"], width=320, height=35)
        self.entry_user.pack(pady=8)
        self.entry_pass = ctk.CTkEntry(self, placeholder_text=T["ph_pwd"], show="*", width=320, height=35)
        self.entry_pass.pack(pady=8)
        ctk.CTkLabel(self, text=T["ph_tags"], text_color="gray", font=("Arial", 12)).pack(pady=(10, 0), padx=50,
                                                                                          anchor="w")
        self.tag_widget = TagInputWidget(self, width=320)
        self.tag_widget.pack(pady=5, padx=50, fill="x")
        ctk.CTkButton(self, text=T["btn_save"], width=320, height=40, font=("Microsoft YaHei", 14, "bold"),
                      fg_color=COLOR_PRIMARY, command=self.on_save).pack(pady=20)

    def on_save(self):
        site, user, pwd = self.entry_site.get().strip(), self.entry_user.get().strip(), self.entry_pass.get().strip()
        if not site or not user or not pwd:
            messagebox.showwarning("Info", T["err_fields"])
            return
        self.callback(site, user, pwd, self.tag_widget.get_tags_string())
        self.destroy()


class AddNoteDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title(T["title_new_memo"])
        self.configure(fg_color=COLOR_MAIN_BG)
        center_window(self, parent, 420, 300)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text=T["title_new_memo"], font=("Microsoft YaHei", 18, "bold")).pack(pady=(20, 15))
        self.entry_title = ctk.CTkEntry(self, placeholder_text=T["ph_memo_title"], width=320, height=35)
        self.entry_title.pack(pady=8)
        self.entry_content = ctk.CTkTextbox(self, width=320, height=100, border_width=2)
        self.entry_content.pack(pady=8)
        ctk.CTkButton(self, text=T["btn_save"], width=320, height=40, font=("Microsoft YaHei", 14, "bold"),
                      fg_color=COLOR_PRIMARY, command=self.on_save).pack(pady=15)

    def on_save(self):
        title = self.entry_title.get().strip()
        content = self.entry_content.get("1.0", "end").strip()
        if not title or not content:
            messagebox.showwarning("Info", T["err_fields"])
            return
        self.callback(title, content)
        self.destroy()


class EditTagsDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_tags, callback):
        super().__init__(parent)
        self.callback = callback
        self.title(T["menu_edit_tags"])
        self.configure(fg_color=COLOR_MAIN_BG)
        center_window(self, parent, 400, 350)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text=T["label_tags_manage"], font=("Microsoft YaHei", 16, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self, text=T["label_tags_hint"], text_color="gray", font=("Arial", 12)).pack(pady=(0, 10))
        self.tag_widget = TagInputWidget(self, width=320)
        self.tag_widget.pack(pady=5, padx=50, fill="x")
        if current_tags:
            for t in current_tags.split(","):
                if t.strip(): self.tag_widget.add_tag(t.strip())
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)
        ctk.CTkButton(btn_frame, text=T["btn_cancel"], width=100, fg_color="gray", command=self.destroy).pack(
            side="left", padx=10)
        ctk.CTkButton(btn_frame, text=T["btn_update"], width=100, fg_color=COLOR_PRIMARY, command=self.on_update).pack(
            side="left", padx=10)

    def on_update(self):
        self.callback(self.tag_widget.get_tags_string())
        self.destroy()


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_theme, current_lang, theme_cb, lang_cb, export_cb, import_cb, change_path_cb):
        super().__init__(parent)
        self.theme_cb = theme_cb
        self.lang_cb = lang_cb
        self.export_cb = export_cb
        self.import_cb = import_cb
        self.change_path_cb = change_path_cb
        self.title(T["title_settings"])
        self.configure(fg_color=COLOR_MAIN_BG)
        center_window(self, parent, 320, 550)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text=T["group_appearance"], font=("Microsoft YaHei", 14, "bold")).pack(pady=(15, 5))
        self.seg_theme = ctk.CTkSegmentedButton(self, values=["System", "Light", "Dark"], command=self.change_theme,
                                                selected_color=COLOR_PRIMARY)
        self.seg_theme.pack(pady=5)
        self.seg_theme.set(current_theme)
        ctk.CTkLabel(self, text=T["group_language"], font=("Microsoft YaHei", 14, "bold")).pack(pady=(15, 5))
        self.seg_lang = ctk.CTkSegmentedButton(self, values=["CN", "EN"], command=self.change_lang,
                                               selected_color=COLOR_PRIMARY)
        self.seg_lang.pack(pady=5)
        self.seg_lang.set(current_lang)
        ctk.CTkLabel(self, text=T["group_path"], font=("Microsoft YaHei", 14, "bold")).pack(pady=(20, 5))
        self.entry_path = ctk.CTkEntry(self, width=280, text_color="gray")
        self.entry_path.pack(pady=5)
        self.entry_path.insert(0, ENV.data_dir)
        self.entry_path.configure(state="readonly")
        ctk.CTkButton(self, text=T["btn_change_path"], width=120, fg_color="gray", command=self.change_path).pack(
            pady=5)
        ctk.CTkLabel(self, text=T["group_data"], font=("Microsoft YaHei", 14, "bold")).pack(pady=(20, 5))
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text=T["btn_export"], width=120, fg_color="#10B981", command=self.export_data).pack(
            side="left", padx=5)
        ctk.CTkButton(btn_frame, text=T["btn_import"], width=120, fg_color="#F59E0B", command=self.import_data).pack(
            side="left", padx=5)
        ctk.CTkLabel(self, text=T["warn_export"], font=("Arial", 10), text_color="red").pack(pady=10)

    def change_theme(self, value): self.theme_cb(value)

    def change_lang(self, value): self.lang_cb(value)

    def change_path(self):
        self.destroy()
        self.change_path_cb()

    def export_data(self):
        self.destroy()
        self.export_cb()

    def import_data(self):
        self.destroy()
        self.import_cb()


# ================= UI 主界面 =================
class PasswordApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.security = SecurityManager()
        self.db = DatabaseManager()
        self.current_view = "passwords"
        self.toast_timer = None
        self.tray_icon = None

        self._load_app_config()

        self.title(T["app_title"])
        self.geometry("1100x700")
        self.minsize(1000, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._init_sidebar()
        self._init_main_content()
        self._init_status_bar()
        self._load_data()
        self._start_tray_thread()

    def _load_app_config(self):
        saved_theme = self.db.get_config("theme", "System")
        ctk.set_appearance_mode(saved_theme)
        self.current_theme = saved_theme

        global T
        saved_lang = self.db.get_config("language", DEFAULT_LANG)
        self.current_lang = saved_lang
        T = TRANSLATIONS.get(saved_lang, TRANSLATIONS[DEFAULT_LANG])

    def _init_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR_BG)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=T["app_title"], font=("Segoe UI", 26, "bold"),
                                       text_color=COLOR_SIDEBAR_TEXT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(35, 5), sticky="w")
        ctk.CTkLabel(self.sidebar_frame, text=T["version_text"], text_color="gray", font=("Consolas", 10)).grid(row=1,
                                                                                                                column=0,
                                                                                                                padx=22,
                                                                                                                sticky="w")
        self.btn_new = ctk.CTkButton(self.sidebar_frame, text=T["btn_new_file"], height=35, anchor="w",
                                     font=("Segoe UI", 13), fg_color=COLOR_PRIMARY, text_color="white",
                                     command=self.open_add_dialog)
        self.btn_new.grid(row=2, column=0, padx=20, pady=(40, 10), sticky="ew")
        self.btn_new_memo = ctk.CTkButton(self.sidebar_frame, text=T["btn_new_memo"], height=35, anchor="w",
                                          font=("Segoe UI", 13), fg_color="transparent", border_width=1,
                                          border_color="gray", text_color="white", hover_color=COLOR_BTN_HOVER,
                                          command=self.open_add_note_dialog)
        self.btn_new_memo.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(self.sidebar_frame, text=T["label_explorer"], anchor="w", font=("Segoe UI", 11, "bold"),
                     text_color="gray").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.btn_nav_pwd = ctk.CTkButton(self.sidebar_frame, text=T["nav_cred"], anchor="w", fg_color="transparent",
                                         text_color=COLOR_SIDEBAR_TEXT, hover_color=COLOR_BTN_HOVER,
                                         font=("Consolas", 12), command=lambda: self.switch_view("passwords"))
        self.btn_nav_pwd.grid(row=5, column=0, padx=10, pady=2, sticky="ew")
        self.btn_nav_memo = ctk.CTkButton(self.sidebar_frame, text=T["nav_memo"], anchor="w", fg_color="transparent",
                                          text_color=COLOR_SIDEBAR_TEXT, hover_color=COLOR_BTN_HOVER,
                                          font=("Consolas", 12), command=lambda: self.switch_view("memos"))
        self.btn_nav_memo.grid(row=6, column=0, padx=10, pady=2, sticky="n ew")
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.settings_frame.grid(row=7, column=0, sticky="ew", pady=(0, 20))
        self.btn_settings = ctk.CTkButton(self.settings_frame, text=T["btn_manage"], anchor="w", fg_color="transparent",
                                          hover_color="#333333", text_color=COLOR_SIDEBAR_TEXT,
                                          command=self.open_settings)
        self.btn_settings.pack(padx=10, fill="x")
        self.btn_quit = ctk.CTkButton(self.settings_frame, text=T["btn_exit"], anchor="w", fg_color="transparent",
                                      hover_color="#ef4444", text_color=COLOR_SIDEBAR_TEXT, command=self.quit_app)
        self.btn_quit.pack(padx=10, fill="x", pady=(5, 0))

    def _init_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_MAIN_BG)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=(15, 10))
        self.lbl_dashboard = ctk.CTkLabel(self.top_bar, text=T["title_pwd_view"], font=("Microsoft YaHei", 24, "bold"),
                                          text_color=COLOR_TITLE_TEXT)
        self.lbl_dashboard.pack(side="left")
        self.search_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.search_frame.pack(side="right")
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text=T["search_placeholder"], width=250,
                                         border_width=1, corner_radius=3)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<Return>", lambda e: self._load_data())
        ctk.CTkButton(self.search_frame, text=T["btn_go"], width=40, fg_color=COLOR_PRIMARY, corner_radius=3,
                      command=self._load_data).pack(side="left")
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.header_frame.pack(fill="x", padx=20, pady=(10, 0))
        self._configure_grid_columns(self.header_frame)
        self.headers = {}
        # 🚨 微调：全局字体稍微加大一点，解决“字变小了”的观感
        fonts = ("Segoe UI", 13, "bold")
        self.headers[0] = SelectableLabel(self.header_frame, text=T["header_name"], font=fonts,
                                          text_color=COLOR_HEADER_TEXT)
        self.headers[0].grid(row=0, column=0, sticky="ew", padx=PAD_TEXT_X)
        self.headers[1] = SelectableLabel(self.header_frame, text=T["header_user"], font=fonts,
                                          text_color=COLOR_HEADER_TEXT)
        self.headers[1].grid(row=0, column=1, sticky="ew", padx=PAD_TEXT_X)
        self.headers[2] = SelectableLabel(self.header_frame, text=T["header_tags"], font=fonts,
                                          text_color=COLOR_HEADER_TEXT)
        self.headers[2].grid(row=0, column=2, sticky="ew", padx=PAD_FRAME_X)
        self.headers[3] = SelectableLabel(self.header_frame, text=T["header_hits"], font=fonts,
                                          text_color=COLOR_HEADER_TEXT)
        self.headers[3].grid(row=0, column=3, sticky="ew", padx=PAD_TEXT_X)
        self.headers[4] = SelectableLabel(self.header_frame, text=T["header_action"], font=fonts,
                                          text_color=COLOR_HEADER_TEXT)
        self.headers[4].grid(row=0, column=4, sticky="ew", padx=PAD_FRAME_X)
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def _init_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color=COLOR_STATUS_BAR)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.lbl_status_l = ctk.CTkLabel(self.status_bar, text=" ⚡ Connected to Local DB ", font=("Segoe UI", 11),
                                         text_color="white")
        self.lbl_status_l.pack(side="left", padx=10)
        self.lbl_status_r = ctk.CTkLabel(self.status_bar, text="UTF-8  Ln 1, Col 1 ", font=("Segoe UI", 11),
                                         text_color="white")
        self.lbl_status_r.pack(side="right", padx=10)

    def _configure_grid_columns(self, frame):
        frame.grid_columnconfigure(0, weight=2, minsize=140)
        frame.grid_columnconfigure(1, weight=3, minsize=160)
        frame.grid_columnconfigure(2, weight=3, minsize=180)
        frame.grid_columnconfigure(3, weight=1, minsize=80)
        frame.grid_columnconfigure(4, weight=2, minsize=160)

    def switch_view(self, view_name):
        self.current_view = view_name
        title_text = T["title_pwd_view"] if view_name == "passwords" else T["title_memo_view"]
        self.lbl_dashboard.configure(text=title_text)
        if view_name == "passwords":
            self._update_header_text(0, T["header_name"])
            self._update_header_text(1, T["header_user"])
            self._update_header_text(2, T["header_tags"])
        else:
            self._update_header_text(0, "TITLE")
            self._update_header_text(1, "PREVIEW")
            self._update_header_text(2, " ")
        self._load_data()

    def _update_header_text(self, col_idx, new_text):
        widget = self.headers[col_idx]
        widget.configure(state="normal")
        widget.delete(0, 'end')
        widget.insert(0, new_text)
        widget.configure(state="readonly")

    def _load_data(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        search = self.entry_search.get().strip()
        if self.current_view == "passwords":
            rows = self.db.get_credentials(search)
            self.btn_nav_pwd.configure(text=f"{T['nav_cred']}: {len(rows)}", text_color="white")
            self.btn_nav_memo.configure(text=f"{T['nav_memo']}", text_color="gray")
            for row in rows: self._create_card_row(row)
        else:
            rows = self.db.get_notes(search)
            pwd_count = len(self.db.get_credentials())
            self.btn_nav_pwd.configure(text=f"{T['nav_cred']}: {pwd_count}", text_color="gray")
            self.btn_nav_memo.configure(text=f"{T['nav_memo']}: {len(rows)}", text_color="white")
            for row in rows: self._create_note_row(row)

    def _create_card_row(self, row):
        cid, site, user, enc_pwd, copy_count, tags = row
        card = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER,
                            corner_radius=6)
        card.pack(fill="x", pady=2, padx=10)
        self._configure_grid_columns(card)
        # 🚨 微调：内容字体也加大一点 (13px)
        SelectableLabel(card, text=site, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="ew",
                                                                             padx=PAD_TEXT_X, pady=12)
        SelectableLabel(card, text=user, font=("Consolas", 13)).grid(row=0, column=1, sticky="ew", padx=PAD_TEXT_X)
        tags_container = ctk.CTkFrame(card, fg_color="transparent")
        tags_container.grid(row=0, column=2, sticky="w", padx=PAD_FRAME_X)
        if tags:
            for t in tags.split(",")[:2]:
                if t: ctk.CTkLabel(tags_container, text=f" {t} ", fg_color=COLOR_TAG_CHIP, corner_radius=3,
                                   font=("Consolas", 11)).pack(side="left", padx=(0, 5))
        else:
            ctk.CTkLabel(tags_container, text=T["placeholder_no_tags"], text_color="gray", font=("Consolas", 11)).pack(
                side="left")
        fire_color = "#D19A66" if copy_count > 10 else "gray"
        SelectableLabel(card, text=f"🔥 {copy_count}", text_color=fire_color, font=("Consolas", 13)).grid(row=0,
                                                                                                         column=3,
                                                                                                         sticky="ew",
                                                                                                         padx=PAD_TEXT_X)
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=0, column=4, sticky="w", padx=PAD_FRAME_X)
        ctk.CTkButton(action_frame, text=T["btn_copy"], width=50, height=24, fg_color=COLOR_PRIMARY, corner_radius=2,
                      command=lambda: self.copy_password(cid, enc_pwd)).pack(side="left", padx=(0, 5))
        opt = ctk.CTkOptionMenu(action_frame, values=[T["menu_edit_tags"], T["menu_delete"]], width=20, height=24,
                                fg_color=COLOR_TAG_CHIP, text_color="gray", button_color=COLOR_TAG_CHIP,
                                command=lambda c, i=cid, t=tags: self.handle_action(c, i, t, opt))
        opt.set("•••")
        opt.pack(side="left")

    def _create_note_row(self, row):
        nid, title, content, copy_count = row
        card = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_CARD_BG, border_width=1, border_color=COLOR_CARD_BORDER,
                            corner_radius=6)
        card.pack(fill="x", pady=2, padx=10)
        self._configure_grid_columns(card)
        SelectableLabel(card, text=title, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="ew",
                                                                              padx=PAD_TEXT_X, pady=12)
        preview = content.replace("\n", " ")
        if len(preview) > 30: preview = preview[:30] + "..."
        SelectableLabel(card, text=preview, font=("Consolas", 13), text_color="gray").grid(row=0, column=1, sticky="ew",
                                                                                           padx=PAD_TEXT_X)
        ctk.CTkLabel(card, text=" ", font=("Consolas", 11)).grid(row=0, column=2, sticky="ew")
        fire_color = "#D19A66" if copy_count > 10 else "gray"
        SelectableLabel(card, text=f"🔥 {copy_count}", text_color=fire_color, font=("Consolas", 13)).grid(row=0,
                                                                                                         column=3,
                                                                                                         sticky="ew",
                                                                                                         padx=PAD_TEXT_X)
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=0, column=4, sticky="w", padx=PAD_FRAME_X)
        ctk.CTkButton(action_frame, text=T["btn_copy"], width=50, height=24, fg_color="#F59E0B", corner_radius=2,
                      command=lambda: self.copy_note(nid, content)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(action_frame, text=T["btn_del"], width=30, height=24, fg_color="#ef4444", corner_radius=2,
                      command=lambda: self.delete_note(nid)).pack(side="left")

    def copy_password(self, cid, enc_pwd):
        try:
            pyperclip.copy(self.security.decrypt_password(enc_pwd))
            self.db.increment_copy_count(cid)
            self._load_data()
            self.show_toast(T["toast_copied"])
        except:
            messagebox.showerror("Error", "Decrypt Failed")

    def copy_note(self, nid, content):
        pyperclip.copy(content)
        self.db.increment_note_copy(nid)
        self._load_data()
        self.show_toast(T["toast_copied"])

    def delete_note(self, nid):
        if messagebox.askyesno("Confirm", T["msg_confirm_del"]):
            self.db.delete_note(nid)
            self._load_data()

    def handle_action(self, choice, cid, current_tags, menu_widget):
        menu_widget.set("•••")
        if choice == T["menu_delete"]:
            if messagebox.askyesno("Confirm", T["msg_confirm_del"]):
                self.db.delete_credential(cid)
                self._load_data()
        elif choice == T["menu_edit_tags"]:
            EditTagsDialog(self, current_tags, lambda new_tags: self.update_tags_callback(cid, new_tags))

    def update_tags_callback(self, cid, new_tags):
        self.db.update_tags(cid, new_tags)
        self._load_data()
        self.show_toast(T["toast_updated"])

    def open_add_dialog(self):
        AddRecordDialog(self, self.save_new_entry)

    def open_add_note_dialog(self):
        AddNoteDialog(self, self.save_new_note)

    def open_settings(self):
        SettingsDialog(self, self.current_theme, self.current_lang, self.update_theme, self.update_lang,
                       self.export_csv, self.import_csv, self.change_storage_path)

    def save_new_entry(self, site, user, pwd, tags):
        self.db.add_credential(site, user, self.security.encrypt_password(pwd), tags)
        self._load_data()
        self.show_toast(T["toast_saved"])

    def save_new_note(self, title, content):
        self.db.add_note(title, content)
        self.switch_view("memos")
        self.show_toast(T["toast_saved"])

    def update_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.current_theme = new_theme
        self.db.set_config("theme", new_theme)
        self.show_toast(f"Theme: {new_theme}")

    def update_lang(self, new_lang):
        if new_lang == self.current_lang: return
        self.db.set_config("language", new_lang)
        messagebox.showinfo("Restart Required", T["msg_restart_lang"])
        self.quit_app()

    def change_storage_path(self):
        new_dir = filedialog.askdirectory(title="Select New Storage Folder")
        if not new_dir: return
        if os.path.normpath(new_dir) == os.path.normpath(ENV.data_dir):
            messagebox.showinfo("Info", "You selected the same folder.")
            return
        if messagebox.askyesno("Migrate Data?", T["msg_confirm_migrate"]):
            try:
                self.db.close()
                old_db = ENV.db_path
                old_key = ENV.key_path
                if os.path.exists(old_db): shutil.move(old_db, new_dir)
                if os.path.exists(old_key): shutil.move(old_key, new_dir)
                ENV.update_data_dir(new_dir)
                messagebox.showinfo("Success", T["msg_path_changed"])
                self.quit_app()
            except Exception as e:
                self.db = DatabaseManager()
                messagebox.showerror("Migration Failed", f"Error moving files:\n{e}")
        else:
            ENV.update_data_dir(new_dir)
            messagebox.showinfo("Path Changed", T["msg_path_changed"])
            self.quit_app()

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        try:
            rows = self.db.get_credentials()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Site", "Username", "Password", "Tags", "Hits"])
                for row in rows:
                    cid, site, user, enc, hits, tags = row
                    try:
                        real_pwd = self.security.decrypt_password(enc)
                    except:
                        real_pwd = "ERR_DECRYPT"
                    writer.writerow([site, user, real_pwd, tags, hits])
            self.show_toast(T["toast_import_ok"])
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        try:
            count_imported = 0
            count_skipped = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 3:
                        site, user, pwd = row[0].strip(), row[1].strip(), row[2].strip()
                        tags = row[3].strip() if len(row) > 3 else ""
                        if self.db.credential_exists(site, user):
                            count_skipped += 1
                            continue
                        enc = self.security.encrypt_password(pwd)
                        self.db.add_credential(site, user, enc, tags)
                        count_imported += 1
            self._load_data()
            msg = T["report_import"].format(count_imported, count_skipped)
            messagebox.showinfo("Import Report", msg)
        except Exception as e:
            messagebox.showerror("Import Failed", f"Check format: Site,User,Pwd,Tags\n{e}")

    def show_toast(self, message):
        if self.toast_timer is not None:
            try:
                self.after_cancel(self.toast_timer)
            except:
                pass
        self.lbl_status_l.configure(text=f" ⚡ {message}")
        self.toast_timer = self.after(3000, self._reset_toast)

    def _reset_toast(self):
        try:
            self.lbl_status_l.configure(text=" ⚡ Connected to Local DB ")
            self.toast_timer = None
        except:
            pass

    def _start_tray_thread(self):
        threading.Thread(target=self._setup_tray_icon, daemon=True).start()

    def _setup_tray_icon(self):
        image = create_app_icon()
        menu = pystray.Menu(pystray.MenuItem("Open LockBox", self._restore_window, default=True),
                            pystray.MenuItem("Exit", self._quit_from_tray))
        self.tray_icon = pystray.Icon("LockBox", image, "LockBox", menu)
        self.tray_icon.run()

    def on_close(self):
        self.withdraw()

    def _restore_window(self, icon, item):
        self.after(0, self.deiconify)

    def _quit_from_tray(self, icon, item):
        self.after(0, self.quit_app)

    def quit_app(self):
        if self.toast_timer: self.after_cancel(self.toast_timer)
        if self.tray_icon: self.tray_icon.stop()
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    # 🚨 关键修复逻辑：开启系统 DPI 感知 🚨
    try:
        # 告诉 Windows: "我是 DPI 感知的，请以我的 System DPI 为准，不要对我进行位图拉伸"
        # 1 = Process_System_DPI_Aware (系统级感知，主屏清晰，副屏系统缩放，稳定)
        # 2 = Process_Per_Monitor_DPI_Aware (显示器级感知，虽然最清晰但会导致Tkinter崩溃，所以不用)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        # Win7 等老系统兼容
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

    if ENV.load_or_setup_paths():
        app = PasswordApp()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()