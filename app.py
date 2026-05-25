# -*- coding: utf-8 -*-
import os
import re
import sys
import html
import tempfile
import subprocess
import hashlib
import shutil
from urllib.parse import urlparse, parse_qsl
import ipaddress
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
    ".zip", ".rar", ".7z", ".cab", ".lnk", ".chm", ".html", ".htm", ".shtml",
    ".svg", ".one", ".xll", ".xlam", ".docm", ".xlsm", ".pptm", ".rtf"
}

MACRO_OFFICE_EXTENSIONS = {".docm", ".xlsm", ".pptm", ".xlam", ".xll"}
HTML_ATTACHMENT_EXTENSIONS = {".html", ".htm", ".shtml", ".svg"}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".cab", ".iso"}
EXECUTABLE_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".scr", ".js", ".jse", ".vbs", ".vbe",
    ".ps1", ".psm1", ".hta", ".msi", ".dll", ".jar", ".reg", ".lnk", ".chm"
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
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "rb.gy", "buff.ly",
    "cutt.ly", "rebrand.ly", "lnkd.in", "s.id", "soo.gd", "shorturl.at", "tiny.cc"
}

TRUST_BRANDS = ["microsoft", "google", "paypal", "amazon", "bank", "apple", "dhl", "acs", "office365", "outlook", "dropbox", "onedrive", "sharepoint", "adobe"]

TRUSTED_BRAND_DOMAINS = {
    "microsoft": {"microsoft.com", "office.com", "office365.com", "live.com", "outlook.com"},
    "office365": {"office.com", "office365.com", "microsoft.com"},
    "outlook": {"outlook.com", "live.com", "office.com", "microsoft.com"},
    "google": {"google.com", "gmail.com", "googleusercontent.com"},
    "paypal": {"paypal.com"},
    "amazon": {"amazon.com", "amazonaws.com"},
    "apple": {"apple.com", "icloud.com"},
    "dhl": {"dhl.com"},
    "dropbox": {"dropbox.com"},
    "onedrive": {"onedrive.live.com", "microsoft.com", "sharepoint.com"},
    "sharepoint": {"sharepoint.com", "microsoft.com"},
    "adobe": {"adobe.com"},
}

IGNORED_URL_DOMAINS = {"w3.org", "www.w3.org"}

CLOUD_STORAGE_DOMAINS = {
    "contabostorage.com", "amazonaws.com", "blob.core.windows.net", "storage.googleapis.com",
    "cloudfront.net", "workers.dev", "pages.dev", "firebaseapp.com", "web.app",
    "github.io", "netlify.app", "vercel.app", "dropbox.com", "box.com", "mega.nz"
}

PHISHING_ACTION_TERMS = [
    "allow messages", "review messages", "release messages", "verify account", "update password",
    "login", "sign in", "password", "mailbox", "webmail", "quarantine", "pending messages",
    "click here", "view message", "open document", "download document",
    "εκκρεμ", "μηνύμα", "ειδοποι", "αποτυχ", "παράδοση", "λογαριασ", "κωδικ",
    "συνδεθ", "επαληθε", "επιβεβα", "άμεση", "αμεσα", "πατήστε εδώ", "πατηστε εδω",
    "κάντε κλικ", "καντε κλικ", "άνοιγμα", "προβολή", "ελέγξτε", "ελεγξτε"
]

URL_REGEX = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', re.IGNORECASE)
DOMAIN_LIKE_REGEX = re.compile(r'(?i)\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b')
DANGEROUS_SCHEMES = {"javascript", "data", "file", "vbscript"}
REDIRECT_PARAM_NAMES = {"url", "u", "uri", "target", "to", "redirect", "redirect_url", "next", "continue", "return", "returnurl", "r", "rurl"}
PUBLIC_EMAIL_DOMAINS = {"gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com", "live.com", "proton.me", "protonmail.com"}
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

# UI readability constants. Keep these centralized so future font tuning does not
# require hunting through the whole interface.
# Compact labels/headings; the readable focus is the content inside text/field boxes.
LABEL_FONT_SIZE = 13
LIST_FONT_SIZE = 13
ENTRY_FONT_SIZE = 15
MESSAGE_BODY_FONT_SIZE = 19
SECURITY_TEXT_FONT_SIZE = 19
TAB_FONT_SIZE = 13
TEXT_BOX_PAD_X = 10
TEXT_BOX_PAD_Y = 8
COMPACT_CONTEXT_FONT_SIZE = 12

