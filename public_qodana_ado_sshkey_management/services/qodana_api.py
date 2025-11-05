from ..config import (
    QODANA_BASE_URL, QODANA_TEAM, QODANA_COOKIE,
    QODANA_TEAM_NAME,QODANA_TOKEN,QODANA_ORG_ID ,
    ADO_ORGANIZATION,ADO_PROJECT
    )
import requests
import os
import subprocess
import time
import json
from urllib.parse import quote
from ..models.projects_info import ProjectInfo
from qodana_ado_sshkey_management.utils.storage import save_projects_info

def get_all_projects() -> list[ProjectInfo]:
    url = f"{QODANA_BASE_URL}/api/v1/teams/{QODANA_TEAM}/projects"
    headers = {
        "accept": "*/*",
        "referer": f"{QODANA_BASE_URL}/teams/{QODANA_TEAM}",
    }
    cookies = {"user-cookie-session": QODANA_COOKIE}

    resp = requests.get(url, headers=headers, cookies=cookies)
    resp.raise_for_status()
    data = resp.json()

    return [ProjectInfo(qp_name=i["name"], qp_id=i["id"]) for i in data.get("items", [])]

def get_or_create_qodana_ssh_keys(projects):
    #updated = []

    for project in projects:
        project_name = getattr(project, "qp_name", None)
        if not project_name:
            print("⚠️ Skipping project without qp_name")
            continue

        if getattr(project,"qp_ssh_pubkey",None) and getattr(project,"qp_ssh_keyID",None):
            print(f"⏭️  Skipping {project_name} (already has SSH key data)")
            continue

        ADO_SSH_URL = f"git@ssh.dev.azure.com:v3/{ADO_ORGANIZATION}/{ADO_PROJECT}"
        # Build the exact encoded SSH URL
        ssh_url = f"{ADO_SSH_URL}/{project_name}"
        encoded_ssh_url = quote(ssh_url, safe="")  # fully encode everything
        url = f"{QODANA_BASE_URL}/api/v1/organizations/{QODANA_ORG_ID}/probe-repository?sshUrl={encoded_ssh_url}"

        print(f"🔑 Requesting SSH key for project: {project_name}")
        print(f"🌐 URL: {url}")

        headers = {"accept": "*/*"}
        cookies = {"user-cookie-session": QODANA_COOKIE}

        resp = requests.get(url, headers=headers, cookies=cookies)

        if resp.status_code == 200:
            try:
                data = resp.json()
                ssh_pubkey = data.get("publicKey") or data.get("sshPublicKey")
                ssh_key_id = data.get("id") or data.get("sshKeyId")

                if not ssh_pubkey or not ssh_key_id:
                    print(f"⚠️ No SSH key data returned for {project_name}")
                    continue

                project.qp_ssh_pubkey = ssh_pubkey
                project.qp_ssh_keyID = ssh_key_id
                save_projects_info(projects)
                print("💾 projects_info.json updated safely (existing keys preserved).")

            except json.JSONDecodeError:
                print(f"❌ Could not parse JSON for {project_name}: {resp.text}")
        else:
            print(f"❌ Qodana returned {resp.status_code} for {project_name}: {resp.text}")
        time.sleep(1)
    return projects
