# SecurePass Vault

## Repository

**Multi-User Password Manager & Encryption-Based Credential Vault**

### Repository

GitHub Repository

```bash
git clone https://github.com/IkjyotKaur/SecurePass.git
cd SecurePass
```

SecurePass Vault is a desktop-based password management application developed using Python and Tkinter. The system enables users to securely store, retrieve, manage, and encrypt credentials using multiple cryptographic algorithms including Fernet, Caesar Cipher, Affine Cipher, and RC4. It features multi-user authentication, encrypted vault storage, clipboard protection, and a modern cybersecurity-inspired graphical interface.

---

## Tech Stack

| Layer          | Technologies                                             |
| -------------- | -------------------------------------------------------- |
| Frontend GUI   | Tkinter, ttk                                             |
| Backend Logic  | Python                                                   |
| Encryption     | Fernet (Cryptography), Caesar Cipher, Affine Cipher, RC4 |
| Authentication | SHA-256 Hashing                                          |
| Storage        | Local File-Based Vault                                   |
| Security       | Clipboard Protection, User Isolation                     |

---

## Project Structure

```text
SecurePass/
│
├── main.py
│
├── auth/
│   ├── vaultauth.bin
│   └── user_authentication.py
│
├── vaults/
│   ├── user1_vault.txt
│   ├── user2_vault.txt
│   └── ...
│
├── encryption/
│   ├── caesar.py
│   ├── affine.py
│   ├── rc4.py
│   └── fernet.py
│
├── assets/
│   ├── icons/
│   └── screenshots/
│
├── vault.key
└── README.md
```

---

## Quick Start

### Installation

Clone the repository:

```bash
git clone https://github.com/IkjyotKaur/SecurePass.git
cd SecurePass
```

---

### Install Dependencies

```bash
pip install cryptography
```

---

### Run Application

```bash
python main.py
```

---

## Features

### Multi-User Authentication

* User Registration
* Secure Login System
* Individual User Vaults
* SHA-256 Password Hashing

---

### Password Vault Management

* Store Credentials
* Retrieve Passwords
* Edit Saved Entries
* Delete Entries
* Website-Based Search

---

### Multiple Encryption Algorithms

#### Fernet Encryption

* Symmetric authenticated encryption
* Strong modern cryptography
* Automatic key generation

#### Caesar Cipher

* Shift-based classical encryption
* User-defined key support

#### Affine Cipher

* Mathematical substitution encryption
* Custom affine keys

#### RC4 Encryption

* Stream cipher implementation
* Custom secret key support

---

### Secure Retrieval

* Temporary password visibility
* Auto-hide after 3 seconds
* Clipboard copy functionality
* Automatic clipboard cleanup after 10 seconds

---

### Dashboard & Analytics

Displays:

* Logged-In User
* Vault Status
* Total Saved Passwords
* Encryption Status
* Last Saved Website
* Session Information

---

### Modern Cybersecurity UI

* Responsive desktop interface
* Sidebar navigation
* Interactive dashboard
* Security-themed design
* Real-time notifications

---

## System Workflow

```text
User Registration/Login
            │
            ▼
      Authentication
            │
            ▼
      User Vault Access
            │
            ▼
Password Encryption & Storage
            │
            ▼
Encrypted Credential Vault
            │
            ▼
Secure Retrieval & Management
```

---

## Core Modules

### Authentication Module

Responsible for:

* User Registration
* Login Verification
* Password Hashing
* Session Management

---

### Encryption Engine

Supports:

* Fernet Encryption
* Caesar Cipher
* Affine Cipher
* RC4 Cipher

---

### Vault Manager

Handles:

* Credential Storage
* Credential Retrieval
* Entry Modification
* Entry Deletion

---

### Security Layer

Provides:

* Encrypted Storage
* Clipboard Protection
* User Isolation
* Secure Password Display

---

## Sample Workflow

### Save Credential

```text
Website: github.com
Username: user@example.com
Password: MySecurePassword123
Encryption: Fernet
```

### Stored Data

```text
github.com|user@example.com|Fernet|EncryptedText|NA
```

### Retrieval

```text
✓ Search Website
✓ Decrypt Password
✓ Reveal for 3 Seconds
✓ Copy Securely
```

---

## Security Features

### Authentication Security

* SHA-256 Password Hashing
* User Credential Verification
* Secure Login Validation

### Data Security

* Encrypted Password Storage
* User-Specific Vaults
* Clipboard Auto-Clear

### Access Control

* Separate Vault per User
* Session-Based Access
* Secure Logout Mechanism

---

## Screenshots

### Home Page

* SecurePass Landing Interface

### Login & Registration

* Multi-User Authentication System

### Dashboard

* Credential Overview & Statistics

### Password Management

* Add, Edit, Retrieve & Delete Credentials

---

## Educational Relevance

This project demonstrates practical implementation of:

* Cryptography Fundamentals
* Password Management Systems
* Authentication & Authorization
* Secure Software Design
* GUI Development using Tkinter
* Encryption Algorithms
* Cybersecurity Principles
* Secure Data Storage

---

## Future Enhancements

* AES-256 Encryption Support
* Password Strength Analyzer
* Password Generator
* Two-Factor Authentication (2FA)
* Cloud Backup Integration
* SQLite Database Storage
* Biometric Authentication
* Dark/Light Theme Switching
* Password Breach Detection

---

## License

Educational and Academic Use Only.

---

## Disclaimer

This project is developed for educational and learning purposes. While it implements encryption and authentication mechanisms, it should not be used as a production-grade password manager without additional security auditing and enhancements.

---

## Support

If you found this project useful, consider giving it a ⭐ on GitHub.
