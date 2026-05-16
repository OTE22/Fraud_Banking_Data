ROLE_REGISTRY: dict[str, list[str]] = {
    "admin": ["users:read", "users:write", "users:delete", "fraud:read", "fraud:write", "models:deploy", "models:train", "audit:read", "roles:manage"],
    "fraud_analyst": ["fraud:read", "fraud:write", "users:read"],
    "data_scientist": ["models:train", "models:evaluate", "fraud:read"],
    "ml_engineer": ["models:deploy", "models:train", "fraud:read"],
    "auditor": ["audit:read", "fraud:read"],
    "soc_team": ["fraud:read", "users:read", "users:write"],
}


def get_role_permissions(role_name: str) -> list[str]:
    return ROLE_REGISTRY.get(role_name, [])


def role_has_permission(role_name: str, permission: str) -> bool:
    return permission in get_role_permissions(role_name)
