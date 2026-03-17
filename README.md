# Mail Viewer (.MSG / .EML) with Basic Security Check  
# Προβολέας Email (.MSG / .EML) με Βασικό Έλεγχο Ασφάλειας

---

## English

### Overview
This project is a simple desktop application built with Python and Tkinter for viewing email files in **`.msg`** and **`.eml`** format.

It is designed to:
- open and preview email files
- display core fields such as subject, sender, recipient, date, and body
- inspect attachments
- perform a **basic security check** for suspicious indicators

This tool is useful for quick manual review of email samples, especially in environments where emails are often exchanged in **Greek** but English compatibility is also required.

---

### Features
- View **`.msg`** files (Microsoft Outlook format)
- View **`.eml`** files (standard email format)
- Display:
  - file path
  - file type
  - subject
  - sender
  - recipient
  - date
  - message body
- Show attachments
- Basic security analysis:
  - suspicious attachment extensions
  - suspicious links
  - phishing-related keywords
  - possible sender spoofing indicators
- Optional **Windows Defender** scan for extracted attachments when running on Windows

---

### Supported Formats
Currently supported:
- `.msg`
- `.eml`

Planned / possible future support:
- `.emlx`
- `.mbox`
- `.pst`

---

### Requirements
- Python 3.10+ recommended
- `extract_msg` library for `.msg` support

Install dependencies:

```bash
pip install extract_msg
```

For Windows executable build:

```bash
pip install pyinstaller
```

---

### Run on macOS

```bash
python3 mail_viewer_msg_eml_security.py
```

---

### Run on Windows

```bash
python mail_viewer_msg_eml_security.py
```

---

### Build Windows EXE

```bash
pyinstaller --onefile --windowed --icon=msg_viewer_icon.ico mail_viewer_msg_eml_security.py
```

The executable will be created inside the `dist` folder.

---

### Security Check Notes
The security analysis in this tool is **heuristic** and should be treated as an **initial indicator**, not a final verdict.

It checks for:
- potentially dangerous attachment types
- suspicious URLs
- phishing language
- suspicious sender/domain mismatch

When running on Windows, the program also attempts to scan attachments using **Windows Defender**.

Important:
- this is **not** a full antivirus engine
- this is **not** a sandbox
- this is **not** an EDR solution

It is best used as a **first-pass review tool**.

---

### macOS vs Windows
Development can be done on macOS, but final `.exe` packaging must be done on **Windows**.

Notes:
- On macOS, the application works for viewing and heuristic checks
- On macOS, Windows Defender scanning is not available
- On Windows, both viewing and Defender-based attachment scanning can work

---

### Project Structure
Example files:

```text
mail_viewer_msg_eml_security.py
msg_viewer_icon.ico
README.md
```

---

### Limitations
- No advanced HTML rendering
- No sandbox detonation
- No cloud reputation lookup
- No full malware classification
- Windows Defender scan works only on Windows systems where Defender tools are available

---

### License
You can choose your preferred license for the repository, for example:
- MIT
- Apache-2.0
- Proprietary / Private internal use

---

## Ελληνικά

### Περιγραφή
Αυτό το project είναι μια απλή desktop εφαρμογή σε Python και Tkinter για προβολή email αρχείων τύπου **`.msg`** και **`.eml`**.

Σκοπός του είναι να:
- ανοίγει και να εμφανίζει email αρχεία
- δείχνει βασικά πεδία όπως θέμα, αποστολέα, παραλήπτη, ημερομηνία και σώμα μηνύματος
- εμφανίζει συνημμένα
- εκτελεί έναν **βασικό έλεγχο ασφάλειας** για ύποπτες ενδείξεις

Είναι χρήσιμο για γρήγορο χειροκίνητο έλεγχο email δειγμάτων, ειδικά σε περιβάλλοντα όπου μεγάλο μέρος των μηνυμάτων είναι στα **Ελληνικά**, αλλά χρειάζεται και συμβατότητα στα Αγγλικά.

---

