from sqlalchemy import create_engine
DATABASE_URL = "sqlite:///./masai.db"
engine = create_engine(DATABASE_URL, echo=True)
