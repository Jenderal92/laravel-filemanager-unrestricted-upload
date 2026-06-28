# Laravel FileManager Unrestricted File Upload → RCE

**CWE-434: Unrestricted Upload of File with Dangerous Type**  
**CVSS Score: 9.8 (Critical)**

---

## 📋 Description

This tool demonstrates a security vulnerability in Laravel FileManager (barryvdh/laravel-elfinder) that allows Remote Code Execution (RCE) through unrestricted file upload.

The vulnerability occurs when:
- FileManager is installed and publicly accessible
- CSRF tokens can be extracted from public pages
- Upload endpoint lacks proper file validation
- PHP execution is allowed in upload directories

---

## 🚨 Vulnerability Details

| Attribute | Value |
|-----------|-------|
| **Vulnerability Type** | Unrestricted File Upload → RCE |
| **CWE** | CWE-434 |
| **CVSS Score** | 9.8 (Critical) |
| **Attack Vector** | Network |
| **Attack Complexity** | Low |
| **Privileges Required** | None |
| **User Interaction** | None |

### Attack Chain