TEXTS = {
    "el": {
        "title": "Mail Viewer (.MSG / .EML) & Basic Security Check",
        "open_files": "Άνοιγμα email αρχείων",
        "open_folder": "Άνοιγμα φακέλου",
        "clear": "Καθαρισμός",
        "export_pdf": "Export PDF",
        "open_attachments": "Άνοιγμα συνημμένων",
        "attachment_open_error_title": "Σφάλμα ανοίγματος",
        "attachment_missing_msg": "Το συνημμένο δεν βρέθηκε στο προσωρινό φάκελο.",
        "attachment_none_extractable": "Δεν υπάρχουν διαθέσιμα συνημμένα για άνοιγμα.",
        "attachment_suspicious_title": "Προσοχή",
        "attachment_suspicious_msg": "Το αρχείο έχει ύποπτη κατάληξη: {ext}\n\nΆνοιξέ το μόνο αν εμπιστεύεσαι την προέλευση. Θέλεις να συνεχίσεις;",
        "attachment_folder_opened": "Άνοιξε ο φάκελος συνημμένων.",
        "attachment_file_opened": "Άνοιξε το συνημμένο: {name}",
        "no_message_title": "Δεν υπάρχει επιλεγμένο μήνυμα",
        "no_message_msg": "Επίλεξε πρώτα ένα email από τη λίστα.",
        "save_pdf_title": "Αποθήκευση PDF",
        "pdf_saved_title": "PDF δημιουργήθηκε",
        "pdf_saved_msg": "Το PDF αποθηκεύτηκε επιτυχώς.",
        "pdf_error_title": "Σφάλμα PDF",
        "report_title": "Αναφορά Email",
        "report_security": "Έλεγχος Ασφάλειας",
        "report_findings": "Ευρήματα",
        "report_links": "Links",
        "report_button_links": "Κουμπιά / Clickable Actions",
        "report_clickable_links": "Υπερσύνδεσμοι / Πραγματικά URLs",
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
        "user_guidance_tab": "Τι να κάνω",
        "summary_tab": "Σύνοψη",
        "findings_tab": "Ευρήματα",
        "button_links_tab": "Κουμπιά / Actions",
        "clickable_links_tab": "Υπερσύνδεσμοι",
        "urls_tab": "URLs",
        "attachments_tab": "Συνημμένα",
        "headers_tab": "Headers",
        "keywords_tab": "Keywords",
        "message_body": "Περιεχόμενο μηνύματος",
        "alerts": "Ευρήματα",
        "links": "Links",
        "button_links": "Κουμπιά με σύνδεσμο",
        "clickable_links": "Υπερσύνδεσμοι με σύνδεσμο",
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
        "no_button_links": "(Δεν βρέθηκαν clickable κουμπιά)",
        "no_clickable_links": "(Δεν βρέθηκαν HTML υπερσύνδεσμοι)",
        "no_attachments": "(Δεν υπάρχουν συνημμένα)",
        "no_headers": "(Δεν βρέθηκαν headers)",
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
        "html_link_detected": "Εντοπίστηκε link μέσα σε HTML href/button: {url}",
        "clickable_button_link_detected": "Εντοπίστηκε clickable κουμπί '{label}' που παραπέμπει σε: {url}",
        "clickable_anchor_link_detected": "Εντοπίστηκε υπερσύνδεσμος '{label}' που παραπέμπει σε: {url}",
        "external_link_from_internal_sender": "Ο αποστολέας φαίνεται εσωτερικός ({sender_domain}) αλλά το link οδηγεί σε εξωτερικό domain: {host}",
        "cloud_storage_link": "Link προς cloud/storage hosting που χρησιμοποιείται συχνά για phishing landing pages: {host}",
        "email_in_url_fragment": "Το email του παραλήπτη υπάρχει μέσα στο URL/fragment, πιθανό tracking ή prefill phishing: {url}",
        "whitelisted_suspicious": "Το μήνυμα φαίνεται να πέρασε ως WHITELISTED ενώ περιέχει ύποπτα στοιχεία.",
        "missing_auth_results": "Δεν βρέθηκαν Authentication-Results/SPF/DKIM/DMARC headers στο δείγμα.",
        "mailer_daemon_return_path": "Return-Path MAILER-DAEMON σε κανονικό-looking webmail μήνυμα, ασυνήθιστο μοτίβο.",
        "phishing_action_terms": "Βρέθηκαν όροι/κουμπιά phishing τύπου login, review, allow, release ή pending messages.",
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
        "defender_status_not_available": "Μη διαθέσιμο",
        "defender_status_no_attachments": "Δεν υπάρχουν συνημμένα",
        "defender_status_no_extractable": "Δεν ήταν δυνατή η εξαγωγή συνημμένων",
        "defender_status_clean": "Καθαρό",
        "defender_status_malicious": "Εντοπίστηκε απειλή",
        "defender_status_unknown": "Άγνωστο αποτέλεσμα",
        "defender_status_error": "Σφάλμα",
        "defender_detail": "Λεπτομέρεια Defender",
        "suspicious_attachment_indicator": "ένδειξη ύποπτου συνημμένου",
        "default_button_label": "κουμπί",
        "default_link_label": "σύνδεσμος",
        "source_label": "πηγή",
        "host_label": "host",
        "extension_label": "επέκταση",
        "size_label": "μέγεθος",
        "path_label": "διαδρομή",
        "suspicious_tag": " [ΥΠΟΠΤΟ]",
        "simple_verdict": "Απλή αξιολόγηση",
        "recommended_action": "Προτεινόμενη ενέργεια",
        "do_not_click": "Μην πατήσεις links και μην ανοίξεις συνημμένα μέχρι να το ελέγξει το Γραφείο Πληροφορικής και Δικτύων.",
        "contact_it_now": "Επικοινώνησε με το Γραφείο Πληροφορικής και Δικτύων και στείλε το email για έλεγχο.",
        "contact_it_if_unsure": "Αν δεν το περίμενες ή δεν γνωρίζεις τον αποστολέα, ρώτησε το Γραφείο Πληροφορικής και Δικτύων πριν κάνεις οτιδήποτε.",
        "normal_caution": "Δεν βρέθηκαν ισχυρές ενδείξεις, αλλά άνοιγε links/συνημμένα μόνο αν τα περίμενες και εμπιστεύεσαι τον αποστολέα.",
        "user_verdict_very_high": "ΠΟΛΥ ΥΠΟΠΤΟ: αντιμετώπισέ το σαν πιθανό phishing/malicious email.",
        "user_verdict_high": "ΥΨΗΛΟ ΡΙΣΚΟ: χρειάζεται έλεγχος από το Γραφείο Πληροφορικής και Δικτύων πριν γίνει οποιαδήποτε ενέργεια.",
        "user_verdict_medium": "ΜΕΤΡΙΟ ΡΙΣΚΟ: υπάρχουν ενδείξεις που θέλουν προσοχή.",
        "user_verdict_low": "ΧΑΜΗΛΟ ΡΙΣΚΟ: δεν εντοπίστηκαν εμφανείς ύποπτες ενδείξεις από τον τοπικό έλεγχο.",
        "user_top_reasons": "Κύριοι λόγοι",
        "user_safe_steps": "Απλά βήματα για τον χρήστη",
        "user_step_no_password": "Μην πληκτρολογείς κωδικούς σε σελίδα που άνοιξε από email.",
        "user_step_check_sender": "Έλεγξε αν περίμενες πραγματικά αυτό το email.",
        "user_step_report": "Αν έχεις αμφιβολία, προώθησέ το στο Γραφείο Πληροφορικής και Δικτύων ως ύποπτο.",
        "user_step_clicked": "Αν πάτησες link ή έβαλες κωδικό, ενημέρωσε άμεσα το Γραφείο Πληροφορικής και Δικτύων.",
        "user_not_final_guarantee": "Σημείωση: ο έλεγχος είναι τοπικός και βοηθητικός. Δεν αποτελεί απόλυτη εγγύηση ότι ένα email είναι ασφαλές.",
    },
    "en": {
        "title": "Mail Viewer (.MSG / .EML) & Basic Security Check",
        "open_files": "Open email files",
        "open_folder": "Open folder",
        "clear": "Clear",
        "export_pdf": "Export PDF",
        "open_attachments": "Open attachments",
        "attachment_open_error_title": "Open error",
        "attachment_missing_msg": "The attachment was not found in the temporary folder.",
        "attachment_none_extractable": "No extractable attachments are available to open.",
        "attachment_suspicious_title": "Warning",
        "attachment_suspicious_msg": "This file has a suspicious extension: {ext}\n\nOpen it only if you trust the source. Do you want to continue?",
        "attachment_folder_opened": "Attachments folder opened.",
        "attachment_file_opened": "Opened attachment: {name}",
        "no_message_title": "No message selected",
        "no_message_msg": "Select an email from the list first.",
        "save_pdf_title": "Save PDF",
        "pdf_saved_title": "PDF created",
        "pdf_saved_msg": "The PDF was saved successfully.",
        "pdf_error_title": "PDF error",
        "report_title": "Email Report",
        "report_security": "Security Check",
        "report_findings": "Findings",
        "report_links": "Links",
        "report_button_links": "Buttons / Clickable Actions",
        "report_clickable_links": "Hyperlinks / Real URLs",
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
        "user_guidance_tab": "What should I do?",
        "summary_tab": "Summary",
        "findings_tab": "Findings",
        "button_links_tab": "Buttons / Actions",
        "clickable_links_tab": "Hyperlinks",
        "urls_tab": "URLs",
        "attachments_tab": "Attachments",
        "headers_tab": "Headers",
        "keywords_tab": "Keywords",
        "message_body": "Message body",
        "alerts": "Findings",
        "links": "Links",
        "button_links": "Buttons with links",
        "clickable_links": "Hyperlinks with links",
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
        "no_button_links": "(No clickable buttons found)",
        "no_clickable_links": "(No HTML hyperlinks found)",
        "no_attachments": "(No attachments)",
        "no_headers": "(No headers found)",
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
        "html_link_detected": "Link found inside HTML href/button: {url}",
        "clickable_button_link_detected": "Clickable button '{label}' points to: {url}",
        "clickable_anchor_link_detected": "Hyperlink '{label}' points to: {url}",
        "external_link_from_internal_sender": "Sender appears internal ({sender_domain}) but link points to external domain: {host}",
        "cloud_storage_link": "Link points to cloud/storage hosting often abused for phishing landing pages: {host}",
        "email_in_url_fragment": "Recipient email appears inside the URL/fragment, possible tracking or phishing prefill: {url}",
        "whitelisted_suspicious": "Message appears to have passed as WHITELISTED while containing suspicious indicators.",
        "missing_auth_results": "Authentication-Results/SPF/DKIM/DMARC headers were not found in the sample.",
        "mailer_daemon_return_path": "MAILER-DAEMON Return-Path on a normal-looking webmail message is unusual.",
        "phishing_action_terms": "Phishing action terms/buttons found, such as login, review, allow, release, or pending messages.",
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
        "defender_status_not_available": "Not available",
        "defender_status_no_attachments": "No attachments",
        "defender_status_no_extractable": "No extractable attachments",
        "defender_status_clean": "Clean",
        "defender_status_malicious": "Threat detected",
        "defender_status_unknown": "Unknown result",
        "defender_status_error": "Error",
        "defender_detail": "Defender detail",
        "suspicious_attachment_indicator": "suspicious attachment indicator",
        "default_button_label": "button",
        "default_link_label": "link",
        "source_label": "source",
        "host_label": "host",
        "extension_label": "ext",
        "size_label": "size",
        "path_label": "path",
        "suspicious_tag": " [SUSPICIOUS]",
        "simple_verdict": "Simple verdict",
        "recommended_action": "Recommended action",
        "do_not_click": "Do not click links or open attachments until the Office of Informatics and Networks reviews the email.",
        "contact_it_now": "Contact the Office of Informatics and Networks and submit the email for review.",
        "contact_it_if_unsure": "If you did not expect it or you do not know the sender, ask the Office of Informatics and Networks before doing anything.",
        "normal_caution": "No strong indicators were found, but open links/attachments only if you expected them and trust the sender.",
        "user_verdict_very_high": "HIGHLY SUSPICIOUS: treat it as possible phishing/malicious email.",
        "user_verdict_high": "HIGH RISK: the Office of Informatics and Networks should review it before any action is taken.",
        "user_verdict_medium": "MEDIUM RISK: there are indicators that require caution.",
        "user_verdict_low": "LOW RISK: no obvious suspicious indicators were found by the local check.",
        "user_top_reasons": "Main reasons",
        "user_safe_steps": "Simple user steps",
        "user_step_no_password": "Do not enter passwords on a page opened from an email link.",
        "user_step_check_sender": "Check whether you were actually expecting this email.",
        "user_step_report": "If you are unsure, forward it to the Office of Informatics and Networks as suspicious.",
        "user_step_clicked": "If you clicked a link or entered a password, inform the Office of Informatics and Networks immediately.",
        "user_not_final_guarantee": "Note: this is a local helper check. It is not an absolute guarantee that an email is safe.",
    }
}


