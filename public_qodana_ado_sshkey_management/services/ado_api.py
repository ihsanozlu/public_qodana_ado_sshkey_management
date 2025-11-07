from ..config import (
    QODANA_BASE_URL, QODANA_TEAM, QODANA_COOKIE, 
    QODANA_TEAM_NAME,QODANA_TOKEN,QODANA_ORG_ID ,
    ADO_ORGANIZATION,ADO_PROJECT,ADO_BASE_URL,
    ADO_X_TFS_SESSION,ADO_TARGET_ACCOUNT,ADO_SERVICE_HOST,
    ADO_COOKIE,ADO_COOKIE_FOR_GET_SSH_KEYS
)

import requests
import os
import subprocess
import time
import json
from urllib.parse import quote
from ..models.projects_info import ProjectInfo
from ..utils.date_utils import calculate_expiration_from_createdTime
from ..utils.log_utils import log_ado_authorization_event
from .qodana_api import get_or_create_qodana_ssh_keys
from public_qodana_ado_sshkey_management.utils.storage import save_projects_info
from datetime import datetime, timedelta

def create_ssh_key_at_ado(projects):
    for project in projects:
        project_name = getattr(project, "qp_name", None)
        project_ssh_publickey =getattr(project,"qp_ssh_pubkey",None)
        project_ssh_keyID =getattr(project,"qp_ssh_keyID",None)
        project_ado_authorizationId = getattr(project,"ado_authorizationId",None)

        if not project_name:
            print("⚠️ Skipping project without qp_name")
            continue

        if not project_ssh_publickey and not project_ssh_keyID:
            print(f"⚠️ Skipping project {project} without SSH key data , first create SSH key data please. ")
            continue

        if project_ado_authorizationId:
            print(f"⏭️  Skipping project {project_name} with authorizationId the Id is exist. ")
            continue

        ADO_HierarchyQuery_URL = f"{ADO_BASE_URL}/{ADO_ORGANIZATION}/_apis/Contribution/HierarchyQuery"

        print(f"🔑 Requesting SSH key for project: {project_name}")

        referer = f"{ADO_BASE_URL}/{ADO_ORGANIZATION}/_usersSettings/keys"
        headers = {
            "accept": "application/json;api-version=5.0-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true",
            "authorization": "Bearer {ADO_BEARER_TOKEN}",
            "content-type": "application/json",
            "origin": ADO_BASE_URL,
            "referer": referer,
            "x-tfs-session": ADO_X_TFS_SESSION,
            "x-vss-clientauthprovider":"MsalTokenProvider",
            "Cookie": ADO_COOKIE
        }

        payload = {
            "contributionIds": [
                "ms.vss-token-web.personal-access-token-issue-session-token-provider"
            ],
            "dataProviderContext": {
                "properties": {
                    "displayName": f"qodana_{project_name}_{(datetime.utcnow()).isoformat(timespec="seconds")}",
                    "publicData": project_ssh_publickey,
                    "validFrom": (datetime.utcnow()).isoformat(timespec="milliseconds") + "Z",
                    "validTo": (datetime.utcnow() + timedelta(days=365)).isoformat(timespec="milliseconds") + "Z",
                    "scope": "app_token",
                    "targetAccounts": [ADO_TARGET_ACCOUNT],
                    "isPublic": True,
                    "sourcePage": {
                        "url": referer,
                        "routeId": "ms.vss-admin-web.user-admin-hub-route",
                        "routeValues": {
                            "adminPivot": "keys",
                            "controller": "ContributedPage",
                            "action": "Execute",
                            "serviceHost": f"{ADO_SERVICE_HOST} ({ADO_ORGANIZATION})"
                        }
                    }
                }
            }
        }
        data_raw = json.dumps(payload)

        resp = requests.post(ADO_HierarchyQuery_URL,headers=headers,data=data_raw)
        print(f"{resp.headers}")

        if resp.status_code == 200:
            try:
                data = resp.json()
                auth_data = data.get("dataProviders", {}).get("ms.vss-token-web.personal-access-token-issue-session-token-provider", {})
                authorizationId = auth_data.get("authorizationId")
                #formattedCreatedTime = data.get("formattedCreatedTime")
                if not authorizationId:
                   print(f"⚠️ No authorizationId returned for {project_name}") 
                   continue

                project.ado_authorizationId = authorizationId
                save_projects_info(projects)
                print("💾 Updated projects_info.json with authorizationId")
            except json.JSONDecodeError:
                print(f"❌ Could not parse JSON for {project_name}: {resp.text}")
        else:
            print(f"❌ Azure DevOps returned {resp.status_code} for {project_name}: {resp.text}")
        time.sleep(1)
    return projects

