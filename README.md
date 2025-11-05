# Qodana ↔ Azure DevOps SSH Key Management

This repository automates SSH key management between **JetBrains Qodana** and **Azure DevOps (ADO)**.

---

## 🧭 Overview

Qodana requires **SSH key-based authorization** to access Azure DevOps repositories (VCS) for CI/CD integration.  
Managing these SSH keys manually across many projects is time-consuming and error-prone — especially since ADO SSH keys **expire periodically**.

This repository provides a full automation workflow for:

- Retrieving **SSH Key IDs and Public Keys** from Qodana  
- Creating corresponding **SSH Keys in Azure DevOps**  
- **Refreshing keys** automatically based on expiration dates  

---

## ⚙️ Process Summary

1. Fetch **SSH keys** (key ID and public key) from Qodana  
2. Register those keys in **Azure DevOps** via REST API  
3. Periodically check for expired SSH keys  
4. Automatically **refresh and update** expired keys in both systems  

---

## 🔑 Requirements

Before using this automation, you must first collect temporary tokens and cookies manually.  
These tokens **expire after a short time**, so you’ll need to regenerate them periodically.

---

### 1. Get Qodana Tokens

> You’ll find the tokens in your browser’s Developer Tools → Network tab, while authorizing a project via Azure DevOps VCS.

| Step | Screenshot |
|------|-------------|
| 1 | ![qodana_get_token_1](/public_qodana_ado_sshkey_management/assets/images/qodana_get_token_1.png) |
| 2 | ![qodana_get_token_2](/public_qodana_ado_sshkey_management/assets/images/qodana_get_token_2.png) |
| 3 | ![qodana_get_token_3_user_cookie](/public_qodana_ado_sshkey_management/assets/images/qodana_get_token_3_user_cookie.png) |

---

### 2. Get Azure DevOps Tokens

Create a **dummy SSH key** in ADO first to capture the required CURL request and tokens.

| Step | Screenshot |
|------|-------------|
| 1. Create dummy SSH key → open DevTools → Network → filter: `HierarchyQuery` | ![ado_get_ssh_keys_bearerToken_cookie](/public_qodana_ado_sshkey_management/assets/images/ado_get_ssh_keys_bearerToken_cookie.png) |
| 2. Look for a “create” request (different from other queries) and copy it as **CURL** |
| 3. Use that CURL to extract your **bearer token** and **cookies** |

---

### 3. Get SSH Key Authorization IDs and Created Dates

You can retrieve this information from the same Network tab after the SSH keys are listed:

| Screenshot |
|-------------|
| ![ado_get_sshkeys_authorizationId_createdDate](/public_qodana_ado_sshkey_management/assets/images/ado_get_sshkeys_authorizationId_createdDate.png) |

---

## ⚡️ Usage Flow

1. Identify projects that:
   - Don’t have SSH keys yet → `missing_projects`
   - Have expired SSH keys → `expired_projects`
2. For each missing or expired project:
   - Fetch or create new SSH keys from Qodana  
   - Register them in Azure DevOps  
   - Update and save the new expiration info in `projects_info.json`

---

## 🔁 Auto Refresh Logic

When refreshing expired projects:
- Old key fields are cleared:

  ```text
  qp_ssh_pubkey
  qp_ssh_keyID
  ado_authorizationId
  ado_expireDate

- Then the process automatically:

1. Generates new SSH keys from Qodana
2. Creates them in ADO
3. Updates expiration and metadata