# Additional generic security rule labels for the stronger local triage engine.
TEXTS["el"].update({
    "reply_to_mismatch": "Το Reply-To οδηγεί σε διαφορετικό domain από τον αποστολέα: {reply_domain}",
    "return_path_mismatch": "Το Return-Path δεν ταιριάζει με το domain του αποστολέα: {return_domain}",
    "auth_failure": "Τα authentication headers δείχνουν αποτυχία ή soft-fail SPF/DKIM/DMARC.",
    "received_public_ip_internal_sender": "Εσωτερικός-looking αποστολέας με εξωτερική public IP στην αλυσίδα Received: {ip}",
    "link_text_mismatch": "Το εμφανιζόμενο link/κείμενο '{label}' οδηγεί σε διαφορετικό domain: {host}",
    "suspicious_url_scheme": "Clickable στοιχείο χρησιμοποιεί επικίνδυνο ή μη αναμενόμενο URL scheme: {scheme}",
    "url_with_at_symbol": "Το URL περιέχει '@' στο authority τμήμα, πιθανή τεχνική απόκρυψης προορισμού: {url}",
    "punycode_url": "Το domain περιέχει punycode/IDN ένδειξη, πιθανό homograph risk: {host}",
    "excessive_url_encoding": "Το URL περιέχει έντονο percent-encoding/obfuscation: {url}",
    "redirector_url": "Το URL περιέχει redirect parameter που μπορεί να κρύβει τον τελικό προορισμό: {url}",
    "brand_in_untrusted_host": "Brand/υπηρεσία '{brand}' εμφανίζεται σε μη επίσημο domain: {host}",
    "many_link_domains": "Το μήνυμα περιέχει links προς πολλά διαφορετικά domains: {count}",
    "double_extension_attachment": "Συνημμένο με διπλή/παραπλανητική κατάληξη: {name}",
    "macro_attachment": "Συνημμένο Office macro/add-in υψηλότερου κινδύνου: {name}",
    "html_attachment": "HTML/SVG attachment μπορεί να χρησιμοποιηθεί ως phishing landing page: {name}",
    "archive_attachment": "Archive/ISO attachment χρειάζεται προσοχή γιατί μπορεί να κρύβει εκτελέσιμα αρχεία: {name}",
    "short_body_with_links": "Το μήνυμα έχει πολύ λίγο κείμενο αλλά περιέχει links/actions, συχνό σε phishing.",
    "no_plain_text_html_only": "Το μήνυμα φαίνεται HTML-heavy χωρίς ουσιαστικό plain-text περιεχόμενο.",
})

TEXTS["en"].update({
    "reply_to_mismatch": "Reply-To points to a different domain than the sender: {reply_domain}",
    "return_path_mismatch": "Return-Path does not match the sender domain: {return_domain}",
    "auth_failure": "Authentication headers indicate SPF/DKIM/DMARC failure or soft-fail.",
    "received_public_ip_internal_sender": "Internal-looking sender with external public IP in the Received chain: {ip}",
    "link_text_mismatch": "Displayed link/text '{label}' points to a different domain: {host}",
    "suspicious_url_scheme": "Clickable element uses a dangerous or unexpected URL scheme: {scheme}",
    "url_with_at_symbol": "URL contains '@' in the authority section, possible destination hiding: {url}",
    "punycode_url": "Domain contains punycode/IDN marker, possible homograph risk: {host}",
    "excessive_url_encoding": "URL contains heavy percent-encoding/obfuscation: {url}",
    "redirector_url": "URL contains a redirect parameter that may hide the final destination: {url}",
    "brand_in_untrusted_host": "Brand/service '{brand}' appears in a non-official domain: {host}",
    "many_link_domains": "Message contains links to many different domains: {count}",
    "double_extension_attachment": "Attachment has a double/deceptive extension: {name}",
    "macro_attachment": "Office macro/add-in attachment has higher risk: {name}",
    "html_attachment": "HTML/SVG attachment may be used as a phishing landing page: {name}",
    "archive_attachment": "Archive/ISO attachment needs caution because it may hide executable files: {name}",
    "short_body_with_links": "Message has very little text but contains links/actions, common in phishing.",
    "no_plain_text_html_only": "Message appears HTML-heavy without meaningful plain-text content.",
})


class MailViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "el"
        self.messages = []
        self.current_index = None
        self.attachments_temp_dir = tempfile.mkdtemp(prefix="mailviewer_attachments_")

        self.title(TEXTS[self.current_lang]["title"])
        self.geometry("1400x860")
        self.minsize(1100, 720)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=THEME["bg"])
        self._set_window_icon()

        self._build_ui()
        self.apply_language(refresh_current=False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._main_tab_layout_mode = None
        self.after(250, self._watch_main_tab_layout)

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
            font=ctk.CTkFont(size=LABEL_FONT_SIZE, weight="normal"),
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

    def _apply_tabview_font(self, tabview):
        """Keep tab headers compact; readability is handled inside the content panes."""
        try:
            tabview._segmented_button.configure(font=ctk.CTkFont(size=TAB_FONT_SIZE, weight="normal"))
        except Exception:
            # CustomTkinter internals may differ between versions; keep the UI functional.
            pass

    def _value_entry(self, master, textvariable):
        return ctk.CTkEntry(
            master,
            textvariable=textvariable,
            fg_color=THEME["field"],
            border_color=THEME["border"],
            text_color=THEME["text"],
            font=ctk.CTkFont(size=ENTRY_FONT_SIZE, weight="normal"),
            height=38,
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

        self.btn_open_attachments = ctk.CTkButton(
            self.top_card, height=38, corner_radius=10,
            fg_color=THEME["panel_alt"], hover_color=THEME["accent_hover"], text_color=THEME["text"],
            command=self.open_current_attachments
        )
        self.btn_open_attachments.pack(side="left", padx=(0, 8), pady=10)

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
            font=("Segoe UI", LIST_FONT_SIZE),
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

        self.compact_meta_frame = ctk.CTkFrame(
            self.right_card,
            fg_color=THEME["field"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"],
        )
        self.compact_meta_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))
        self.compact_meta_label = ctk.CTkLabel(
            self.compact_meta_frame,
            text="",
            anchor="w",
            justify="left",
            text_color=THEME["text_soft"],
            font=ctk.CTkFont(size=COMPACT_CONTEXT_FONT_SIZE, weight="normal"),
        )
        self.compact_meta_label.pack(fill="x", padx=10, pady=6)
        self.compact_meta_frame.grid_remove()

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
        self._apply_tabview_font(self.tabview)

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
            font=("Segoe UI", MESSAGE_BODY_FONT_SIZE),
            padx=TEXT_BOX_PAD_X,
            pady=TEXT_BOX_PAD_Y,
            spacing1=2,
            spacing3=4,
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

        self.security_tabs = ctk.CTkTabview(
            self.security_tab,
            fg_color=THEME["panel"],
            segmented_button_fg_color=THEME["panel_alt"],
            segmented_button_selected_color=THEME["accent"],
            segmented_button_selected_hover_color=THEME["accent_hover"],
            segmented_button_unselected_color=THEME["panel_alt"],
            segmented_button_unselected_hover_color=THEME["field"],
            text_color=THEME["text"],
            corner_radius=10,
        )
        self.security_tabs.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._apply_tabview_font(self.security_tabs)

        self.security_tab_keys = [
            "user_guidance", "summary", "findings", "button_links", "clickable_links", "urls", "attachments", "headers", "keywords"
        ]
        self.security_tab_label_keys = {
            "user_guidance": "user_guidance_tab",
            "summary": "summary_tab",
            "findings": "findings_tab",
            "button_links": "button_links_tab",
            "clickable_links": "clickable_links_tab",
            "urls": "urls_tab",
            "attachments": "attachments_tab",
            "headers": "headers_tab",
            "keywords": "keywords_tab",
        }

        self.security_subtabs = {}
        self.security_text_widgets = {}
        self.security_title_labels = {}
        for key in self.security_tab_keys:
            label = self.t(self.security_tab_label_keys[key])
            self.security_tabs.add(label)
            tab = self.security_tabs.tab(label)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            self.security_subtabs[key] = tab

            # The tab header already identifies the section. Keep the details panel large
            # and readable by not spending vertical space on duplicate inner headings.
            title = self._label(tab)
            self.security_title_labels[key] = title

            text = self._make_text_box(tab)
            text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
            self.security_text_widgets[key] = text

        # Backward-compatible aliases for older internal calls/tests.
        self.alerts_text = self.security_text_widgets["findings"]
        self.clickable_links_text = self.security_text_widgets["clickable_links"]
        self.links_text = self.security_text_widgets["urls"]
        self.attachments_text = self.security_text_widgets["attachments"]
        self.flags_text = self.security_text_widgets["keywords"]

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
            font=("Segoe UI", SECURITY_TEXT_FONT_SIZE),
            height=8,
            padx=TEXT_BOX_PAD_X,
            pady=TEXT_BOX_PAD_Y,
            spacing1=2,
            spacing3=4,
        )
        return widget

    def _current_main_tab_is_security(self):
        try:
            current = self.tabview.get()
        except Exception:
            return False
        return current in set(self._security_tab_names())

    def _watch_main_tab_layout(self):
        """Adapt the layout when the user enters/leaves Security Check.

        Security mode keeps only a compact message context at the top and gives
        the detailed security panes as much vertical space as possible.
        """
        try:
            self._set_security_layout_mode(self._current_main_tab_is_security())
        finally:
            self.after(250, self._watch_main_tab_layout)

    def _set_security_layout_mode(self, security_mode):
        mode = "security" if security_mode else "message"
        if getattr(self, "_main_tab_layout_mode", None) == mode:
            return
        self._main_tab_layout_mode = mode

        if security_mode:
            self.form_frame.grid_remove()
            self.compact_meta_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 2))
            self.tabview.grid_configure(padx=12, pady=(2, 12))
            self.security_header.grid_configure(padx=8, pady=(2, 2))
            self.security_tabs.grid_configure(padx=8, pady=(0, 8))
            self._update_compact_metadata()
        else:
            self.compact_meta_frame.grid_remove()
            self.form_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
            self.tabview.grid_configure(padx=12, pady=(6, 12))
            self.security_header.grid_configure(padx=8, pady=(8, 6))
            self.security_tabs.grid_configure(padx=8, pady=(0, 8))

    def _update_compact_metadata(self):
        if not hasattr(self, "compact_meta_label"):
            return
        file_value = self.file_var.get().strip()
        file_name = os.path.basename(file_value) if file_value else "-"
        type_value = self.type_var.get().strip() or "-"
        subject_value = self.subject_var.get().strip() or "-"
        from_value = self.from_var.get().strip() or "-"
        to_value = self.to_var.get().strip() or "-"
        date_value = self.date_var.get().strip() or "-"

        text = (
            f"{self.t('file')}: {file_name}    |    {self.t('type')}: {type_value}\n"
            f"{self.t('subject')}: {subject_value}\n"
            f"{self.t('from')}: {from_value}    |    {self.t('to')}: {to_value}    |    {self.t('date')}: {date_value}"
        )
        try:
            width = max(700, self.right_card.winfo_width() - 80)
            self.compact_meta_label.configure(text=text, wraplength=width)
        except Exception:
            self.compact_meta_label.configure(text=text)

    def on_language_change(self, choice):
        self.current_lang = "en" if choice == "English" else "el"
        self._reanalyze_loaded_messages(preserve_defender=True)
        self.apply_language(refresh_current=True)

    def _message_tab_names(self):
        return ["message", TEXTS["el"]["message_tab"], TEXTS["en"]["message_tab"]]

    def _security_tab_names(self):
        return ["security", TEXTS["el"]["security_tab"], TEXTS["en"]["security_tab"]]

    def _security_subtab_names(self, key):
        label_key = self.security_tab_label_keys.get(key, key)
        return [key, TEXTS["el"].get(label_key, key), TEXTS["en"].get(label_key, key)]

    def _security_subtab_key_from_name(self, name):
        for key in getattr(self, "security_tab_keys", []):
            if name in self._security_subtab_names(key):
                return key
        return "summary"

    @staticmethod
    def _existing_tab_name_in(tabview, candidates):
        for name in candidates:
            try:
                tabview.tab(name)
                return name
            except Exception:
                continue
        return None

    @staticmethod
    def _safe_rename_tab_in(tabview, candidates, new_name):
        existing_name = MailViewerApp._existing_tab_name_in(tabview, candidates)
        if existing_name and existing_name != new_name:
            tabview.rename(existing_name, new_name)

    def _safe_set_security_subtab(self, key):
        if not hasattr(self, "security_tabs"):
            return
        label = self.t(self.security_tab_label_keys.get(key, "summary_tab"))
        existing_name = self._existing_tab_name_in(self.security_tabs, [label] + self._security_subtab_names(key))
        if existing_name:
            self.security_tabs.set(existing_name)

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
        previous_security_subtab = None
        try:
            previous_tab = self.tabview.get()
        except Exception:
            previous_tab = None
        try:
            previous_security_subtab = self.security_tabs.get()
        except Exception:
            previous_security_subtab = None

        previous_tab_is_security = previous_tab in set(self._security_tab_names())
        previous_security_subtab_key = self._security_subtab_key_from_name(previous_security_subtab) if previous_security_subtab else "summary"

        self.title(self.t("title"))
        self.btn_open_files.configure(text=self.t("open_files"))
        self.btn_open_folder.configure(text=self.t("open_folder"))
        self.btn_clear.configure(text=self.t("clear"))
        self.btn_export_pdf.configure(text=self.t("export_pdf"))
        self.btn_open_attachments.configure(text=self.t("open_attachments"))
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
        self._update_compact_metadata()

        if hasattr(self, "security_tabs"):
            for key in self.security_tab_keys:
                label_key = self.security_tab_label_keys[key]
                new_label = self.t(label_key)
                self._safe_rename_tab_in(self.security_tabs, self._security_subtab_names(key), new_label)
                if key in self.security_title_labels:
                    self.security_title_labels[key].configure(text=new_label)
            self._safe_set_security_subtab(previous_security_subtab_key)

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

    def _reanalyze_loaded_messages(self, preserve_defender=True):
        """Refresh translated security explanations after language changes.

        Security findings are generated with localized text. When the user switches
        from Greek to English or back, re-run the static heuristic analysis so the
        explanations, risk labels, Defender messages and no-finding messages match
        the selected UI language. Existing Defender results are preserved by default
        to avoid repeatedly scanning attachments just because the language changed.
        """
        for data in self.messages:
            previous_analysis = data.get("analysis", {}) or {}
            previous_defender = previous_analysis.get("defender") if preserve_defender else None
            data["analysis"] = self._analyze_message(
                data.get("subject", ""),
                data.get("sender", ""),
                data.get("to", ""),
                data.get("body", ""),
                data.get("attachments", []) or [],
                data.get("raw_content", ""),
                data.get("headers", {}) or {},
                defender_result_override=previous_defender,
            )

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
                data["subject"], data["sender"], data["to"], data["body"], data["attachments"],
                data.get("raw_content", ""), data.get("headers", {})
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
            "raw_content": "\n".join([self._safe_text(msg.subject), self._safe_text(msg.sender), self._safe_text(msg.to), self._safe_text(getattr(msg, "body", "")), self._safe_text(getattr(msg, "htmlBody", ""))]),
            "headers": {},
            "attachments": self._extract_msg_attachments_info(msg, path),
        }

    def _read_eml(self, path):
        with open(path, "rb") as f:
            eml = BytesParser(policy=policy.default).parse(f)
        headers = self._collect_eml_headers(eml)
        body = self._extract_eml_body(eml)
        raw_content = self._extract_eml_raw_content(eml, headers)
        return {
            "path": path,
            "mail_type": "EML",
            "subject": self._safe_text(eml.get("subject", "")),
            "sender": self._safe_text(eml.get("from", "")),
            "to": self._safe_text(eml.get("to", "")),
            "date": self._format_date(self._parse_email_date(eml.get("date", ""))),
            "body": body,
            "raw_content": raw_content,
            "headers": headers,
            "attachments": self._extract_eml_attachments_info(eml, path),
        }

    def _collect_eml_headers(self, eml):
        headers = {}
        for key, value in eml.items():
            key_l = str(key).lower()
            headers.setdefault(key_l, []).append(self._safe_text(value))
        return headers

    def _extract_eml_raw_content(self, eml, headers):
        parts = []
        for key, values in (headers or {}).items():
            for value in values:
                parts.append(f"{key}: {value}")

        if eml.is_multipart():
            iterator = eml.walk()
        else:
            iterator = [eml]

        for part in iterator:
            content_type = str(part.get_content_type() or "").lower()
            if content_type not in {"text/plain", "text/html"}:
                continue
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
            if payload:
                parts.append(payload)
        return "\n".join(parts)

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

    def _extract_msg_attachments_info(self, msg, mail_path):
        results = []
        for att in getattr(msg, "attachments", []) or []:
            name = (
                self._safe_text(getattr(att, "longFilename", ""))
                or self._safe_text(getattr(att, "filename", ""))
                or self.t("no_name")
            )
            ext = os.path.splitext(name)[1].lower()
            data = getattr(att, "data", None)
            data = data if isinstance(data, (bytes, bytearray)) else None
            saved_path = self._save_attachment_data(mail_path, name, data, len(results) + 1) if data else ""
            size_text = f"{len(data)} bytes" if data else "-"
            results.append({"name": name, "ext": ext, "size": size_text, "data": data, "path": saved_path})
        return results

    def _extract_eml_attachments_info(self, eml, mail_path):
        results = []
        for part in eml.iter_attachments():
            name = self._safe_text(part.get_filename()) or self.t("no_name")
            ext = os.path.splitext(name)[1].lower()
            try:
                raw = part.get_payload(decode=True)
            except Exception:
                raw = None
            raw = raw if isinstance(raw, (bytes, bytearray)) else None
            saved_path = self._save_attachment_data(mail_path, name, raw, len(results) + 1) if raw else ""
            size_text = f"{len(raw)} bytes" if raw else "-"
            results.append({"name": name, "ext": ext, "size": size_text, "data": raw, "path": saved_path})
        return results

    def _attachment_dir_for_message(self, mail_path):
        source_name = self._safe_filename(os.path.splitext(os.path.basename(mail_path))[0] or "email")
        digest = hashlib.sha1(os.path.abspath(mail_path).encode("utf-8", errors="ignore")).hexdigest()[:10]
        folder = os.path.join(self.attachments_temp_dir, f"{source_name}_{digest}")
        os.makedirs(folder, exist_ok=True)
        return folder

    def _save_attachment_data(self, mail_path, filename, data, index):
        if not isinstance(data, (bytes, bytearray)):
            return ""

        folder = self._attachment_dir_for_message(mail_path)
        safe_name = re.sub(r'[\\/:*?"<>|]+', "_", filename or f"attachment_{index}").strip() or f"attachment_{index}"
        base, ext = os.path.splitext(safe_name)
        candidate = os.path.join(folder, safe_name)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(folder, f"{base}_{counter}{ext}")
            counter += 1

        with open(candidate, "wb") as f:
            f.write(data)
        return candidate

    def _open_path_with_default_app(self, path):
        if not path or not os.path.exists(path):
            messagebox.showerror(self.t("attachment_open_error_title"), self.t("attachment_missing_msg"))
            return False

        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True

    def open_current_attachments(self):
        item = self._get_current_message()
        if item is None:
            return

        attachments = item.get("attachments", []) or []
        extractable = [a for a in attachments if a.get("path") and os.path.exists(a.get("path", ""))]
        if not extractable:
            messagebox.showinfo(self.t("attachments"), self.t("attachment_none_extractable"))
            return

        if len(extractable) == 1:
            att = extractable[0]
            ext = (att.get("ext") or os.path.splitext(att.get("path", ""))[1]).lower()
            if ext in SUSPICIOUS_EXTENSIONS:
                proceed = messagebox.askyesno(
                    self.t("attachment_suspicious_title"),
                    self.t("attachment_suspicious_msg", ext=ext or "-")
                )
                if not proceed:
                    return
            if self._open_path_with_default_app(att["path"]):
                self._set_status(self.t("attachment_file_opened", name=att.get("name", "")))
            return

        folder = os.path.dirname(extractable[0]["path"])
        if self._open_path_with_default_app(folder):
            self._set_status(self.t("attachment_folder_opened"))

    def on_close(self):
        try:
            shutil.rmtree(self.attachments_temp_dir, ignore_errors=True)
        finally:
            self.destroy()

    def _analyze_message(self, subject, sender, to_, body, attachments, raw_content="", headers=None, defender_result_override=None):
        """Static local email triage.

        This is intentionally heuristic: it does not visit URLs, does not download payloads,
        and does not replace SPF/DKIM/DMARC validation by the mail gateway. It gives the
        operator explainable indicators that deserve review.
        """
        alerts = []
        score = 0
        headers = headers or {}

        analysis_text = "\n".join([subject or "", sender or "", to_ or "", body or "", raw_content or ""])
        analysis_text_lower = analysis_text.lower()

        links = self._extract_urls(analysis_text)
        button_links = self._extract_clickable_button_links(raw_content or analysis_text)
        anchor_links = self._extract_anchor_links(raw_content or analysis_text)
        for item in button_links + anchor_links:
            url = item.get("url", "")
            if url and re.match(r"^https?://", url, flags=re.IGNORECASE) and url not in links:
                links.append(url)

        display_links = self._extract_urls(body)
        html_only_links = [url for url in links if url not in display_links]
        unique_hosts = sorted({self._host_from_url(url) for url in links if self._host_from_url(url)})

        found_keywords = self._find_keywords(analysis_text)
        sender_email = self._extract_email(sender)
        sender_domain = self._domain_from_email(sender_email)
        sender_text_lower = sender.lower()
        recipient_email = self._extract_email(to_)

        def add_alert(key, points=0, once_key=None, **kwargs):
            nonlocal score
            if once_key is not None:
                if once_key in seen_alerts:
                    return
                seen_alerts.add(once_key)
            alerts.append(self.t(key, **kwargs))
            score += points

        seen_alerts = set()

        # Sender and header consistency checks.
        if not sender.strip():
            add_alert("sender_missing", 2, "sender_missing")

        if sender_domain:
            for brand in TRUST_BRANDS:
                if brand in sender_text_lower and brand not in sender_domain:
                    add_alert("display_name_spoof", 3, f"display_spoof:{brand}", brand=brand, domain=sender_domain)
                    break
            if sender_domain in SHORTENER_DOMAINS:
                add_alert("sender_short_domain", 2, "sender_short_domain", domain=sender_domain)

        reply_to_blob = "\n".join(headers.get("reply-to", []))
        reply_to_email = self._extract_email(reply_to_blob)
        reply_domain = self._domain_from_email(reply_to_email)
        if sender_domain and reply_domain and not self._same_or_subdomain(reply_domain, sender_domain):
            add_alert("reply_to_mismatch", 3, "reply_to_mismatch", reply_domain=reply_domain)

        return_path_blob = "\n".join(headers.get("return-path", []))
        return_email = self._extract_email(return_path_blob)
        return_domain = self._domain_from_email(return_email)
        if sender_domain and return_domain and not self._same_or_subdomain(return_domain, sender_domain):
            # Bounce processors can be legitimate, so this is lower score unless other phishing signs exist.
            points = 2 if self._looks_internal_or_service_sender(sender, sender_domain) else 1
            add_alert("return_path_mismatch", points, "return_path_mismatch", return_domain=return_domain)

        auth_blob = "\n".join(
            value
            for name in ("authentication-results", "received-spf", "dkim-signature")
            for value in headers.get(name, [])
        ).lower()
        if self._auth_headers_show_failure(auth_blob):
            add_alert("auth_failure", 4, "auth_failure")

        public_received_ips = self._extract_public_received_ips(headers)
        if sender_domain and self._looks_internal_or_service_sender(sender, sender_domain) and public_received_ips:
            add_alert("received_public_ip_internal_sender", 2, "received_public_ip", ip=public_received_ips[0])

        # Button/action links are important evidence, but this is generic, not tied to one campaign.
        button_alerts_added = 0
        for button in button_links:
            if button_alerts_added >= 8:
                break
            add_alert(
                "clickable_button_link_detected",
                2,
                f"button:{button.get('label')}:{button.get('url')}",
                label=button.get("label") or "button",
                url=self._defang_url(button.get("url", "")),
            )
            button_alerts_added += 1

        # All HTML anchors are captured as clickable hyperlinks. This is not limited
        # to visually styled buttons: text such as "Πατήστε εδώ" / "click here"
        # must still expose its real href destination to the analyst.
        anchor_alerts_added = 0
        for anchor in anchor_links:
            label = anchor.get("label", "") or "link"
            url = anchor.get("url", "") or ""
            if re.match(r"^https?://", url, flags=re.IGNORECASE) and anchor_alerts_added < 8:
                add_alert(
                    "clickable_anchor_link_detected",
                    1,
                    f"anchor:{label}:{url}",
                    label=label,
                    url=self._defang_url(url),
                )
                anchor_alerts_added += 1
            scheme = self._url_scheme(url)
            if scheme in DANGEROUS_SCHEMES:
                add_alert("suspicious_url_scheme", 4, f"scheme:{scheme}:{label}", scheme=scheme)
                continue
            if not re.match(r"^https?://", url, flags=re.IGNORECASE):
                continue
            host = self._host_from_url(url)
            label_host = self._host_from_display_text(label)
            if label_host and host and not self._same_or_subdomain(host, label_host):
                add_alert(
                    "link_text_mismatch",
                    4,
                    f"label_mismatch:{label_host}:{host}",
                    label=label[:80],
                    host=host,
                )

        html_alerts_added = 0
        external_internal_added = set()
        cloud_added = set()
        email_fragment_added = 0

        for url in links:
            host = self._host_from_url(url)
            if not host:
                continue
            host_l = host.lower()

            if url in html_only_links and html_alerts_added < 4:
                add_alert("html_link_detected", 1, f"html_only:{url}", url=self._defang_url(url))
                html_alerts_added += 1

            if IP_HOST_REGEX.match(host):
                add_alert("ip_link", 3, f"ip_link:{host}", url=self._defang_url(url))
            if host_l in SHORTENER_DOMAINS:
                add_alert("shortened_link", 3, f"shortener:{host_l}", url=self._defang_url(url))

            if sender_domain and not self._same_or_subdomain(host_l, sender_domain):
                key = (sender_domain, host_l)
                if key not in external_internal_added and self._looks_internal_or_service_sender(sender, sender_domain):
                    add_alert("external_link_from_internal_sender", 4, f"external_from_internal:{sender_domain}:{host_l}", sender_domain=sender_domain, host=host_l)
                    external_internal_added.add(key)

            if self._is_cloud_storage_host(host_l) and host_l not in cloud_added:
                add_alert("cloud_storage_link", 3, f"cloud:{host_l}", host=host_l)
                cloud_added.add(host_l)

            if recipient_email and recipient_email.lower() in html.unescape(url).lower() and email_fragment_added < 3:
                add_alert("email_in_url_fragment", 3, f"email_in_url:{url}", url=self._defang_url(url))
                email_fragment_added += 1

            if self._url_has_authority_at_symbol(url):
                add_alert("url_with_at_symbol", 4, f"url_at:{url}", url=self._defang_url(url))

            if host_l.startswith("xn--") or ".xn--" in host_l:
                add_alert("punycode_url", 3, f"punycode:{host_l}", host=host_l)

            if self._has_excessive_url_encoding(url):
                add_alert("excessive_url_encoding", 2, f"encoding:{url}", url=self._defang_url(url))

            if self._looks_like_redirector_url(url):
                add_alert("redirector_url", 2, f"redirector:{url}", url=self._defang_url(url))

            for brand in TRUST_BRANDS:
                if self._brand_appears_in_untrusted_host(host_l, brand):
                    add_alert("brand_in_untrusted_host", 3, f"brand_host:{brand}:{host_l}", brand=brand, host=host_l)
                    break

            for brand in TRUST_BRANDS:
                if brand in analysis_text_lower and brand not in host_l and any(x in url.lower() for x in ["login", "verify", "secure", "account", "update", "review", "signin", "password"]):
                    add_alert("brand_mismatch_link", 2, f"brand_mismatch:{brand}:{host_l}", url=self._defang_url(url))
                    break

        if len(unique_hosts) >= 4:
            add_alert("many_link_domains", 1, "many_link_domains", count=len(unique_hosts))

        suspicious_attachments = []
        for att in attachments:
            name = str(att.get("name", ""))
            ext = str(att.get("ext", "")).lower()
            name_l = name.lower()

            if ext in SUSPICIOUS_EXTENSIONS:
                suspicious_attachments.append(name)
                add_alert("suspicious_attachment", 3, f"suspicious_attachment:{name}", name=name)
            if self._has_double_extension(name_l):
                add_alert("double_extension_attachment", 4, f"double_ext:{name}", name=name)
            if ext in MACRO_OFFICE_EXTENSIONS:
                add_alert("macro_attachment", 4, f"macro:{name}", name=name)
            if ext in HTML_ATTACHMENT_EXTENSIONS:
                add_alert("html_attachment", 3, f"html_att:{name}", name=name)
            if ext in ARCHIVE_EXTENSIONS:
                add_alert("archive_attachment", 2, f"archive:{name}", name=name)

        if len(links) >= 3:
            add_alert("many_links", 1, "many_links", count=len(links))

        visible_body_text = self._strip_html_to_text(body)
        if links and len(visible_body_text) < 80:
            add_alert("short_body_with_links", 2, "short_body_with_links")
        if raw_content and links and len(visible_body_text) < max(40, len(raw_content) * 0.02):
            add_alert("no_plain_text_html_only", 1, "html_heavy")

        if found_keywords:
            add_alert("found_keywords", min(3, len(found_keywords)), "found_keywords")

        if any(term in analysis_text_lower for term in PHISHING_ACTION_TERMS):
            add_alert("phishing_action_terms", 3, "phishing_action_terms")

        if self._header_contains(headers, "x-spam-status", "whitelisted") and (links or found_keywords or button_links):
            add_alert("whitelisted_suspicious", 3, "whitelisted_suspicious")

        if not self._has_any_header(headers, ["authentication-results", "received-spf", "dkim-signature"]):
            add_alert("missing_auth_results", 1, "missing_auth_results")

        return_paths = "\n".join(headers.get("return-path", []))
        if "mailer-daemon" in return_paths.lower() and any(x in analysis_text_lower for x in ["webmail", "allow messages", "review messages", "εκκρεμ", "μηνύμα", "mailbox", "quarantine"]):
            add_alert("mailer_daemon_return_path", 2, "mailer_daemon_return_path")

        if subject and subject.isupper() and len(subject) > 8:
            add_alert("uppercase_subject", 1, "uppercase_subject")

        defender_result = self._localized_defender_result(defender_result_override) if defender_result_override else self._scan_attachments_with_defender(attachments)
        if defender_result["status"] == "malicious":
            add_alert("defender_detected", 6, "defender_detected")
        elif defender_result["status"] == "error":
            add_alert("defender_error", 1, "defender_error", msg=defender_result["message"])

        return {
            "score": score,
            "level": self._risk_level(score),
            "alerts": alerts or [self.t("no_findings")],
            "links": links,
            "button_links": button_links,
            "anchor_links": anchor_links,
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


    def _localized_defender_result(self, defender_result):
        """Return a Defender result whose known status/message are localized for the current UI language.

        The scan itself is not repeated when the user changes language. Only the display
        text for stable internal statuses is regenerated, so English UI does not retain
        Greek Defender messages such as "Δεν υπάρχουν συνημμένα".
        """
        result = dict(defender_result or {})
        status = str(result.get("status", "") or "unknown").strip()

        # Backward compatibility with older builds that stored localized status text.
        reverse_status = {
            TEXTS["el"].get("status_not_available", "not_available"): "not_available",
            TEXTS["en"].get("status_not_available", "not_available"): "not_available",
        }
        status = reverse_status.get(status, status)
        if status not in {
            "not_available", "no_attachments", "no_extractable", "clean",
            "malicious", "unknown", "error"
        }:
            status = status or "unknown"
        result["status"] = status

        message_key_by_status = {
            "not_available": "status_defender_not_found",
            "no_attachments": "status_no_attachments",
            "no_extractable": "status_no_extractable",
            "clean": "status_clean",
        }
        if status in message_key_by_status:
            result["message"] = self.t(message_key_by_status[status])
        elif status == "error":
            old_message = str(result.get("message", "") or "")
            timeout_messages = {TEXTS["el"].get("status_timeout", ""), TEXTS["en"].get("status_timeout", "")}
            if old_message in timeout_messages:
                result["message"] = self.t("status_timeout")
            else:
                result["message"] = old_message
        else:
            result["message"] = str(result.get("message", "") or "")
        return result

    def _defender_status_display(self, defender_result):
        status = str((defender_result or {}).get("status", "") or "unknown")
        key = {
            "not_available": "defender_status_not_available",
            "no_attachments": "defender_status_no_attachments",
            "no_extractable": "defender_status_no_extractable",
            "clean": "defender_status_clean",
            "malicious": "defender_status_malicious",
            "unknown": "defender_status_unknown",
            "error": "defender_status_error",
        }.get(status, "defender_status_unknown")
        return self.t(key)

    def _defender_message_display(self, defender_result):
        return self._localized_defender_result(defender_result).get("message", "")

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
        self._update_compact_metadata()

        self._set_text(self.body_text, item["body"])
        self._populate_security(item)
        self._set_status(self.t("showing_message", index=index + 1, total=len(self.messages)))

    def _build_user_guidance(self, score, analysis, attachments):
        """Build a plain-language action panel for non-technical users.

        The detailed tabs still exist for Office of Informatics and Networks / SOC review, but this panel answers the
        employee's immediate question: "Can I interact with this email or should I ask the Office of Informatics and Networks?"
        """
        try:
            numeric_score = int(score)
        except Exception:
            numeric_score = 0

        if numeric_score >= 9:
            verdict = self.t("user_verdict_very_high")
            action = self.t("contact_it_now")
        elif numeric_score >= 6:
            verdict = self.t("user_verdict_high")
            action = self.t("contact_it_now")
        elif numeric_score >= 3:
            verdict = self.t("user_verdict_medium")
            action = self.t("contact_it_if_unsure")
        else:
            verdict = self.t("user_verdict_low")
            action = self.t("normal_caution")

        alerts = [a for a in (analysis.get("alerts", []) or []) if a and a != self.t("no_findings")]
        links = analysis.get("links", []) or []
        button_links = analysis.get("button_links", []) or []
        anchor_links = analysis.get("anchor_links", []) or []
        suspicious_attachments = set(analysis.get("suspicious_attachments", []) or [])
        has_suspicious_attachment = any(
            (att.get("ext", "").lower() in SUSPICIOUS_EXTENSIONS) or (att.get("name", "") in suspicious_attachments)
            for att in (attachments or [])
        )

        lines = [
            f"{self.t('simple_verdict')}: {verdict}",
            f"{self.t('recommended_action')}: {action}",
            "",
            self.t("do_not_click") if numeric_score >= 6 else self.t("normal_caution"),
        ]

        reasons = []
        if button_links or anchor_links:
            reasons.append(f"- {self.t('clickable_links_tab')}: {len(button_links) + len(anchor_links)}")
        if links:
            reasons.append(f"- {self.t('urls_tab')}: {len(links)}")
        if has_suspicious_attachment:
            reasons.append(f"- {self.t('attachments_tab')}: {self.t('suspicious_attachment_indicator')}")
        for alert in alerts[:4]:
            reasons.append(f"- {alert}")

        if reasons:
            lines.extend(["", f"{self.t('user_top_reasons')}:" ])
            lines.extend(reasons[:7])

        lines.extend([
            "",
            f"{self.t('user_safe_steps')}:",
            f"1. {self.t('user_step_no_password')}",
            f"2. {self.t('user_step_check_sender')}",
            f"3. {self.t('user_step_report')}",
            f"4. {self.t('user_step_clicked')}",
            "",
            self.t("user_not_final_guarantee"),
        ])
        return lines

    def _populate_security(self, item):
        attachments = item.get("attachments", []) or []
        analysis = item.get("analysis", {}) or {}
        headers = item.get("headers", {}) or {}

        score = analysis.get("score", "-")
        level = analysis.get("level", "-")
        defender = analysis.get("defender", {}) or {}
        defender_status = self._defender_status_display(defender)
        defender_message = self._defender_message_display(defender)

        self.risk_label.configure(text=f"{self.t('risk_score')}: {score}/10+")
        self.level_label.configure(text=f"{self.t('level')}: {level}")
        self.defender_label.configure(text=f"{self.t('defender')}: {defender_status}")

        button_links = analysis.get("button_links", []) or []
        anchor_links = analysis.get("anchor_links", []) or []
        links = analysis.get("links", []) or []
        alerts = analysis.get("alerts", []) or []
        keywords = analysis.get("keywords", []) or []
        suspicious_attachments = set(analysis.get("suspicious_attachments", []) or [])

        user_guidance_lines = self._build_user_guidance(score, analysis, attachments)
        self._set_text(self.security_text_widgets["user_guidance"], "\n".join(user_guidance_lines))

        summary_lines = [
            f"{self.t('risk_score')}: {score}/10+",
            f"{self.t('level')}: {level}",
            f"{self.t('defender')}: {defender_status}",
            "",
            f"{self.t('user_guidance_tab')}: {user_guidance_lines[0] if user_guidance_lines else '-'}",
            "",
            f"{self.t('findings_tab')}: {len(alerts)}",
            f"{self.t('button_links_tab')}: {len(button_links)}",
            f"{self.t('clickable_links_tab')}: {len(anchor_links)}",
            f"{self.t('urls_tab')}: {len(links)}",
            f"{self.t('attachments_tab')}: {len(attachments)}",
            f"{self.t('keywords_tab')}: {len(keywords)}",
        ]
        if defender_message:
            summary_lines.extend(["", f"{self.t('defender_detail')}: {defender_message}"])
        self._set_text(self.security_text_widgets["summary"], "\n".join(summary_lines))

        findings_text = "\n".join(f"- {x}" for x in alerts) if alerts else self.t("no_findings")
        self._set_text(self.security_text_widgets["findings"], findings_text)

        if button_links:
            button_lines = []
            for button in button_links:
                label = button.get("label") or self.t("default_button_label")
                source = button.get("source") or ""
                url = self._defang_url(button.get("url", ""))
                suffix = f" [{self.t('source_label')}: {source}]" if source else ""
                button_lines.append(f"- {label}{suffix}\n  -> {url}")
            self._set_text(self.security_text_widgets["button_links"], "\n\n".join(button_lines))
        else:
            self._set_text(self.security_text_widgets["button_links"], self.t("no_button_links"))

        if anchor_links:
            anchor_lines = []
            for anchor in anchor_links:
                label = anchor.get("label") or self.t("default_link_label")
                source = anchor.get("source") or ""
                url_raw = anchor.get("url", "")
                url = self._defang_url(url_raw)
                host = self._host_from_url(url_raw)
                suffix = f" [{self.t('source_label')}: {source}]" if source else ""
                host_part = f" | {self.t('host_label')}: {host}" if host else ""
                anchor_lines.append(f"- {label}{suffix}{host_part}\n  -> {url}")
            self._set_text(self.security_text_widgets["clickable_links"], "\n\n".join(anchor_lines))
        else:
            self._set_text(self.security_text_widgets["clickable_links"], self.t("no_clickable_links"))

        if links:
            url_lines = []
            for link in links:
                host = self._host_from_url(link)
                host_part = f" [{self.t('host_label')}: {host}]" if host else ""
                url_lines.append(f"- {self._defang_url(link)}{host_part}")
            self._set_text(self.security_text_widgets["urls"], "\n".join(url_lines))
        else:
            self._set_text(self.security_text_widgets["urls"], self.t("no_links"))

        if attachments:
            lines = []
            for att in attachments:
                name = att.get("name", "")
                size = att.get("size", "")
                ext = att.get("ext", "") or "-"
                tag = self.t("suspicious_tag") if ext in SUSPICIOUS_EXTENSIONS or name in suspicious_attachments else ""
                path = att.get("path", "")
                path_part = f" | {self.t('path_label')}: {path}" if path else ""
                lines.append(f"- {name} | {self.t('extension_label')}: {ext} | {self.t('size_label')}: {size}{tag}{path_part}")
            self._set_text(self.security_text_widgets["attachments"], "\n".join(lines))
        else:
            self._set_text(self.security_text_widgets["attachments"], self.t("no_attachments"))

        if headers:
            header_lines = []
            for key, values in headers.items():
                for value in values:
                    header_lines.append(f"{key}: {value}")
            self._set_text(self.security_text_widgets["headers"], "\n".join(header_lines))
        else:
            self._set_text(self.security_text_widgets["headers"], self.t("no_headers"))

        self._set_text(
            self.security_text_widgets["keywords"],
            "\n".join(f"- {x}" for x in keywords) if keywords else self.t("no_keywords")
        )

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
        button_links = analysis.get("button_links", []) or []
        anchor_links = analysis.get("anchor_links", []) or []
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
        story.append(Paragraph(f"<b>{self._pdf_text(self.t('defender'))}:</b> {self._pdf_text(self._defender_status_display(defender))}", normal_style))
        defender_message = self._defender_message_display(defender)
        if defender_message:
            story.append(Paragraph(f"<b>{self._pdf_text(self.t('defender_detail'))}:</b> {self._pdf_text(defender_message)}", normal_style))

        story.append(Paragraph(self._pdf_text(self.t("report_findings")), heading_style))
        if alerts:
            for alert in alerts:
                story.append(Paragraph(f"- {self._pdf_text(alert)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_findings")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_button_links")), heading_style))
        if button_links:
            for button in button_links:
                label = button.get("label") or self.t("default_button_label")
                url = self._defang_url(button.get("url", ""))
                story.append(Paragraph(f"- {self._pdf_text(label)} -> {self._pdf_text(url)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_button_links")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_clickable_links")), heading_style))
        if anchor_links:
            for anchor in anchor_links:
                label = anchor.get("label") or self.t("default_link_label")
                url = self._defang_url(anchor.get("url", ""))
                story.append(Paragraph(f"- {self._pdf_text(label)} -> {self._pdf_text(url)}", small_style))
        else:
            story.append(Paragraph(self._pdf_text(self.t("no_clickable_links")), small_style))

        story.append(Paragraph(self._pdf_text(self.t("report_links")), heading_style))
        if links:
            for link in links:
                story.append(Paragraph(f"- {self._pdf_text(self._defang_url(link))}", small_style))
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

    def clear_all(self):
        self.messages.clear()
        self.current_index = None
        self.listbox.delete(0, tk.END)

        for var in [self.file_var, self.type_var, self.subject_var, self.from_var, self.to_var, self.date_var]:
            var.set("")
        self._update_compact_metadata()

        self._set_text(self.body_text, "")
        for widget in getattr(self, "security_text_widgets", {}).values():
            self._set_text(widget, "")

        self.risk_label.configure(text=f"{self.t('risk_score')}: -")
        self.level_label.configure(text=f"{self.t('level')}: -")
        self.defender_label.configure(text=f"{self.t('defender')}: -")

        self.top_info_label.configure(text=self.t("hint"))
        self._set_status(self.t("cleared"))

    @staticmethod
    def _extract_urls(text):
        text = html.unescape(text or "")
        results = []
        for match in URL_REGEX.findall(text):
            url = str(match).strip()
            url = url.rstrip(".,;:)>]}")
            if url.lower().startswith("www."):
                url = "http://" + url
            host = MailViewerApp._host_from_url(url)
            if host in IGNORED_URL_DOMAINS or any(host.endswith("." + d) for d in IGNORED_URL_DOMAINS):
                continue
            if url and url not in results:
                results.append(url)
        return results

    @staticmethod
    def _strip_html_to_text(value):
        value = html.unescape(value or "")
        value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
        value = re.sub(r"(?is)<br\s*/?>", " ", value)
        value = re.sub(r"(?is)</p\s*>", " ", value)
        value = re.sub(r"(?is)<[^>]+>", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    @staticmethod
    def _normalize_url(value):
        url = html.unescape(value or "").strip()
        url = url.rstrip(".,;:)>]}")
        if url.lower().startswith("www."):
            url = "http://" + url
        return url

    @staticmethod
    def _defang_url(url):
        url = str(url or "")
        url = url.replace("https://", "hxxps://").replace("http://", "hxxp://")
        return url.replace(".", "[.]")

    @staticmethod
    def _html_attr_value(tag, attr_name):
        pattern = rf"\b{re.escape(attr_name)}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))"
        match = re.search(pattern, tag or "", flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return html.unescape(next((g for g in match.groups() if g is not None), "")).strip()

    @staticmethod
    def _looks_like_clickable_button(anchor_tag, label):
        tag_l = (anchor_tag or "").lower()
        label_l = (label or "").lower()
        button_markers = [
            "button", "btn", "border-radius", "background-color", "display: inline-block",
            "padding:", "call-to-action", "cta", "mso-", "v:roundrect"
        ]
        action_markers = [term.lower() for term in PHISHING_ACTION_TERMS]
        return any(marker in tag_l for marker in button_markers) or any(marker in label_l for marker in action_markers)

    @staticmethod
    def _extract_clickable_button_links(raw_html):
        """Return visible clickable button/action links without visiting them.

        The function focuses on HTML anchors/forms/buttons that visually or semantically
        behave like action buttons. URLs are kept raw internally; UI/PDF output defangs them.
        """
        raw_html = html.unescape(raw_html or "")
        results = []
        seen = set()

        def add_button(label, url, source):
            url = MailViewerApp._normalize_url(url)
            if not url or not re.match(r"^https?://", url, flags=re.IGNORECASE):
                return
            host = MailViewerApp._host_from_url(url)
            if host in IGNORED_URL_DOMAINS or any(host.endswith("." + d) for d in IGNORED_URL_DOMAINS):
                return
            label = MailViewerApp._strip_html_to_text(label) or source or "button"
            key = (label.lower(), url)
            if key in seen:
                return
            seen.add(key)
            results.append({"label": label[:120], "url": url, "source": source})

        for match in re.finditer(r"(?is)<a\b([^>]*)>(.*?)</a>", raw_html):
            attrs, inner = match.group(1), match.group(2)
            href = MailViewerApp._html_attr_value(attrs, "href")
            label = MailViewerApp._strip_html_to_text(inner)
            if href and MailViewerApp._looks_like_clickable_button(attrs + " " + inner, label):
                add_button(label, href, "html_anchor")

        for match in re.finditer(r"(?is)<form\b([^>]*)>(.*?)</form>", raw_html):
            attrs, inner = match.group(1), match.group(2)
            action = MailViewerApp._html_attr_value(attrs, "action")
            button_match = re.search(r"(?is)<button\b[^>]*>(.*?)</button>|<input\b[^>]*\bvalue\s*=\s*(['\"])(.*?)\2", inner)
            label = ""
            if button_match:
                label = button_match.group(1) or button_match.group(3) or "form button"
            if action:
                add_button(label, action, "html_form")

        for match in re.finditer(r"(?is)<button\b([^>]*)>(.*?)</button>", raw_html):
            attrs, inner = match.group(1), match.group(2)
            label = MailViewerApp._strip_html_to_text(inner) or "button"
            onclick = MailViewerApp._html_attr_value(attrs, "onclick")
            if onclick:
                url_match = URL_REGEX.search(onclick)
                if url_match:
                    add_button(label, url_match.group(0), "button_onclick")

        return results

    @staticmethod
    def _extract_anchor_links(raw_html):
        """Extract all HTML anchor destinations without visiting them."""
        raw_html = html.unescape(raw_html or "")
        results = []
        seen = set()
        for match in re.finditer(r"(?is)<a\b([^>]*)>(.*?)</a>", raw_html):
            attrs, inner = match.group(1), match.group(2)
            href = MailViewerApp._html_attr_value(attrs, "href")
            if not href:
                continue
            label = MailViewerApp._strip_html_to_text(inner) or "link"
            url = MailViewerApp._normalize_url(href)
            key = (label.lower(), url.lower())
            if key in seen:
                continue
            seen.add(key)
            results.append({"label": label[:160], "url": url, "source": "html_anchor"})
        return results

    @staticmethod
    def _url_scheme(url):
        value = html.unescape(url or "").strip()
        match = re.match(r"^([a-z][a-z0-9+.-]*):", value, flags=re.IGNORECASE)
        return match.group(1).lower() if match else ""

    @staticmethod
    def _host_from_display_text(text):
        value = MailViewerApp._strip_html_to_text(text)
        if not value:
            return ""
        # If the visible text is a URL or a naked domain, extract the displayed host.
        url_match = URL_REGEX.search(value)
        if url_match:
            return MailViewerApp._host_from_url(url_match.group(0))
        domain_match = DOMAIN_LIKE_REGEX.search(value)
        if domain_match:
            return MailViewerApp._host_from_url("http://" + domain_match.group(0))
        return ""

    @staticmethod
    def _url_has_authority_at_symbol(url):
        try:
            parsed = urlparse(html.unescape(url or ""))
            return "@" in (parsed.netloc or "")
        except Exception:
            return False

    @staticmethod
    def _has_excessive_url_encoding(url):
        value = html.unescape(url or "")
        enc_count = len(re.findall(r"%[0-9a-fA-F]{2}", value))
        return enc_count >= 5 or any(token in value.lower() for token in ["%2f%2f", "%252f", "%253a"])

    @staticmethod
    def _looks_like_redirector_url(url):
        try:
            parsed = urlparse(html.unescape(url or ""))
            query_items = parse_qsl(parsed.query, keep_blank_values=True)
        except Exception:
            return False
        for key, value in query_items:
            key_l = (key or "").lower()
            value_l = (value or "").lower()
            if key_l in REDIRECT_PARAM_NAMES and ("http://" in value_l or "https://" in value_l or "%2f" in value_l):
                return True
        return False

    @staticmethod
    def _brand_appears_in_untrusted_host(host, brand):
        host = (host or "").lower()
        brand = (brand or "").lower()
        if not host or not brand or brand not in host:
            return False
        trusted_domains = TRUSTED_BRAND_DOMAINS.get(brand, set())
        if any(MailViewerApp._same_or_subdomain(host, trusted) for trusted in trusted_domains):
            return False
        # Avoid extremely broad false positives for generic words.
        if brand in {"bank", "mail", "webmail"} and not any(x in host for x in ["login", "verify", "secure", "account", "webmail", "mail"]):
            return False
        return True

    @staticmethod
    def _auth_headers_show_failure(auth_blob):
        value = (auth_blob or "").lower()
        failure_markers = [
            "spf=fail", "spf=softfail", "spf=neutral",
            "dkim=fail", "dkim=neutral", "dkim=temperror", "dkim=permerror",
            "dmarc=fail", "dmarc=quarantine", "dmarc=reject",
            "compauth=fail", "reason=fail",
        ]
        return any(marker in value for marker in failure_markers)

    @staticmethod
    def _extract_public_received_ips(headers):
        received_values = headers.get("received", []) if headers else []
        ips = []
        for value in received_values:
            for candidate in re.findall(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)", str(value)):
                try:
                    ip = ipaddress.ip_address(candidate)
                    if ip.is_global and candidate not in ips:
                        ips.append(candidate)
                except Exception:
                    continue
        return ips

    @staticmethod
    def _has_double_extension(filename):
        name = (filename or "").lower().strip()
        parts = [p for p in name.split(".") if p]
        if len(parts) < 3:
            return False
        last_ext = "." + parts[-1]
        previous_ext = "." + parts[-2]
        document_like = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".txt"}
        return previous_ext in document_like and last_ext in EXECUTABLE_EXTENSIONS

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
        cleaned = html.unescape(url or "").strip()
        if cleaned.lower().startswith("www."):
            cleaned = "http://" + cleaned
        try:
            parsed = urlparse(cleaned)
            host = parsed.hostname or ""
        except Exception:
            cleaned_l = cleaned.lower()
            cleaned_l = re.sub(r"^https?://", "", cleaned_l)
            cleaned_l = re.sub(r"^www\.", "", cleaned_l)
            host = cleaned_l.split("/", 1)[0].split(":", 1)[0]
        host = (host or "").lower()
        return host[4:] if host.startswith("www.") else host

    @staticmethod
    def _same_or_subdomain(host, domain):
        host = (host or "").lower()
        domain = (domain or "").lower()
        host = host[4:] if host.startswith("www.") else host
        domain = domain[4:] if domain.startswith("www.") else domain
        return bool(host and domain and (host == domain or host.endswith("." + domain)))

    @staticmethod
    def _is_cloud_storage_host(host):
        host = (host or "").lower()
        host = host[4:] if host.startswith("www.") else host
        return any(host == domain or host.endswith("." + domain) for domain in CLOUD_STORAGE_DOMAINS)

    @staticmethod
    def _looks_internal_or_service_sender(sender, sender_domain):
        sender_l = (sender or "").lower()
        domain_l = (sender_domain or "").lower()
        service_words = [
            "webmail", "mail", "admin", "administrator", "support", "helpdesk", "security",
            "it", "system", "service", "noreply", "no-reply", "postmaster", "mailer-daemon"
        ]
        if not domain_l or domain_l in PUBLIC_EMAIL_DOMAINS:
            return False
        return any(word in sender_l for word in service_words)

    @staticmethod
    def _has_any_header(headers, names):
        return any(name.lower() in headers and headers.get(name.lower()) for name in names)

    @staticmethod
    def _header_contains(headers, name, needle):
        values = headers.get(name.lower(), []) if headers else []
        return any(needle.lower() in str(value).lower() for value in values)

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
