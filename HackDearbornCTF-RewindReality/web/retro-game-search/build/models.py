from database import Base
from sqlalchemy import Column, Integer, String

class Game(Base):
    __tablename__ = "games"
    rank = Column(Integer, primary_key=True)
    release_date = Column(String(4), nullable=False)
    title = Column(String(100), unique=True, nullable=False)

    def __init__(self, rank=None, release_date=None, title=None):
        self.rank = rank
        self.release_date = release_date
        self.title = title

class Flag(Base):
    __tablename__ = "flag"
    flag = Column(String(40), primary_key=True)

    def __init__(self, flag=None):
        self.flag = flag