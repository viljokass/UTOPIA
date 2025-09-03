from desdeo.api.models import User, UserRole
from desdeo.api.db import get_session
from desdeo.api.routers.user_authentication import get_password_hash

# testing
session = next(get_session())
user = User(
    username="testi",
    password_hash=get_password_hash("testi"),
    role=UserRole.dm
)
session.add(user)
session.commit()
session.close()