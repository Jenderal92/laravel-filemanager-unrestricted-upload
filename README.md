# Laravel FileManager Unrestricted File Upload (CVE-2025-56399)

**CWE-434: Unrestricted Upload of File with Dangerous Type**  
**CVSS Score: 8.5 (High)**  

---

## 📋 Description

This tool provides a **Proof of Concept (PoC)** for **CVE-2025-56399**, a critical vulnerability in `alexusmai/laravel-file-manager` (versions ≤ 3.3.1).  

The vulnerability allows an **authenticated attacker** to achieve **Remote Code Execution (RCE)** by uploading a crafted file, bypassing client‑side validation, and renaming it to a PHP extension.  

This script automates the entire process:
- Detects FileManager endpoints (supports multiple Laravel FileManager variants)
- Extracts CSRF tokens
- Uploads a payload and verifies execution

---

## 🚨 Vulnerability Details (CVE-2025-56399)

| Attribute | Value |
|-----------|-------|
| **Vulnerability Type** | Unrestricted File Upload → RCE |
| **CWE** | CWE-434 |
| **CVSS Score** | 8.5 (High) |
| **Attack Vector** | Network |
| **Attack Complexity** | Low |
| **Privileges Required** | Low (Authenticated) |
| **User Interaction** | Active |

### Attack Chain (as per CVE-2025-56399)

1. Authenticate to the application  
2. Access the FileManager interface (`/file-manager`)  
3. Upload a `.png` file containing PHP code  
4. Use the rename API to change the extension to `.php`  
5. Access the file → server executes PHP code → **RCE achieved**

---

## 🛠️ Installation

```bash
git clone https://github.com/Jenderal92/laravel-filemanager-unrestricted-upload.git
cd laravel-filemanager-unrestricted-upload
pip install -r requirements.txt
```

Requirements

· Python 2.7
· requests
· colorama

---

📖 Usage

```bash
python2 lfm.py list.txt
```

Input Format (list.txt)

```
https://target1.com
https://target2.com
http://target3.com
```

Output

· valid.txt – List of validated shell URLs (append ?shinday=1 to access)

Example output:

```
https://target.com/storage/shxt_123456.php?shinday=1
```

---

🧪 How the Exploit Works

1. Detection – Checks common FileManager paths:
   · /file-manager/tinymce
   · /file-manager/ckeditor
   · /file-manager/tinymce5
   · /file-manager/summernote
   · /admin/file-manager/tinymce
   For alexusmai/laravel-file-manager, the default path is /file-manager. You can add it to the paths list in the script if needed.
2. CSRF Token Extraction – Extracts the token from <meta name="csrf-token"> or an _token input field.
3. Initialization – Calls /file-manager/initialize to retrieve the disk configuration.
4. Upload – Uploads .htaccess (to bypass restrictions) and then the payload (shxt_<timestamp>.php) with a GIF MIME type.
5. Verification – Checks if ?shinday=1 returns the string Shinday; if so, the shell is valid and saved to valid.txt.

---

📂 Payload Details

The uploaded PHP file is a one‑file web shell that:

· Displays system information (php_uname)
· Provides a file upload form (for adding more tools)
· Responds to the parameter ?shinday=1 with the full shell interface
· Otherwise, outputs a valid GIF89a image to avoid detection

Access the shell via:

```
https://target.com/path/to/shxt_123456.php?shinday=1
```

---

🛡️ Mitigation

To protect against this vulnerability:

1. Update the package – Wait for a patch (no official fix yet). Consider replacing alexusmai/laravel-file-manager with an alternative.
2. Restrict Access – Add authentication middleware to all FileManager routes:
   ```php
   Route::group(['middleware' => ['auth', 'admin']], function () {
       // File Manager routes
   });
   ```
3. Disable if Not Needed – Remove the package:
   ```bash
   composer remove alexusmai/laravel-file-manager
   ```
4. Prevent PHP Execution – Place a .htaccess file in the storage directory:
   ```apache
   <FilesMatch "\.(php|phtml|php3|php4|php5|phar)$">
       Deny from all
   </FilesMatch>
   ```
5. Validate File Types – Implement strict server‑side validation for uploaded files.

---

📦 Affected Versions

Package Affected Versions
alexusmai/laravel-file-manager ≤ 3.3.1

---

🔗 References

· CVE-2025-56399 - NVD
· GitHub Advisory
· Snyk Vulnerability Database
· VulDB Entry
· alexusmai/laravel-file-manager

---

📜 Disclaimer

WARNING: This tool is for educational and authorized security testing only.
By using it, you agree to:

· Only test systems you own or have explicit permission to test
· Not use it for malicious purposes
· Comply with all applicable laws

The author assumes no liability for any misuse or damage caused.

---
