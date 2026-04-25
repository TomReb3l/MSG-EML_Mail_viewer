# -*- coding: utf-8 -*-
import os
import re
import sys
import html
import tempfile
import subprocess
import shutil
from typing import Any
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

import tkinter as tk
from tkinter import filedialog, messagebox
from xml.sax.saxutils import escape

import customtkinter as ctk

try:
    import extract_msg
except ImportError:
    extract_msg = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


APP_NAME = "MailViewer"

SUSPICIOUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".scr", ".js", ".jse", ".vbs", ".vbe",
    ".ps1", ".psm1", ".hta", ".msi", ".dll", ".jar", ".reg", ".iso",
    ".zip", ".rar", ".7z", ".cab", ".lnk", ".chm"
}

SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately", "verify", "verification", "login", "reset password",
    "payment failed", "invoice attached", "open attachment", "enable macros",
    "click here", "confirm account", "security alert", "your account",
    "κάντε login", "επαλήθευση", "επιβεβαίωση", "επείγον", "άμεσα",
    "κωδικός", "λογαριασμός", "συνδεθείτε", "πατήστε εδώ", "τιμολόγιο",
    "επισυναπτόμενο", "άνοιξε το συνημμένο", "ενεργοποίηση μακροεντολών"
]

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "rb.gy", "buff.ly"
}

TRUST_BRANDS = ["microsoft", "google", "paypal", "amazon", "bank", "apple", "dhl", "acs"]

URL_REGEX = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', re.IGNORECASE)
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE)
IP_HOST_REGEX = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')

THEME = {
    "bg": "#1f1f1f",
    "panel": "#2b2b2b",
    "panel_alt": "#343638",
    "field": "#26282b",
    "border": "#4a4d50",
    "text": "#ffffff",
    "text_soft": "#d8d8d8",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "danger": "#ef4444",
    "success": "#22c55e",
}

