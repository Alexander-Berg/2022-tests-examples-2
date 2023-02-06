# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
)
from sqlalchemy.schema import (
    Column,
    MetaData,
    PrimaryKeyConstraint,
    Table,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    Integer,
    String,
)


metadata = MetaData()

user_table = Table(
    'user_table',
    metadata,
    Column('uid', BigInteger, nullable=False),
    Column('login', String, nullable=False),
    Column('password', String, nullable=False),
    Column('locked_until', DateTime, nullable=True, default=datetime.now),
    Column('delete_at', DateTime, nullable=True),
    Column('env', String, nullable=False),
    PrimaryKeyConstraint('uid', 'env')
)

tag_table = Table(
    'tag_table',
    metadata,
    Column('tag_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('tag', String, nullable=False, unique=True),
)

user_tags_table = Table(
    'user_tags_table',
    metadata,
    Column('uid', BigInteger, nullable=False),
    Column('tag_id', Integer, nullable=False),
    Column('env', String, nullable=False),
    ForeignKeyConstraint(('uid', 'env'), ('user_table.uid', 'user_table.env'), ondelete="CASCADE"),
    PrimaryKeyConstraint('uid', 'tag_id', 'env')
)

consumer_table = Table(
    'consumer_table',
    metadata,
    Column('consumer_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('consumer_name', String, nullable=False, unique=True),
)

client_table = Table(
    'client_table',
    metadata,
    Column('login_id', BigInteger, primary_key=True, nullable=False),
    Column('login', String, nullable=False, unique=True),
)

consumer_clients_table = Table(
    'consumer_clients_table',
    metadata,
    Column('login', BigInteger, ForeignKey('client_table.login', ondelete="CASCADE"), nullable=False),
    Column('consumer_name', String, ForeignKey('consumer_table.consumer_name', ondelete="CASCADE"), nullable=False),
    Column('role', String, nullable=False),
    PrimaryKeyConstraint('login', 'consumer_name', 'role')
)

consumer_test_accounts_table = Table(
    'consumer_test_accounts_table',
    metadata,
    Column('uid', BigInteger, nullable=False),
    Column('env', String, nullable=False),
    Column('consumer_name', String, ForeignKey('consumer_table.consumer_name', ondelete="CASCADE"), nullable=False),
    ForeignKeyConstraint(('uid', 'env'), ('user_table.uid', 'user_table.env'), ondelete="CASCADE"),
    PrimaryKeyConstraint('uid', 'consumer_name', 'env')
)
