async def create_group(name: str, description: str = "") -> dict:
    return {"name": name, "description": description, "members": []}


async def add_member_to_group(group: dict, user_id: int) -> dict:
    if user_id not in group["members"]:
        group["members"].append(user_id)
    return group
