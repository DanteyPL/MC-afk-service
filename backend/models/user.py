from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    ign = Column(String, unique=True)
    store_password = Column(Boolean, default=False)
    encrypted_ms_email = Column(String, nullable=True)
    encrypted_ms_credentials = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)

class Whitelist(Base):
    __tablename__ = "whitelist"

    id = Column(Integer, primary_key=True, index=True)
    ign = Column(String, unique=True, index=True)
    approved = Column(Boolean, default=False)

class ItemStat(Base):
    __tablename__ = "item_stats"

    id = Column(Integer, primary_key=True, index=True)
    ign = Column(String, index=True)
    item_name = Column(String)
    rarity = Column(String)  # Common, Uncommon, Rare, Epic, Legendary, Ultra
    count = Column(Integer, default=0)
    shiny_count = Column(Integer, default=0)
