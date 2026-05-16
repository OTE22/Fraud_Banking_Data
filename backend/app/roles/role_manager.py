from app.roles.permission_manager import get_role_permissions


def create_role(name: str, description: str = "") -> dict:
    return {"name": name, "description": description, "permissions": get_role_permissions(name)}


def list_roles() -> list[dict]:
    role_names = ["admin", "fraud_analyst", "data_scientist", "ml_engineer", "auditor", "soc_team"]
    return [create_role(name) for name in role_names]
