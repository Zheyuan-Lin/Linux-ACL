from typing import Optional, Dict, Any
import ldap
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.database import User, Role
from app.schemas.auth import UserLogin

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

def get_ldap_connection():
    """Create and return an LDAP connection"""
    try:
        conn = ldap.initialize(f"ldap://{settings.LDAP_SERVER}:{settings.LDAP_PORT}")
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        return conn
    except ldap.LDAPError as e:
        raise AuthenticationError(f"LDAP connection error: {str(e)}")

async def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
    """
    Authenticate a user using LDAP and update/create user in database
    """
    try:
        # Split username into parts
        if '@' not in login_data.username:
            raise AuthenticationError("Username must be in format: username@institution")
        
        user_id, institution = login_data.username.split('@')
        
        # Get LDAP connection
        conn = get_ldap_connection()
        
        # Create user DN from template
        user_dn = settings.LDAP_USER_DN_TEMPLATE.format(
            username=user_id,
            institution=institution
        )
        
        # Try to bind with user credentials
        try:
            conn.simple_bind_s(user_dn, login_data.password)
        except ldap.INVALID_CREDENTIALS:
            return None
        except ldap.LDAPError as e:
            raise AuthenticationError(f"LDAP authentication error: {str(e)}")
        
        # Search for user attributes
        base_dn = settings.LDAP_BASE_DN
        search_filter = f"(uid={user_id})"
        attributes = ['mail', 'cn', 'eduPersonAffiliation']
        
        try:
            result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attributes)
            if not result:
                raise AuthenticationError("User not found in LDAP")
                
            user_attrs = result[0][1]
            email = user_attrs.get('mail', [b''])[0].decode()
            name = user_attrs.get('cn', [b''])[0].decode()
            affiliations = [aff.decode() for aff in user_attrs.get('eduPersonAffiliation', [])]
            
            # Get or create user in database
            db_user = db.query(User).filter_by(username=login_data.username).first()
            if not db_user:
                db_user = User(
                    username=login_data.username,
                    email=email,
                    ldap_dn=user_dn,
                    is_active=True
                )
                db.add(db_user)
            
            # Update user roles based on LDAP affiliations
            pi_role = db.query(Role).filter_by(name="pi").first()
            researcher_role = db.query(Role).filter_by(name="researcher").first()
            
            # Clear existing roles
            db_user.roles = []
            
            # Assign roles based on LDAP affiliations
            if "faculty" in affiliations or "staff" in affiliations:
                db_user.roles.append(pi_role)
            if "researcher" in affiliations or "student" in affiliations:
                db_user.roles.append(researcher_role)
            
            # Update last login
            db_user.last_login = datetime.utcnow()
            
            db.commit()
            return db_user
            
        except ldap.LDAPError as e:
            raise AuthenticationError(f"LDAP search error: {str(e)}")
        finally:
            conn.unbind_s()
            
    except Exception as e:
        raise AuthenticationError(f"Authentication failed: {str(e)}")

async def create_user_token(user: User) -> Dict[str, Any]:
    """Create access token for user"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include roles in token payload
    role_names = [role.name for role in user.roles]
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "roles": role_names
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "roles": role_names
        }
    }
