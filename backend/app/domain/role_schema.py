from pydantic import BaseModel, Field
from typing import Optional


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    permissions: list[str] = []


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: list[str]


class PermissionCreate(BaseModel):
    name: str
    resource: str
    action: str


class PermissionResponse(BaseModel):
    id: int
    name: str
    resource: str
    action: str
