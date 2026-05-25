# 📧 MailViewer

Professional lightweight viewer for email files (`.msg`, `.eml`) with modern interface, bilingual support and built-in export tools.

---

### 🇬🇷 Ελληνικά
- Άνοιγμα αρχείων `.msg` και `.eml`
- Άνοιγμα ολόκληρου φακέλου με email αρχεία
- Προβολή:
  - Αποστολέας
  - Παραλήπτης
  - Θέμα
  - Ημερομηνία
  - Περιεχόμενο
- Διαχείριση συνημμένων αρχείων
- Νέος ισχυρότερος έλεγχος ασφαλείας
- Οργανωμένα security tabs:
  - Τι να κάνω
  - Σύνοψη
  - Ευρήματα
  - Κουμπιά / Actions
  - Υπερσύνδεσμοι
  - URLs
  - Συνημμένα
  - Headers
  - Keywords
- Εμφάνιση πραγματικού συνδέσμου πίσω από κουμπιά και υπερσυνδέσμους
- Μεγαλύτερα και πιο ευανάγνωστα πλαίσια μηνύματος και ελέγχου ασφαλείας
- Export σε PDF
- Δίγλωσσο περιβάλλον (Ελληνικά / English)
- Σύγχρονο dark UI
- Portable έκδοση χωρίς εγκατάσταση

---

### Τι ελέγχει

- Έλεγχος βασικών στοιχείων email:
  - Αποστολέας
  - Παραλήπτης
  - Θέμα
  - Ημερομηνία
  - Τύπος αρχείου
  - Συνημμένα

- Έλεγχος αποστολέα:
  - Διαφορά μεταξύ `From` και `Return-Path`
  - Διαφορά μεταξύ `From` και `Reply-To`
  - Ύποπτη χρήση εσωτερικού-looking αποστολέα
  - Email που παριστάνουν webmail, helpdesk, support ή security alert

- Έλεγχος headers:
  - `Received`
  - `Return-Path`
  - `Reply-To`
  - `Message-ID`
  - `Authentication-Results`
  - `Received-SPF`
  - `DKIM-Signature`
  - `X-Spam-Status`
  - `X-Spam-Flag`
  - `X-Spam-Score`

- Έλεγχος authentication indicators:
  - SPF fail / softfail / neutral, όταν υπάρχει στα headers
  - DKIM fail, όταν υπάρχει στα headers
  - DMARC fail / quarantine / reject, όταν υπάρχει στα headers
  - Απουσία βασικών authentication headers
  - Ύποπτη ένδειξη `WHITELISTED` σε email με άλλα ύποπτα στοιχεία

- Έλεγχος URLs:
  - Εξαγωγή URLs από plain text
  - Εξαγωγή URLs από HTML
  - Εξαγωγή πραγματικών `href` links
  - Defanged εμφάνιση URLs για αποφυγή τυχαίου click
  - Εντοπισμός shortened URLs
  - Εντοπισμός IP-based URLs
  - Εντοπισμός URLs με `@`
  - Εντοπισμός redirect parameters όπως `url=`, `redirect=`, `next=`, `continue=`
  - Εντοπισμός πολλών διαφορετικών domains στο ίδιο email
  - Εντοπισμός cloud/object-storage links που μπορεί να χρησιμοποιούνται σε phishing

- Έλεγχος κουμπιών και actions:
  - Εμφάνιση πραγματικού URL πίσω από κουμπιά
  - Παράδειγμα:
    - `Review Messages -> hxxps://example[.]com/login`
  - Εντοπισμός action words όπως:
    - Login
    - Verify
    - Review
    - Release
    - Allow
    - Update
    - Confirm
    - Πατήστε εδώ
    - Επαλήθευση
    - Σύνδεση
    - Προβολή
    - Ενημέρωση

- Έλεγχος υπερσυνδέσμων:
  - Εμφάνιση ορατού κειμένου και πραγματικού URL
  - Παράδειγμα:
    - `Πατήστε εδώ -> hxxps://suspicious[.]site/login`

- Έλεγχος display URL mismatch:
  - Εντοπισμός περιπτώσεων όπου το ορατό link φαίνεται νόμιμο αλλά το πραγματικό `href` οδηγεί αλλού

- Έλεγχος ύποπτων domains:
  - Punycode / IDN indicators
  - Brand impersonation patterns
  - Περίεργα subdomains
  - Domain mismatch με τον αποστολέα
  - Cloud-hosted login pages

