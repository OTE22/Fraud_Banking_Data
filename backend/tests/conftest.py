import sys, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import get_db
from app.auth.password_utils import hash_password


class MockUser:
    def __init__(self, id=1, username="admin", email="admin@bank.com", password="admin123", roles="admin,analyst", is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hash_password(password)
        self.roles = roles
        self.is_active = is_active
        self.created_at = None


class MockSession:
    def __init__(self):
        self._users: list[MockUser] = [
            MockUser(id=1, username="admin", email="admin@bank.com", roles="admin,analyst"),
            MockUser(id=2, username="analyst1", email="analyst1@bank.com", roles="fraud_analyst"),
        ]
        self._next_id = 3
        self._added = []

    async def __aenter__(self): return self
    async def __aexit__(self, *a): pass
    async def flush(self): pass
    async def close(self): pass

    def add(self, obj):
        self._added.append(obj)

    async def commit(self):
        for obj in self._added:
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = self._next_id
                self._next_id += 1
            self._users.append(obj)
        self._added = []

    async def refresh(self, obj):
        pass

    async def execute(self, stmt):
        from sqlalchemy import select
        from app.users.models import UserModel
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))

        class MockScalars:
            def __init__(self, users):
                self._users = users
            def all(self):
                return self._users
            def __iter__(self):
                return iter(self._users)
            def first(self):
                return self._users[0] if self._users else None

        class MockResult:
            def __init__(self, users):
                self._users = users
            def scalars(self):
                return MockScalars(self._users)
            def scalar_one_or_none(self):
                return self._users[0] if self._users else None

        import re
        username_match = re.search(r"username\s*=\s*'(\w+)'", compiled)
        if username_match:
            name = username_match.group(1)
            matches = [u for u in self._users if u.username == name]
            return MockResult(matches)
        if "WHERE users.id = " in compiled:
            import re
            m = re.search(r"users\.id = (\d+)", compiled)
            if m:
                uid = int(m.group(1))
                matches = [u for u in self._users if u.id == uid]
                return MockResult(matches)
        if "FROM users" in compiled:
            return MockResult(self._users)
        return MockResult([])


_mock_session = MockSession()


async def override_db():
    yield _mock_session


@pytest.fixture(autouse=True)
def reset_mock():
    _mock_session._users = [
        MockUser(id=1, username="admin", email="admin@bank.com", roles="admin,analyst"),
        MockUser(id=2, username="analyst1", email="analyst1@bank.com", roles="fraud_analyst"),
    ]
    _mock_session._next_id = 3
    _mock_session._added = []


app.dependency_overrides[get_db] = override_db


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
