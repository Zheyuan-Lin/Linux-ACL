from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for user roles
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=True)  # Can be null for LDAP users
    ldap_dn = Column(String, unique=True)  # LDAP Distinguished Name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    owned_projects = relationship("Project", back_populates="pi")
    memberships = relationship("ProjectMember", back_populates="user")

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # 'pi', 'researcher'
    description = Column(String)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    storage_path = Column(String, nullable=False)  # Base path for project storage
    created_at = Column(DateTime, default=datetime.utcnow)
    pi_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    pi = relationship("User", back_populates="owned_projects")
    members = relationship("ProjectMember", back_populates="project")

class ProjectMember(Base):
    __tablename__ = 'project_members'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    access_level = Column(String, nullable=False)  # 'read', 'write', 'admin'
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="memberships") 