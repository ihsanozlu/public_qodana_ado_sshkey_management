def check_if_projects_exist(old_projects, fetched_projects):
    """Compare old vs fetched projects and print differences."""
    def get_name(p):
        return getattr(p, "qp_name", getattr(p, "name", None))

    old_names = {get_name(p) for p in old_projects}
    new_names = {get_name(p) for p in fetched_projects}

    added = [p for p in fetched_projects if get_name(p) not in old_names]
    removed = [p for p in old_projects if get_name(p) not in new_names]

    print("\n🔍 Project comparison results:")
    if added:
        print("🆕 New projects:")
        for p in added:
            print(f"  ➕ {get_name(p)}")
    else:
        print("✅ No new projects found.")

    if removed:
        print("\n❌ Removed projects:")
        for p in removed:
            print(f"  ➖ {get_name(p)}")
    else:
        print("✅ No removed projects found.")
