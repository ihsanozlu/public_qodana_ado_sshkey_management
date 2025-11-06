from .services.qodana_api import get_all_projects, get_or_create_qodana_ssh_keys,authorize_qodana_projects
from .services.ado_api import create_ssh_key_at_ado,get_created_date_ssh_key,refresh_expired_ssh_keys
from .utils.storage import load_projects_info, save_projects_info
from .utils.comparison import check_if_projects_exist
from .utils.date_utils import is_expired_date
from .utils.project_utils import check_if_new_project_exist

def main():
    print("🚀 Starting Qodana–ADO Sync...")

    # Load previously stored projects
    old_projects = load_projects_info()
    print(f"📦 Loaded {len(old_projects)} local projects")

    # Fetch latest from Qodana
    fetched_projects = get_all_projects()
    print(f"✅ Found {len(fetched_projects)} Qodana projects")
    check_if_projects_exist(old_projects, fetched_projects)

    merged_projects = check_if_new_project_exist(old_projects, fetched_projects)

    save_projects_info(merged_projects)
    print("💾 projects_info.json safely updated (existing SSH keys preserved).")

    project_names = [p.qp_name for p in fetched_projects if getattr(p, "qp_name", None)]
    print(f"🔍 Preparing to request SSH keys for {len(project_names)} projects:")
    for name in project_names:
        print(f"   • {name}")

    updated_projects_with_ssh_data = get_or_create_qodana_ssh_keys(fetched_projects)
    print(f"🔑 SSH key retrieval completed. Updated {len(updated_projects_with_ssh_data)} projects.")

    updated_projects_with_ado_authorizationId = create_ssh_key_at_ado(updated_projects_with_ssh_data)
    print(f"🔑 ADO SSH key ceration and authorization retrival completed. Updated {len(updated_projects_with_ado_authorizationId)} projects.")

    projects_missing_expire = [
        p for p in updated_projects_with_ado_authorizationId
        if not getattr(p, "ado_expireDate", None)
    ]

    projects_with_expire_dates = [
        p for p in updated_projects_with_ado_authorizationId
        if getattr(p, "ado_expireDate", None)
    ]

    expired_projects = [
        p for p in projects_with_expire_dates
        if is_expired_date(getattr(p, "ado_expireDate"))
    ]

    if projects_missing_expire:
        print(f"⚠️ Found {len(projects_missing_expire)} projects missing ado_expireDate. Fetching from ADO...")
        updated_missing = get_created_date_ssh_key(projects_missing_expire)
    else:
        updated_missing = []
    if expired_projects:
        print(f"⚠️ Found {len(expired_projects)} expired ADO SSH keys. Refreshing expiration info...")
        updated_expired = refresh_expired_ssh_keys(expired_projects)
    else:
        updated_expired = []

    if not projects_missing_expire and not expired_projects:
        print("✅ All projects have valid (non-expired) ado_expireDate.")
        final_projects = updated_projects_with_ado_authorizationId
    else:
        final_old_map = {p.qp_name: p for p in updated_projects_with_ado_authorizationId}
        for p in updated_missing + updated_expired:
            final_old_map[p.qp_name] = p

        final_projects = list(final_old_map.values())

    save_projects_info(final_projects)

    authorized_projects_at_qodana = authorize_qodana_projects(final_projects)
    print(f"🔑 Authorizing projects at Qodana is completed. Updated {len(authorized_projects_at_qodana)} projects.")

    save_projects_info(authorized_projects_at_qodana)

if __name__ == "__main__":
    main()