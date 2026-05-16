from app.config import get_settings


def check_permission(required_role: str, user_roles: list[str]) -> bool:
    hierarchy = get_settings().role_hierarchy
    for role in user_roles:
        if role in hierarchy and required_role in hierarchy[role]:
            return True
    return False


def require_feature(feature: str, user_permissions: list[str]) -> bool:
    return feature in user_permissions
