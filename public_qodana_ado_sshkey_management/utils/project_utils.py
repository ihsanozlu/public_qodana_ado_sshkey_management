def check_if_new_project_exist(old_projects, fetched_projects):
    merged_projects = []

    old_map = {p.qp_name: p for p in old_projects}
    for p in fetched_projects:
        existing = old_map.get(p.qp_name)
        if existing:
            # Preserve SSH and other metadata
            p.qp_name = getattr(existing, "qp_name", None)
            p.qp_id = getattr(existing, "qp_id", None)
            p.qp_ssh_pubkey = getattr(existing, "qp_ssh_pubkey", None)
            p.qp_ssh_keyID = getattr(existing, "qp_ssh_keyID", None)
            p.qp_isAccessible = getattr(existing, "qp_isAccessible", False)
            p.ado_authorizationId = getattr(existing, "ado_authorizationId", None)
            p.ado_expireDate = getattr(existing, "ado_expireDate", None)
        merged_projects.append(p)
    return merged_projects