TEXTS = {
    "el": {
        "title": "Mail Viewer (.MSG / .EML) & Basic Security Check",
        "open_files": "Άνοιγμα email αρχείων",
        "open_folder": "Άνοιγμα φακέλου",
        "clear": "Καθαρισμός",
        "export_pdf": "Export PDF",
        "print_email": "Εκτύπωση",
        "no_message_title": "Δεν υπάρχει επιλεγμένο μήνυμα",
        "no_message_msg": "Επίλεξε πρώτα ένα email από τη λίστα.",
        "save_pdf_title": "Αποθήκευση PDF",
        "pdf_saved_title": "PDF δημιουργήθηκε",
        "pdf_saved_msg": "Το PDF αποθηκεύτηκε επιτυχώς.",
        "pdf_error_title": "Σφάλμα PDF",
        "print_error_title": "Σφάλμα εκτύπωσης",
        "print_started": "Η εκτύπωση στάλθηκε στον προεπιλεγμένο εκτυπωτή.",
        "print_opened_pdf": "Δεν υπάρχει εφαρμογή PDF με εντολή άμεσης εκτύπωσης. Το PDF άνοιξε για να το τυπώσεις χειροκίνητα με Ctrl+P.",
        "print_opened_pdf_title": "Άνοιγμα PDF για εκτύπωση",
        "report_title": "Αναφορά Email",
        "report_security": "Έλεγχος Ασφάλειας",
        "report_findings": "Ευρήματα",
        "report_links": "Links",
        "report_attachments": "Συνημμένα",
        "report_keywords": "Λέξεις / Flags",
        "missing_reportlab": "Λείπει η βιβλιοθήκη reportlab.\n\nΤρέξε:\npip install reportlab",
        "language": "Γλώσσα",
        "hint": "Φόρτωσε .msg ή .eml αρχεία",
        "files": "Αρχεία email",
        "file": "Αρχείο",
        "type": "Τύπος",
        "subject": "Θέμα",
        "from": "Από",
        "to": "Προς",
        "date": "Ημερομηνία",
        "message_tab": "Μήνυμα",
        "security_tab": "Έλεγχος Ασφάλειας",
        "message_body": "Περιεχόμενο μηνύματος",
        "alerts": "Ευρήματα",
        "links": "Links",
        "attachments": "Συνημμένα",
        "flags": "Λέξεις / Flags",
        "risk_score": "Risk Score",
        "level": "Επίπεδο",
        "defender": "Defender Scan",
        "ready": "Έτοιμο",
        "loaded_files": "Φορτώθηκαν {count} αρχεία.",
        "loaded_folder": "Φορτώθηκαν {count} αρχεία από τον φάκελο.",
        "total_loaded": "Σύνολο φορτωμένων μηνυμάτων: {count}",
        "showing_message": "Εμφανίζεται μήνυμα {index} από {total}",
        "cleared": "Καθαρίστηκαν όλα τα δεδομένα.",
        "select_files": "Επιλογή email αρχείων",
        "select_folder": "Επιλογή φακέλου με .msg / .eml αρχεία",
        "no_files_title": "Δεν βρέθηκαν αρχεία",
        "no_files_msg": "Δεν βρέθηκαν .msg ή .eml αρχεία στον φάκελο.",
        "read_error": "Σφάλμα ανάγνωσης",
        "missing_extract_msg": "Για αρχεία .msg χρειάζεται η βιβλιοθήκη extract_msg.\n\nΤρέξε:\npip install extract-msg",
        "unsupported_type": "Μη υποστηριζόμενος τύπος αρχείου",
        "no_subject": "(Χωρίς θέμα)",
        "unknown_sender": "(Άγνωστος αποστολέας)",
        "no_name": "(χωρίς όνομα)",
        "no_content": "(Δεν βρέθηκε περιεχόμενο μηνύματος)",
        "no_links": "(Δεν βρέθηκαν links)",
        "no_attachments": "(Δεν υπάρχουν συνημμένα)",
        "no_keywords": "(Δεν βρέθηκαν flagged keywords)",
        "sender_missing": "Λείπει αποστολέας.",
        "display_name_spoof": "Πιθανό display-name spoofing: εμφανίζεται '{brand}' αλλά domain '{domain}'.",
        "sender_short_domain": "Ο αποστολέας χρησιμοποιεί shortened/ύποπτο domain: {domain}",
        "ip_link": "Link με IP αντί για domain: {url}",
        "shortened_link": "Shortened link: {url}",
        "brand_mismatch_link": "Πιθανό brand mismatch σε link: {url}",
        "suspicious_attachment": "Ύποπτο συνημμένο: {name}",
        "many_links": "Πολλά links στο μήνυμα: {count}",
        "found_keywords": "Βρέθηκαν phishing/πίεσης keywords.",
        "uppercase_subject": "Το θέμα είναι όλο με κεφαλαία.",
        "defender_detected": "Ο Windows Defender εντόπισε απειλή σε συνημμένο.",
        "defender_error": "Defender scan δεν ολοκληρώθηκε: {msg}",
        "no_findings": "Δεν βρέθηκαν εμφανή ύποπτα στοιχεία με τον βασικό heuristic έλεγχο.",
        "risk_low": "Χαμηλό Ρίσκο",
        "risk_medium": "Μέτριο Ρίσκο",
        "risk_high": "Υψηλό Ρίσκο",
        "risk_very_high": "Πολύ Ύποπτο",
        "status_not_available": "not_available",
        "status_no_attachments": "Δεν υπάρχουν συνημμένα.",
        "status_no_extractable": "Δεν ήταν δυνατή η εξαγωγή συνημμένων για scan.",
        "status_clean": "Δεν εντοπίστηκε απειλή από τον Defender.",
        "status_defender_not_found": "Δεν βρέθηκε το MpCmdRun.exe του Windows Defender.",
        "status_timeout": "Ο Defender scan έληξε λόγω timeout.",
        "suspicious_tag": " [ΥΠΟΠΤΟ]",
    },
    "en": {
        "title": "Mail Viewer (.MSG / .EML) & Basic Security Check",
        "open_files": "Open email files",
        "open_folder": "Open folder",
        "clear": "Clear",
        "export_pdf": "Export PDF",
        "print_email": "Print",
        "no_message_title": "No message selected",
        "no_message_msg": "Select an email from the list first.",
        "save_pdf_title": "Save PDF",
        "pdf_saved_title": "PDF created",
        "pdf_saved_msg": "The PDF was saved successfully.",
        "pdf_error_title": "PDF error",
        "print_error_title": "Print error",
        "print_started": "The print job was sent to the default printer.",
        "print_opened_pdf": "No PDF application is associated with direct printing. The PDF was opened so you can print it manually with Ctrl+P.",
        "print_opened_pdf_title": "Open PDF for printing",
        "report_title": "Email Report",
        "report_security": "Security Check",
        "report_findings": "Findings",
        "report_links": "Links",
        "report_attachments": "Attachments",
        "report_keywords": "Keywords / Flags",
        "missing_reportlab": "The reportlab library is missing.\n\nRun:\npip install reportlab",
        "language": "Language",
        "hint": "Load .msg or .eml files",
        "files": "Email files",
        "file": "File",
        "type": "Type",
        "subject": "Subject",
        "from": "From",
        "to": "To",
        "date": "Date",
        "message_tab": "Message",
        "security_tab": "Security Check",
        "message_body": "Message body",
        "alerts": "Findings",
        "links": "Links",
        "attachments": "Attachments",
        "flags": "Keywords / Flags",
        "risk_score": "Risk Score",
        "level": "Level",
        "defender": "Defender Scan",
        "ready": "Ready",
        "loaded_files": "Loaded {count} files.",
        "loaded_folder": "Loaded {count} files from folder.",
        "total_loaded": "Total loaded messages: {count}",
        "showing_message": "Showing message {index} of {total}",
        "cleared": "All data cleared.",
        "select_files": "Select email files",
        "select_folder": "Select folder with .msg / .eml files",
        "no_files_title": "No files found",
        "no_files_msg": "No .msg or .eml files were found in the selected folder.",
        "read_error": "Read error",
        "missing_extract_msg": "The extract_msg library is required for .msg files.\n\nRun:\npip install extract-msg",
        "unsupported_type": "Unsupported file type",
        "no_subject": "(No subject)",
        "unknown_sender": "(Unknown sender)",
        "no_name": "(no name)",
        "no_content": "(No message content found)",
        "no_links": "(No links found)",
        "no_attachments": "(No attachments)",
        "no_keywords": "(No flagged keywords found)",
        "sender_missing": "Sender is missing.",
        "display_name_spoof": "Possible display-name spoofing: '{brand}' shown but domain is '{domain}'.",
        "sender_short_domain": "Sender uses shortened/suspicious domain: {domain}",
        "ip_link": "Link uses IP instead of domain: {url}",
        "shortened_link": "Shortened link: {url}",
        "brand_mismatch_link": "Possible brand mismatch in link: {url}",
        "suspicious_attachment": "Suspicious attachment: {name}",
        "many_links": "Many links in message: {count}",
        "found_keywords": "Phishing / pressure keywords were found.",
        "uppercase_subject": "Subject is all uppercase.",
        "defender_detected": "Windows Defender detected a threat in an attachment.",
        "defender_error": "Defender scan did not complete: {msg}",
        "no_findings": "No obvious suspicious findings were detected by the basic heuristic check.",
        "risk_low": "Low Risk",
        "risk_medium": "Medium Risk",
        "risk_high": "High Risk",
        "risk_very_high": "Highly Suspicious",
        "status_not_available": "not_available",
        "status_no_attachments": "No attachments.",
        "status_no_extractable": "Attachments could not be extracted for scanning.",
        "status_clean": "No threat detected by Defender.",
        "status_defender_not_found": "Windows Defender MpCmdRun.exe was not found.",
        "status_timeout": "Defender scan timed out.",
        "suspicious_tag": " [SUSPICIOUS]",
    }
}


class MailViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "el"
        self.messages = []
        self.current_index = None

        self.title(TEXTS[self.current_lang]["title"])
        self.geometry("1400x860")
        self.minsize(1100, 720)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=THEME["bg"])
        self._set_window_icon()

        self._build_ui()
        self.apply_language(refresh_current=False)

    def t(self, key, **kwargs):
        text = TEXTS[self.current_lang][key]
        return text.format(**kwargs) if kwargs else text

    def _card(self, master):
        return ctk.CTkFrame(master, fg_color=THEME["panel"], corner_radius=12, border_width=1, border_color=THEME["border"])

    def _label(self, master, text="", soft=False):
        return ctk.CTkLabel(
            master,
            text=text,
            text_color=THEME["text_soft"] if soft else THEME["text"],
            font=ctk.CTkFont(size=13, weight="normal"),
        )

    @staticmethod
    def _resource_path(relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(base_path, relative_path)

    def _set_window_icon(self):
        icon_path = self._resource_path("mail_viewer_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _value_entry(self, master, textvariable):
        return ctk.CTkEntry(
            master,
            textvariable=textvariable,
            fg_color=THEME["field"],
            border_color=THEME["border"],
            text_color=THEME["text"],
            height=36,
        )

    def _build_ui(self):
        self.file_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.from_var = tk.StringVar()
        self.to_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.top_card = self._card(self)
        self.top_card.pack(fill="x", padx=12, pady=(12, 8))

        self.btn_open_files = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color=THEME["accent_hover"], text_color=THEME["text"],
            command=self.open_files
        )
        self.btn_open_files.pack(side="left", padx=(10, 8), pady=10)

        self.btn_open_folder = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color=THEME["accent_hover"], text_color=THEME["text"],
            command=self.open_folder
        )
        self.btn_open_folder.pack(side="left", padx=0, pady=10)

        self.btn_clear = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color="#7f1d1d", text_color=THEME["text"],
            command=self.clear_all
        )
        self.btn_clear.pack(side="left", padx=8, pady=10)

        self.btn_export_pdf = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color=THEME["accent_hover"], text_color=THEME["text"],
            command=self.export_current_pdf
        )
        self.btn_export_pdf.pack(side="left", padx=(0, 8), pady=10)

        self.btn_print = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color=THEME["accent_hover"], text_color=THEME["text"],
            command=self.print_current_message
        )
        self.btn_print.pack(side="left", padx=(0, 8), pady=10)

        self.top_info_label = self._label(self.top_card, soft=True)
        self.top_info_label.pack(side="left", padx=(14, 0), pady=10)

        self.lang_label = self._label(self.top_card, soft=True)
        self.lang_label.pack(side="right", padx=(8, 12), pady=10)

        self.lang_var = tk.StringVar(value="Ελληνικά")
        self.lang_menu = ctk.CTkOptionMenu(
            self.top_card,
            values=["Ελληνικά", "English"],
            variable=self.lang_var,
            command=self.on_language_change,
            width=120,
            height=36,
            corner_radius=10,
            fg_color=THEME["field"],
            button_color=THEME["panel_alt"],
            button_hover_color=THEME["accent_hover"],
            dropdown_fg_color=THEME["panel"],
            dropdown_hover_color=THEME["panel_alt"],
            text_color=THEME["text"],
        )
        self.lang_menu.pack(side="right", padx=(0, 0), pady=10)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=4)
        self.content.grid_rowconfigure(0, weight=1)

        self.left_card = self._card(self.content)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        self.left_card.grid_rowconfigure(1, weight=1)
        self.left_card.grid_columnconfigure(0, weight=1)

        self.files_label = self._label(self.left_card)
        self.files_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 8))

        self.listbox = tk.Listbox(
            self.left_card,
            bg=THEME["field"],
            fg=THEME["text"],
            selectbackground=THEME["accent"],
            selectforeground=THEME["text"],
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Segoe UI", 12),
        )
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.listbox.bind("<<ListboxSelect>>", self.on_select_message)

        self.right_card = self._card(self.content)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)
        self.right_card.grid_rowconfigure(2, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        self.form_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        self.form_frame.grid_columnconfigure(1, weight=1)

        self.lbl_file = self._label(self.form_frame)
        self.lbl_file.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_file = self._value_entry(self.form_frame, self.file_var)
        self.ent_file.grid(row=0, column=1, sticky="ew", pady=5)

        self.lbl_type = self._label(self.form_frame)
        self.lbl_type.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_type = self._value_entry(self.form_frame, self.type_var)
        self.ent_type.grid(row=1, column=1, sticky="ew", pady=5)

        self.lbl_subject = self._label(self.form_frame)
        self.lbl_subject.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_subject = self._value_entry(self.form_frame, self.subject_var)
        self.ent_subject.grid(row=2, column=1, sticky="ew", pady=5)

        self.lbl_from = self._label(self.form_frame)
        self.lbl_from.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_from = self._value_entry(self.form_frame, self.from_var)
        self.ent_from.grid(row=3, column=1, sticky="ew", pady=5)

        self.lbl_to = self._label(self.form_frame)
        self.lbl_to.grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_to = self._value_entry(self.form_frame, self.to_var)
        self.ent_to.grid(row=4, column=1, sticky="ew", pady=5)

        self.lbl_date = self._label(self.form_frame)
        self.lbl_date.grid(row=5, column=0, sticky="w", padx=(0, 10), pady=5)
        self.ent_date = self._value_entry(self.form_frame, self.date_var)
        self.ent_date.grid(row=5, column=1, sticky="ew", pady=5)

        self.tabview = ctk.CTkTabview(
            self.right_card,
            fg_color=THEME["panel"],
            segmented_button_fg_color=THEME["panel_alt"],
            segmented_button_selected_color=THEME["accent"],
            segmented_button_selected_hover_color=THEME["accent_hover"],
            segmented_button_unselected_color=THEME["panel_alt"],
            segmented_button_unselected_hover_color=THEME["field"],
            text_color=THEME["text"],
            corner_radius=10,
        )
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))

        self.tabview.add("message")
        self.tabview.add("security")

        self.message_tab = self.tabview.tab("message")
        self.security_tab = self.tabview.tab("security")

        self.message_tab.grid_rowconfigure(1, weight=1)
        self.message_tab.grid_columnconfigure(0, weight=1)

        self.message_body_label = self._label(self.message_tab)
        self.message_body_label.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 6))

        self.body_text = tk.Text(
            self.message_tab,
            wrap="word",
            bg=THEME["field"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            selectbackground=THEME["accent"],
            selectforeground=THEME["text"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
            font=("Segoe UI", 14),
        )
        self.body_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.security_tab.grid_rowconfigure(1, weight=1)
        self.security_tab.grid_columnconfigure(0, weight=1)

        self.security_header = ctk.CTkFrame(self.security_tab, fg_color="transparent")
        self.security_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 6))
        self.security_header.grid_columnconfigure((0, 1, 2), weight=1)

        self.risk_label = self._label(self.security_header)
        self.risk_label.grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.level_label = self._label(self.security_header)
        self.level_label.grid(row=0, column=1, sticky="w", padx=(0, 16))
        self.defender_label = self._label(self.security_header)
        self.defender_label.grid(row=0, column=2, sticky="w")

        self.security_grid = ctk.CTkFrame(self.security_tab, fg_color="transparent")
        self.security_grid.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.security_grid.grid_columnconfigure((0, 1), weight=1)
        self.security_grid.grid_rowconfigure((1, 3), weight=1)

        self.alerts_title = self._label(self.security_grid)
        self.alerts_title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.links_title = self._label(self.security_grid)
        self.links_title.grid(row=2, column=0, sticky="w", pady=(10, 4))
        self.attachments_title = self._label(self.security_grid)
        self.attachments_title.grid(row=0, column=1, sticky="w", pady=(0, 4), padx=(8, 0))
        self.flags_title = self._label(self.security_grid)
        self.flags_title.grid(row=2, column=1, sticky="w", pady=(10, 4), padx=(8, 0))

        self.alerts_text = self._make_text_box(self.security_grid)
        self.alerts_text.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        self.links_text = self._make_text_box(self.security_grid)
        self.links_text.grid(row=3, column=0, sticky="nsew", pady=(0, 0))
        self.attachments_text = self._make_text_box(self.security_grid)
        self.attachments_text.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        self.flags_text = self._make_text_box(self.security_grid)
        self.flags_text.grid(row=3, column=1, sticky="nsew", padx=(8, 0))

        self.status_bar = self._card(self)
        self.status_bar.pack(fill="x", padx=12, pady=(0, 12))
        self.status_label = self._label(self.status_bar, soft=True)
        self.status_label.pack(anchor="w", padx=12, pady=8)

    def _make_text_box(self, master):
        widget = tk.Text(
            master,
            wrap="word",
            bg=THEME["field"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            selectbackground=THEME["accent"],
            selectforeground=THEME["text"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
            font=("Consolas", 15),
            height=8,
        )
        return widget

    def on_language_change(self, choice):
        self.current_lang = "en" if choice == "English" else "el"
        self.apply_language(refresh_current=True)

    def _message_tab_names(self):
        return ["message", TEXTS["el"]["message_tab"], TEXTS["en"]["message_tab"]]

    def _security_tab_names(self):
        return ["security", TEXTS["el"]["security_tab"], TEXTS["en"]["security_tab"]]

    def _existing_tab_name(self, candidates):
        for name in candidates:
            try:
                self.tabview.tab(name)
                return name
            except Exception:
                continue
        return None

    def _safe_rename_tab(self, candidates, new_name):
        existing_name = self._existing_tab_name(candidates)
        if existing_name and existing_name != new_name:
            self.tabview.rename(existing_name, new_name)

    def _safe_set_active_tab(self, preferred_name):
        existing_name = self._existing_tab_name([preferred_name])
        if existing_name:
            self.tabview.set(existing_name)
            return

        existing_name = self._existing_tab_name(self._message_tab_names() + self._security_tab_names())
        if existing_name:
            self.tabview.set(existing_name)

    def apply_language(self, refresh_current=True):
        previous_tab = None
        try:
            previous_tab = self.tabview.get()
        except Exception:
            previous_tab = None

        previous_tab_is_security = previous_tab in set(self._security_tab_names())

        self.title(self.t("title"))
        self.btn_open_files.configure(text=self.t("open_files"))
        self.btn_open_folder.configure(text=self.t("open_folder"))
        self.btn_clear.configure(text=self.t("clear"))
        self.btn_export_pdf.configure(text=self.t("export_pdf"))
        self.btn_print.configure(text=self.t("print_email"))
        self.lang_label.configure(text=f"{self.t('language')}:")
        self.top_info_label.configure(text=self.t("hint") if not self.messages else self.t("total_loaded", count=len(self.messages)))
        self.files_label.configure(text=self.t("files"))
        self.lbl_file.configure(text=f"{self.t('file')}:")
        self.lbl_type.configure(text=f"{self.t('type')}:")
        self.lbl_subject.configure(text=f"{self.t('subject')}:")
        self.lbl_from.configure(text=f"{self.t('from')}:")
        self.lbl_to.configure(text=f"{self.t('to')}:")
        self.lbl_date.configure(text=f"{self.t('date')}:")
        self._safe_rename_tab(self._message_tab_names(), self.t("message_tab"))
        self._safe_rename_tab(self._security_tab_names(), self.t("security_tab"))
        self._safe_set_active_tab(self.t("security_tab") if previous_tab_is_security else self.t("message_tab"))
        self.message_body_label.configure(text=self.t("message_body"))
        self.alerts_title.configure(text=self.t("alerts"))
        self.links_title.configure(text=self.t("links"))
        self.attachments_title.configure(text=self.t("attachments"))
        self.flags_title.configure(text=self.t("flags"))

        if not self.status_var.get():
            self.status_var.set(self.t("ready"))
        self.status_label.configure(text=self.status_var.get())
        self._refresh_list()

        if refresh_current and self.current_index is not None and 0 <= self.current_index < len(self.messages):
            self._display_message(self.current_index)
        else:
            self.risk_label.configure(text=f"{self.t('risk_score')}: -")
            self.level_label.configure(text=f"{self.t('level')}: -")
            self.defender_label.configure(text=f"{self.t('defender')}: -")

    def open_files(self):
        paths = filedialog.askopenfilenames(
            title=self.t("select_files"),
            filetypes=[("Email files", "*.msg *.eml"), ("MSG files", "*.msg"), ("EML files", "*.eml")]
        )
        if not paths:
            return

        loaded = 0
        for path in paths:
            if self._load_message(path):
                loaded += 1

        self._refresh_list()
        self._set_status(self.t("loaded_files", count=loaded))
        self.top_info_label.configure(text=self.t("total_loaded", count=len(self.messages)))

        if self.messages and self.current_index is None:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(0)
            self.listbox.event_generate("<<ListboxSelect>>")

    def open_folder(self):
        folder = filedialog.askdirectory(title=self.t("select_folder"))
        if not folder:
            return

        mail_files = [os.path.join(folder, x) for x in os.listdir(folder) if x.lower().endswith((".msg", ".eml"))]
        if not mail_files:
            messagebox.showinfo(self.t("no_files_title"), self.t("no_files_msg"))
            return

        loaded = 0
        for path in sorted(mail_files):
            if self._load_message(path):
                loaded += 1

        self._refresh_list()
        self._set_status(self.t("loaded_folder", count=loaded))
        self.top_info_label.configure(text=self.t("total_loaded", count=len(self.messages)))

        if self.messages and self.current_index is None:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(0)
            self.listbox.event_generate("<<ListboxSelect>>")

    def _load_message(self, path):
        for item in self.messages:
            if os.path.abspath(item["path"]) == os.path.abspath(path):
                return False

        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".msg":
                if extract_msg is None:
                    raise RuntimeError(self.t("missing_extract_msg"))
                data = self._read_msg(path)
            elif ext == ".eml":
                data = self._read_eml(path)
            else:
                raise RuntimeError(f"{self.t('unsupported_type')}: {ext}")

            data["analysis"] = self._analyze_message(
                data["subject"], data["sender"], data["to"], data["body"], data["attachments"]
            )
            self.messages.append(data)
            return True
        except Exception as exc:
            messagebox.showwarning(self.t("read_error"), f"{path}\n\n{exc}")
            return False

    def _read_msg(self, path):
        if extract_msg is None:
            raise RuntimeError(self.t("missing_extract_msg"))
        msg = extract_msg.Message(path)  # type: ignore[union-attr]
        return {
            "path": path,
            "mail_type": "MSG",
            "subject": self._safe_text(msg.subject),
            "sender": self._safe_text(msg.sender),
            "to": self._safe_text(msg.to),
            "date": self._format_date(msg.date),
            "body": self._extract_msg_body(msg),
            "attachments": self._extract_msg_attachments_info(msg),
        }

    def _read_eml(self, path):
        with open(path, "rb") as f:
            eml = BytesParser(policy=policy.default).parse(f)
        return {
            "path": path,
            "mail_type": "EML",
            "subject": self._safe_text(eml.get("subject", "")),
            "sender": self._safe_text(eml.get("from", "")),
            "to": self._safe_text(eml.get("to", "")),
            "date": self._format_date(self._parse_email_date(eml.get("date", ""))),
            "body": self._extract_eml_body(eml),
            "attachments": self._extract_eml_attachments_info(eml),
        }

    def _extract_msg_body(self, msg):
        body = self._safe_text(getattr(msg, "body", ""))
        if body:
            return body

        html_body = getattr(msg, "htmlBody", b"")
        if isinstance(html_body, bytes):
            decoded = ""
            for enc in ("utf-8", "cp1253", "latin1"):
                try:
                    decoded = html_body.decode(enc, errors="replace")
                    break
                except Exception:
                    decoded = ""
            html_body = decoded

        html_body = self._safe_text(html_body)
        if html_body:
            text = re.sub(r"<[^>]+>", " ", html_body)
            text = html.unescape(text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        return self.t("no_content")

    def _extract_eml_body(self, eml):
        plain_parts = []
        html_parts = []

        if eml.is_multipart():
            for part in eml.walk():
                if str(part.get_content_disposition() or "").lower() == "attachment":
                    continue

                content_type = str(part.get_content_type() or "").lower()
                try:
                    payload = part.get_content()
                except Exception:
                    try:
                        raw = part.get_payload(decode=True) or b""
                        charset = part.get_content_charset() or "utf-8"
                        payload = raw.decode(charset, errors="replace")
                    except Exception:
                        payload = ""

                payload = self._safe_text(payload)
                if not payload:
                    continue

                if content_type == "text/plain":
                    plain_parts.append(payload)
                elif content_type == "text/html":
                    html_parts.append(payload)
        else:
            try:
                payload = eml.get_content()
            except Exception:
                raw = eml.get_payload(decode=True) or b""
                charset = eml.get_content_charset() or "utf-8"
                payload = raw.decode(charset, errors="replace")
            payload = self._safe_text(payload)
            if str(eml.get_content_type() or "").lower() == "text/html":
                html_parts.append(payload)
            else:
                plain_parts.append(payload)

        if plain_parts:
            return "\n\n".join(x for x in plain_parts if x).strip()

        if html_parts:
            text = "\n\n".join(html_parts)
            text = re.sub(r"<[^>]+>", " ", text)
            text = html.unescape(text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        return self.t("no_content")

    def _extract_msg_attachments_info(self, msg):
        results = []
        for att in getattr(msg, "attachments", []) or []:
            name = (
                self._safe_text(getattr(att, "longFilename", ""))
                or self._safe_text(getattr(att, "filename", ""))
                or self.t("no_name")
            )
            ext = os.path.splitext(name)[1].lower()
            data = getattr(att, "data", None)
            size_text = f"{len(data)} bytes" if isinstance(data, (bytes, bytearray)) else "-"
            results.append({"name": name, "ext": ext, "size": size_text, "data": data if isinstance(data, (bytes, bytearray)) else None})
        return results

    def _extract_eml_attachments_info(self, eml):
        results = []
        for part in eml.iter_attachments():
            name = self._safe_text(part.get_filename()) or self.t("no_name")
            ext = os.path.splitext(name)[1].lower()
            try:
                raw = part.get_payload(decode=True)
            except Exception:
                raw = None
            size_text = f"{len(raw)} bytes" if isinstance(raw, (bytes, bytearray)) else "-"
            results.append({"name": name, "ext": ext, "size": size_text, "data": raw if isinstance(raw, (bytes, bytearray)) else None})
        return results

    def _analyze_message(self, subject, sender, to_, body, attachments):
        alerts = []
        score = 0

        links = self._extract_urls(body)
        found_keywords = self._find_keywords(" ".join([subject, body]))
        sender_email = self._extract_email(sender)
        sender_domain = self._domain_from_email(sender_email)
        sender_text_lower = sender.lower()

        if not sender.strip():
            alerts.append(self.t("sender_missing"))
            score += 2

        if sender_domain:
            for brand in TRUST_BRANDS:
                if brand in sender_text_lower and brand not in sender_domain:
                    alerts.append(self.t("display_name_spoof", brand=brand, domain=sender_domain))
                    score += 3
                    break
            if sender_domain in SHORTENER_DOMAINS:
                alerts.append(self.t("sender_short_domain", domain=sender_domain))
                score += 2

        for url in links:
            host = self._host_from_url(url)
            if not host:
                continue
            if IP_HOST_REGEX.match(host):
                alerts.append(self.t("ip_link", url=url))
                score += 3
            if host.lower() in SHORTENER_DOMAINS:
                alerts.append(self.t("shortened_link", url=url))
                score += 2
            for brand in TRUST_BRANDS:
                if brand in body.lower() and brand not in host.lower() and any(x in url.lower() for x in ["login", "verify", "secure", "account"]):
                    alerts.append(self.t("brand_mismatch_link", url=url))
                    score += 2
                    break

        suspicious_attachments = []
        for att in attachments:
            if att["ext"] in SUSPICIOUS_EXTENSIONS:
                suspicious_attachments.append(att["name"])
                alerts.append(self.t("suspicious_attachment", name=att["name"]))
                score += 3

        if len(links) >= 3:
            alerts.append(self.t("many_links", count=len(links)))
            score += 1

        if found_keywords:
            alerts.append(self.t("found_keywords"))
            score += min(3, len(found_keywords))

        if subject and subject.isupper() and len(subject) > 8:
            alerts.append(self.t("uppercase_subject"))
            score += 1

        defender_result = self._scan_attachments_with_defender(attachments)
        if defender_result["status"] == "malicious":
            alerts.append(self.t("defender_detected"))
            score += 6
        elif defender_result["status"] == "error":
            alerts.append(self.t("defender_error", msg=defender_result["message"]))
            score += 1

        return {
            "score": score,
            "level": self._risk_level(score),
            "alerts": alerts or [self.t("no_findings")],
            "links": links,
            "keywords": found_keywords,
            "suspicious_attachments": suspicious_attachments,
            "defender": defender_result,
        }

    def _scan_attachments_with_defender(self, attachments):
        if not attachments:
            return {"status": "no_attachments", "message": self.t("status_no_attachments")}

        mpcmdrun = r"C:\Program Files\Windows Defender\MpCmdRun.exe"
        if not os.path.exists(mpcmdrun):
            return {"status": self.t("status_not_available"), "message": self.t("status_defender_not_found")}

        temp_dir = tempfile.mkdtemp(prefix="mail_attach_scan_")
        try:
            written = 0
            for i, att in enumerate(attachments, start=1):
                if att["data"] is None:
                    continue
                safe_name = re.sub(r'[\\/:*?"<>|]+', "_", att["name"]) or f"attachment_{i}"
                out_path = os.path.join(temp_dir, safe_name)
                with open(out_path, "wb") as f:
                    f.write(att["data"])
                written += 1

            if written == 0:
                return {"status": "no_extractable", "message": self.t("status_no_extractable")}

            cmd = [mpcmdrun, "-Scan", "-ScanType", "3", "-File", temp_dir]
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            combined = "\n".join([proc.stdout or "", proc.stderr or ""]).strip().lower()

            if any(x in combined for x in ["threat", "infected", "malware", "virus", "found"]):
                return {"status": "malicious", "message": combined[:1500] or "Threat found"}
            if proc.returncode == 0:
                return {"status": "clean", "message": self.t("status_clean")}
            return {"status": "unknown", "message": combined[:1500] or f"Return code: {proc.returncode}"}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": self.t("status_timeout")}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.messages:
            subject = item["subject"] if item["subject"] else self.t("no_subject")
            sender = item["sender"] if item["sender"] else self.t("unknown_sender")
            self.listbox.insert(tk.END, f"[{item['mail_type']}] {subject}  |  {sender}")

    def on_select_message(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            self._display_message(selection[0])

    def _display_message(self, index):
        self.current_index = index
        item = self.messages[index]

        self.file_var.set(item["path"])
        self.type_var.set(item["mail_type"])
        self.subject_var.set(item["subject"])
        self.from_var.set(item["sender"])
        self.to_var.set(item["to"])
        self.date_var.set(item["date"])

        self._set_text(self.body_text, item["body"])
        self._populate_security(item["attachments"], item["analysis"])
        self._set_status(self.t("showing_message", index=index + 1, total=len(self.messages)))

    def _populate_security(self, attachments, analysis):
        self.risk_label.configure(text=f"{self.t('risk_score')}: {analysis['score']}/10+")
        self.level_label.configure(text=f"{self.t('level')}: {analysis['level']}")
        self.defender_label.configure(text=f"{self.t('defender')}: {analysis['defender']['status']}")

        self._set_text(self.alerts_text, "\n".join(f"- {x}" for x in analysis["alerts"]))
        self._set_text(self.links_text, "\n".join(analysis["links"]) if analysis["links"] else self.t("no_links"))

        if attachments:
            lines = []
            for att in attachments:
                tag = self.t("suspicious_tag") if att["ext"] in SUSPICIOUS_EXTENSIONS else ""
                lines.append(f"{att['name']} | {att['size']}{tag}")
            self._set_text(self.attachments_text, "\n".join(lines))
        else:
            self._set_text(self.attachments_text, self.t("no_attachments"))

        self._set_text(self.flags_text, "\n".join(analysis["keywords"]) if analysis["keywords"] else self.t("no_keywords"))

    def _set_text(self, widget, text):
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)

    def _set_status(self, text):
        self.status_var.set(text)
        self.status_label.configure(text=text)

    def _get_current_message(self):
        if self.current_index is None or not (0 <= self.current_index < len(self.messages)):
            messagebox.showwarning(self.t("no_message_title"), self.t("no_message_msg"))
            return None
        return self.messages[self.current_index]

    @staticmethod
    def _safe_filename(value):
        value = value or "email"
        value = re.sub(r'[\\/:*?"<>|]+', "_", str(value))
        value = re.sub(r"\s+", " ", value).strip()
        return value[:120] or "email"

    def _register_pdf_font(self):
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
        for font_path in candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("MailViewerFont", font_path))
                    return "MailViewerFont"
                except Exception:
                    continue
        return "Helvetica"

    @staticmethod
    def _clean_pdf_text(value):
        value = "" if value is None else str(value)
        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
        return value

    def _pdf_text(self, value):
        value = self._clean_pdf_text(value)
        return escape(value).replace("\n", "<br/>")

    def _build_pdf_story(self, item):
        font_name = self._register_pdf_font()
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "MailViewerTitle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=18,
            leading=22,
            spaceAfter=14,
        )
        heading_style = ParagraphStyle(
            "MailViewerHeading",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=6,
        )
        normal_style = ParagraphStyle(
            "MailViewerNormal",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            wordWrap="CJK",
            spaceAfter=5,
        )
        small_style = ParagraphStyle(
            "MailViewerSmall",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=9,
            leading=12,
            wordWrap="CJK",
            spaceAfter=4,
        )

        analysis = item.get("analysis", {}) or {}
        defender = analysis.get("defender", {}) or {}
        attachments = item.get("attachments", []) or []
        links = analysis.get("links", []) or []
        alerts = analysis.get("alerts", []) or []
        keywords = analysis.get("keywords", []) or []

        story: list[Any] = [Paragraph(self._pdf_text(self.t("report_title")), title_style)]

        meta_lines = [
            (self.t("file"), item.get("path", "")),
            (self.t("type"), item.get("mail_type", "")),
            (self.t("subject"), item.get("subject", "")),
            (self.t("from"), item.get("sender", "")),
            (self.t("to"), item.get("to", "")),
            (self.t("date"), item.get("date", "")),
        ]
        for label, value in meta_lines:
            story.append(Paragraph(f"<b>{self._pdf_text(label)}:</b> {self._pdf_text(value)}", normal_style))

        story.append(Spacer(1, 10))
        story.append(Paragraph(self._pdf_text(self.t("message_body")), heading_style))
        story.append(Paragraph(self._pdf_text(item.get("body", "") or self.t("no_content")), normal_style))

        story.append(Spacer(1, 10))
        story.append(Paragraph(self._pdf_text(self.t("report_security")), heading_style))
        story.append(Paragraph(f"<b>{self._pdf_text(self.t('risk_score'))}:</b> {self._pdf_text(analysis.get('score', '-'))}", normal_style))
        story.append(Paragraph(f"<b>{self._pdf_text(self.t('level'))}:</b> {self._pdf_text(analysis.get('level', '-'))}", normal_style))
        story.append(Paragraph(f"<b>{self._pdf_text(self.t('defender'))}:</b> {self._pdf_text(defender.get('status', '-'))}", normal_style))

        story.append(Paragraph(self._pdf_text(self.t("report_findings")), heading_style))
        if alerts:
            for alert in alerts:
                story.append(Paragraph(f"- {self._pdf_text(alert)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_findings")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_links")), heading_style))
        if links:
            for link in links:
                story.append(Paragraph(f"- {self._pdf_text(link)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_links")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_attachments")), heading_style))
        if attachments:
            for att in attachments:
                name = att.get("name", "")
                size = att.get("size", "")
                tag = self.t("suspicious_tag") if att.get("ext", "") in SUSPICIOUS_EXTENSIONS else ""
                story.append(Paragraph(f"- {self._pdf_text(name)} | {self._pdf_text(size)}{self._pdf_text(tag)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_attachments")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_keywords")), heading_style))
        if keywords:
            for keyword in keywords:
                story.append(Paragraph(f"- {self._pdf_text(keyword)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_keywords")), small_style))

        return story

    def _write_message_pdf(self, item, pdf_path):
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError(self.t("missing_reportlab"))

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title=item.get("subject", APP_NAME) or APP_NAME,
            author=APP_NAME,
        )
        doc.build(self._build_pdf_story(item))

    def export_current_pdf(self):
        item = self._get_current_message()
        if item is None:
            return

        default_name = self._safe_filename(item.get("subject") or os.path.basename(item.get("path", ""))) + ".pdf"
        pdf_path = filedialog.asksaveasfilename(
            title=self.t("save_pdf_title"),
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf")]
        )
        if not pdf_path:
            return

        try:
            self._write_message_pdf(item, pdf_path)
            messagebox.showinfo(self.t("pdf_saved_title"), self.t("pdf_saved_msg"))
        except Exception as exc:
            messagebox.showerror(self.t("pdf_error_title"), str(exc))

    def _open_pdf_file(self, pdf_path):
        if os.name == "nt":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])

    def print_current_message(self):
        item = self._get_current_message()
        if item is None:
            return

        try:
            temp_dir = tempfile.mkdtemp(prefix="mailviewer_print_")
            pdf_path = os.path.join(temp_dir, self._safe_filename(item.get("subject") or "email") + ".pdf")
            self._write_message_pdf(item, pdf_path)

            if os.name == "nt":
                try:
                    os.startfile(pdf_path, "print")
                    self._set_status(self.t("print_started"))
                except OSError as exc:
                    # Windows error 1155 means there is no PDF app associated with the direct Print verb.
                    # In that case, open the PDF normally so the user can print with Ctrl+P.
                    if getattr(exc, "winerror", None) == 1155:
                        self._open_pdf_file(pdf_path)
                        self._set_status(self.t("print_opened_pdf"))
                        messagebox.showinfo(self.t("print_opened_pdf_title"), self.t("print_opened_pdf"))
                    else:
                        raise
            else:
                self._open_pdf_file(pdf_path)
                self._set_status(self.t("print_opened_pdf"))

        except Exception as exc:
            messagebox.showerror(self.t("print_error_title"), str(exc))

    def clear_all(self):
        self.messages.clear()
        self.current_index = None
        self.listbox.delete(0, tk.END)

        for var in [self.file_var, self.type_var, self.subject_var, self.from_var, self.to_var, self.date_var]:
            var.set("")

        self._set_text(self.body_text, "")
        self._set_text(self.alerts_text, "")
        self._set_text(self.links_text, "")
        self._set_text(self.attachments_text, "")
        self._set_text(self.flags_text, "")

        self.risk_label.configure(text=f"{self.t('risk_score')}: -")
        self.level_label.configure(text=f"{self.t('level')}: -")
        self.defender_label.configure(text=f"{self.t('defender')}: -")

        self.top_info_label.configure(text=self.t("hint"))
        self._set_status(self.t("cleared"))

    @staticmethod
    def _extract_urls(text):
        return list(dict.fromkeys(URL_REGEX.findall(text or "")))

    @staticmethod
    def _find_keywords(text):
        text_lower = (text or "").lower()
        return [x for x in SUSPICIOUS_KEYWORDS if x.lower() in text_lower]

    @staticmethod
    def _extract_email(text):
        match = EMAIL_REGEX.search(text or "")
        return match.group(0).lower() if match else ""

    @staticmethod
    def _domain_from_email(email):
        return email.split("@", 1)[1].lower() if "@" in email else ""

    @staticmethod
    def _host_from_url(url):
        cleaned = url.lower().strip()
        cleaned = re.sub(r"^https?://", "", cleaned)
        cleaned = re.sub(r"^www\.", "", cleaned)
        return cleaned.split("/", 1)[0].split(":", 1)[0]

    @staticmethod
    def _parse_email_date(date_str):
        if not date_str:
            return ""
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return date_str

    def _risk_level(self, score):
        if score >= 9:
            return self.t("risk_very_high")
        if score >= 6:
            return self.t("risk_high")
        if score >= 3:
            return self.t("risk_medium")
        return self.t("risk_low")

    @staticmethod
    def _safe_text(value):
        if value is None:
            return ""
        try:
            return str(value).strip()
        except Exception:
            return ""

    @staticmethod
    def _format_date(value):
        if value is None or value == "":
            return ""
        try:
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y %H:%M:%S")
            return str(value)
        except Exception:
            return str(value)


if __name__ == "__main__":
    app = MailViewerApp()
    app.mainloop()
