from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///databases/portfolio.db")
Base = declarative_base()


class Users(Base):
    """Class of database table."""

    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    telegram_address = Column(Integer)
    company_symbol = Column(String)


def add_users_ticker(telegram_address, company_symbol):
    """Add to database user's telegram id and company's\
    symbol from his portfolio.

    Database's path is src/databases/portfolio.db
    :param telegram_address: user's telegram id.
    :param company_symbol: symbol of company.
    :return:
    """
    current_user = Users(telegram_address=telegram_address,
                         company_symbol=company_symbol)
    session = sessionmaker(bind=engine)()
    session.add(current_user)
    session.commit()