def get_created_date_ssh_key(projects):
    for project in projects:
        project_name = getattr(project, "qp_name", None)
        project_ssh_publickey =getattr(project,"qp_ssh_pubkey",None)
        project_ssh_keyID =getattr(project,"qp_ssh_keyID",None)
        project_ado_authorizationId = getattr(project,"ado_authorizationId",None)
        project_ado_expireDate = getattr(project,"ado_expireDate",None)

        if not project_name:
            print("⚠️ Skipping project without qp_name")
            continue

        if not project_ssh_publickey and not project_ssh_keyID:
            print(f"⚠️ Skipping project {project} without SSH key data , first create SSH key data please. ")
            continue

        if not project_ado_authorizationId:
            print(f"⚠️ Skipping project {project_name} without authorizationId , first get authorizationId from ADO. ")
            continue

        ADO_HierarchyQuery_URL = f"{ADO_BASE_URL}/{ADO_ORGANIZATION}/_apis/Contribution/HierarchyQuery"

        referer = f"{ADO_BASE_URL}/{ADO_ORGANIZATION}/_usersSettings/keys"

        headers = {
            "accept": "application/json;api-version=5.0-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true",
            "authorization": "Bearer {ADO_BEARER_TOKEN}",
            "content-type": "application/json",
            "origin": ADO_BASE_URL,
            "referer": referer,
            "x-tfs-session": ADO_X_TFS_SESSION,
            "x-vss-clientauthprovider":"MsalTokenProvider",
            "Cookie": ADO_COOKIE_FOR_GET_SSH_KEYS
        }

        payload = {
            "contributionIds": [
                "ms.vss-admin-web.profile-sshpublickeys-view-data-provider"
            ],
            "dataProviderContext": {
                "properties": {
                    "authorizationId": project_ado_authorizationId,
                    "sourcePage": {
                        "url": referer,
                        "routeId": "ms.vss-admin-web.user-admin-hub-route",
                        "routeValues": {
                            "adminPivot": "keys",
                            "controller": "ContributedPage",
                            "action": "Execute",
                            "serviceHost": f"{ADO_SERVICE_HOST} ({ADO_ORGANIZATION})"
                        }
                    }
                }
            }
        }
        
        print(f"🔑 Cecking Creation Date of SSH KEY at ADO for project: {project_name}")
        data_raw = json.dumps(payload)
        try:
            resp = requests.post(ADO_HierarchyQuery_URL,headers=headers,data=data_raw)
        except requests.RequestException as e:
            print(f"❌ Request error for {project_name}: {e}")
            continue

        if resp.status_code == 200:
            try:
                data = resp.json()
                proovider = data.get("dataProviders", {}).get("ms.vss-admin-web.profile-sshpublickeys-view-data-provider", {})
                createdTime = proovider.get("createdTime")
                if not createdTime:
                   print(f"⚠️ No createdTime returned for {project_name}") 
                   continue
                #print(f"DEBUG: {project_name} createdTime={createdTime}")
                expireDate = calculate_expiration_from_createdTime(createdTime)
                #print(f"DEBUG: {project_name} createdTime={createdTime} -> expireDate={expireDate}")
                project.ado_expireDate = expireDate
                save_projects_info(projects)
                print("💾 Updated projects_info.json with ExpirationDate")

                log_ado_authorization_event(
                    project_name=project.qp_name,
                    authorization_id=project.ado_authorizationId,
                    expire_date=expireDate,
                    event="created" if not getattr(project, "qp_isAccessible", False) else "refreshed"
                )
            except json.JSONDecodeError:
                print(f"❌ Could not parse JSON for {project_name}: {resp.text}")
        else:
            print(f"❌ Azure DevOps returned {resp.status_code} for {project_name}: {resp.text}")
        time.sleep(1)
    print("💾 All projects updated with SSH key expiration dates.")
    return projects

def refresh_expired_ssh_keys(expired_projects):
    if not expired_projects:
        print("✅ No expired SSH keys to refresh.")
        return []

    print(f"🔁 Refreshing SSH keys for {len(expired_projects)} expired projects...")

    for project in expired_projects:
        project.qp_ssh_pubkey = None
        project.qp_ssh_keyID = None
        project.qp_isAccessible = False
        project.ado_authorizationId = None
        project.ado_expireDate = None

    updated_projects = get_or_create_qodana_ssh_keys(expired_projects)
    updated_projects = create_ssh_key_at_ado(updated_projects)
    updated_projects = get_created_date_ssh_key(updated_projects)

    print(f"✅ Completed refreshing SSH keys for {len(updated_projects)} projects.")
    return updated_projects

