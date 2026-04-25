# 📧 MailViewer

Απλό, γρήγορο και ελαφρύ εργαλείο για άνοιγμα και προβολή αρχείων email (`.msg`, `.eml`) με ενσωματωμένο basic security check και υποστήριξη Ελληνικών.

Simple, fast and lightweight tool for opening and viewing email files (`.msg`, `.eml`) with basic security checks and Greek language support.

---

## ✨ Features / Χαρακτηριστικά

### 🇬🇷 Ελληνικά
- Άνοιγμα αρχείων:
  - `.msg` (Outlook)
  - `.eml` (standard email)
- Άνοιγμα ολόκληρου φακέλου με email αρχεία
- Καθαρή προβολή:
  - Αποστολέας
  - Παραλήπτης
  - Θέμα
  - Ημερομηνία
  - Περιεχόμενο
- Basic security check:
  - Έλεγχος για ύποπτα patterns, links, keywords και συνημμένα
- Export του επιλεγμένου email σε PDF
- Εκτύπωση του επιλεγμένου email
- Διγλωσσικό UI:
  - Ελληνικά / English
- Σύγχρονο dark theme με customtkinter
- Portable executable χωρίς εγκατάσταση

---

### 🇬🇧 English
- Open email files:
  - `.msg` (Outlook)
  - `.eml` (standard email)
- Open a full folder containing email files
- Clean display:
  - Sender
  - Recipient
  - Subject
  - Date
  - Message body
- Basic security check:
  - Detection of suspicious patterns, links, keywords and attachments
- Export selected email to PDF
- Print selected email
- Bilingual UI:
  - Greek / English
- Modern dark theme with customtkinter
- Portable executable without installation

---

## 🚀 Usage / Χρήση

### 🇬🇷
1. Άνοιξε το πρόγραμμα
2. Πάτα **Άνοιγμα email αρχείων** ή **Άνοιγμα φακέλου**
3. Επίλεξε `.msg` ή `.eml`
4. Δες το περιεχόμενο και το security check
5. Πάτα **Export PDF** για αποθήκευση σε PDF
6. Πάτα **Εκτύπωση** για εκτύπωση του επιλεγμένου email

---

### 🇬🇧
1. Launch the application
2. Click **Open email files** or **Open folder**
3. Select `.msg` or `.eml`
4. View the content and security check
5. Click **Export PDF** to save as PDF
6. Click **Print** to print the selected email

---

## 📦 Download / Λήψη

Από το GitHub Releases:

- `MailViewer.exe` → portable έκδοση

---

## 🛠 Requirements / Απαιτήσεις για run από source

```bash
pip install -r requirements.txt
python app.py
```

---

## 🧱 Build EXE

```bat
build_exe.bat
```

Το τελικό αρχείο δημιουργείται στο:

```text
dist\MailViewer.exe
```
