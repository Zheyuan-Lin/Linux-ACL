from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite-specific setting
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    from app.models.database import Base, Role, User
    Base.metadata.create_all(bind=engine)
    
    # Create default roles if they don't exist
    db = SessionLocal()
    try:
        # Check if roles exist
        pi_role = db.query(Role).filter_by(name="pi").first()
        researcher_role = db.query(Role).filter_by(name="researcher").first()
        
        # Create PI role if it doesn't exist
        if not pi_role:
            pi_role = Role(
                name="pi",
                description="Principal Investigator with full project management rights"
            )
            db.add(pi_role)
        
        # Create Researcher role if it doesn't exist
        if not researcher_role:
            researcher_role = Role(
                name="researcher",
                description="Researcher with project-specific access rights"
            )
            db.add(researcher_role)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Apply changes
init_db() 