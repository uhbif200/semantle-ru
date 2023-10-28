import datetime

from fastapi_users_db_sqlalchemy.generics import GUID, TIMESTAMPAware, now_utc

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=now_utc),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False)
)

accesstoken = Table(
    "accesstoken",
    metadata,
    Column("token", String(length=43), primary_key=True),
    Column("created_at", TIMESTAMP, default=now_utc),
    Column("user_id", Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
        
)