### Δυνατότητες
- Προβολή αρχείων **`.msg`** (μορφή Microsoft Outlook)
- Προβολή αρχείων **`.eml`** (τυπική μορφή email)
- Εμφάνιση:
  - διαδρομής αρχείου
  - τύπου αρχείου
  - θέματος
  - αποστολέα
  - παραλήπτη
  - ημερομηνίας
  - περιεχομένου μηνύματος
- Εμφάνιση συνημμένων
- Βασικός έλεγχος ασφάλειας:
  - ύποπτες επεκτάσεις συνημμένων
  - ύποπτα links
  - λέξεις-κλειδιά phishing
  - πιθανές ενδείξεις spoofing αποστολέα
- Προαιρετικό **Windows Defender** scan στα εξαγόμενα συνημμένα όταν το πρόγραμμα τρέχει σε Windows

---

### Υποστηριζόμενα Formats
Αυτή τη στιγμή υποστηρίζονται:
- `.msg`
- `.eml`

Πιθανή μελλοντική υποστήριξη:
- `.emlx`
- `.mbox`
- `.pst`

---

### Απαιτήσεις
- Προτείνεται Python 3.10+
- Η βιβλιοθήκη `extract_msg` για υποστήριξη `.msg`

Εγκατάσταση εξαρτήσεων:

```bash
pip install extract_msg
```

Για build σε Windows executable:

```bash
pip install pyinstaller
```

---

### Εκτέλεση σε macOS

```bash
python3 mail_viewer_msg_eml_security.py
```

---

### Εκτέλεση σε Windows

```bash
python mail_viewer_msg_eml_security.py
```

---

### Δημιουργία Windows EXE

```bash
pyinstaller --onefile --windowed --icon=msg_viewer_icon.ico mail_viewer_msg_eml_security.py
```

Το εκτελέσιμο θα δημιουργηθεί μέσα στον φάκελο `dist`.

---

### Σημειώσεις για τον Έλεγχο Ασφάλειας
Ο έλεγχος ασφάλειας που κάνει το εργαλείο είναι **heuristic** και πρέπει να θεωρείται **πρώτη ένδειξη**, όχι τελική διάγνωση.

Ελέγχει για:
- πιθανώς επικίνδυνους τύπους συνημμένων
- ύποπτα URLs
- phishing φρασεολογία
- ύποπτη ασυμφωνία αποστολέα / domain

Όταν τρέχει σε Windows, το πρόγραμμα προσπαθεί επίσης να κάνει scan τα συνημμένα μέσω **Windows Defender**.

Σημαντικό:
- δεν είναι πλήρες antivirus engine
- δεν είναι sandbox
- δεν είναι EDR λύση

Είναι καταλληλότερο ως **εργαλείο πρώτου ελέγχου**.

---

### macOS vs Windows
Η ανάπτυξη μπορεί να γίνει σε macOS, αλλά το τελικό build σε `.exe` πρέπει να γίνει σε **Windows**.

Σημειώσεις:
- Σε macOS η εφαρμογή δουλεύει για προβολή και heuristic checks
- Σε macOS δεν υπάρχει Windows Defender scan
- Σε Windows μπορούν να δουλέψουν και η προβολή και το Defender-based attachment scan

---

### Δομή Project
Ενδεικτικά αρχεία:

```text
mail_viewer_msg_eml_security.py
msg_viewer_icon.ico
README.md
```

---

### Περιορισμοί
- Δεν υπάρχει advanced HTML rendering
- Δεν υπάρχει sandbox detonation
- Δεν υπάρχει cloud reputation lookup
- Δεν υπάρχει πλήρης malware classification
- Το Windows Defender scan λειτουργεί μόνο σε Windows συστήματα όπου υπάρχουν τα κατάλληλα Defender tools

---

### Άδεια Χρήσης
Μπορείς να επιλέξεις όποια άδεια θέλεις για το repository, για παράδειγμα:
- MIT
- Apache-2.0
- Proprietary / Private internal use
