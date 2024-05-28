import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

# create connection url
def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

# create engine
engine = create_engine(database_connection_url(), pool_pre_ping=True)

# create object metadata
metadata_obj = sqlalchemy.MetaData()
player_points = sqlalchemy.Table("player_points", metadata_obj, autoload_with=engine)