- Έλεγχος συνημμένων:
  - Εκτελέσιμα αρχεία
  - Script files
  - Office macro files
  - HTML / SVG attachments
  - Archives και containers
  - Double extensions όπως `invoice.pdf.exe`

- Έλεγχος phishing language:
  - Ελληνικές και αγγλικές φράσεις που συχνά εμφανίζονται σε phishing emails
  - Παραδείγματα:
    - Πατήστε εδώ
    - Απαιτείται ενέργεια
    - Επαλήθευση λογαριασμού
    - Review messages
    - Verify account
    - Password
    - Security alert
    - Mailbox full

- Risk scoring:
  - Χαμηλό Ρίσκο
  - Μέτριο Ρίσκο
  - Ύποπτο
  - Πολύ Ύποπτο

- User-friendly guidance:
  - Απλή οδηγία προς τον χρήστη
  - Τι να κάνει
  - Τι να μην κάνει
  - Πότε να ενημερώσει το Γραφείο Πληροφορικής και Δικτύων

---

### 🇬🇧 English
- Open `.msg` and `.eml` files
- Open folders containing emails
- View sender, recipient, subject, date and body
- Attachment handling
- New advanced security check
- Organized security tabs:
  - What should I do
  - Summary
  - Findings
  - Buttons / Actions
  - Hyperlinks
  - URLs
  - Attachments
  - Headers
  - Keywords
- Show the real destination behind buttons and hyperlinks
- Larger and more readable message and security detail panels
- Export to PDF
- Bilingual interface
- Modern dark UI
- Portable version

---

### What it checks

- Basic email information:
  - Sender
  - Recipient
  - Subject
  - Date
  - File type
  - Attachments

- Sender consistency:
  - `From` and `Return-Path` mismatch
  - `From` and `Reply-To` mismatch
  - Suspicious internal-looking sender
  - Emails impersonating webmail, helpdesk, support or security alerts

- Header inspection:
  - `Received`
  - `Return-Path`
  - `Reply-To`
  - `Message-ID`
  - `Authentication-Results`
  - `Received-SPF`
  - `DKIM-Signature`
  - `X-Spam-Status`
  - `X-Spam-Flag`
  - `X-Spam-Score`

- Authentication indicators:
  - SPF fail / softfail / neutral, when present in headers
  - DKIM fail, when present in headers
  - DMARC fail / quarantine / reject, when present in headers
  - Missing authentication headers
  - Suspicious `WHITELISTED` status combined with other suspicious indicators

- URL analysis:
  - Extracts URLs from plain text
  - Extracts URLs from HTML
  - Extracts real `href` destinations
  - Displays URLs in defanged form to reduce accidental clicks
  - Detects shortened URLs
  - Detects IP-based URLs
  - Detects URLs containing `@`
  - Detects redirect parameters such as `url=`, `redirect=`, `next=`, `continue=`
  - Detects multiple unrelated domains inside the same email
  - Detects cloud/object-storage links often abused in phishing campaigns

- Button and action link analysis:
  - Shows the real URL behind clickable buttons
  - Example:
    - `Review Messages -> hxxps://example[.]com/login`
  - Detects action words such as:
    - Login
    - Verify
    - Review
    - Release
    - Allow
    - Update
    - Confirm
    - Click here
    - View
    - Open

- Hyperlink analysis:
  - Shows visible hyperlink text and the real destination URL
  - Example:
    - `Click here -> hxxps://suspicious[.]site/login`

- Display URL mismatch detection:
  - Detects cases where the visible link appears legitimate but the real `href` points somewhere else

- Suspicious domain indicators:
  - Punycode / IDN indicators
  - Brand impersonation patterns
  - Suspicious subdomains
  - Domain mismatch with sender
  - Cloud-hosted login pages

- Attachment checks:
  - Executable files
  - Script files
  - Office macro files
  - HTML / SVG attachments
  - Archives and container files
  - Double extensions such as `invoice.pdf.exe`

- Phishing language detection:
  - Greek and English phrases commonly used in phishing emails
  - Examples:
    - Click here
    - Verify account
    - Review messages
    - Password
    - Security alert
    - Mailbox full
    - Urgent action required

- Risk scoring:
  - Low Risk
  - Medium Risk
  - Suspicious
  - Highly Suspicious

- User-friendly guidance:
  - Simple recommendation for the user
  - What to do
  - What not to do
  - When to contact the Office of Informatics and Networks
