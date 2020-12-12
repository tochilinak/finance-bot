from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///portfolio.db")
Base = declarative_base()


class Users(Base):
    """Class of database table."""

    __tablename__ = 'Users'

    telegram_address = Column(Integer, primary_key=True)
    company_symbol = Column(String, primary_key=True)


class Operations(Base):
    """Table with buy-sell operations."""

    __tablename__ = 'Operations'

    id = Column(Integer, primary_key=True)
    telegram_address = Column(Integer)
    company_symbol = Column(String)
    count_of_stocks = Column(Integer)
    price = Column(Integer)
    date = Column(String)
    operation_type = Column(Integer)


# deleting table(s)
#Base.metadata.drop_all(bind=engine, tables=[Operations.__table__])

# create tables that don't exist
Base.metadata.create_all(bind=engine)


def add_users_ticker(telegram_address, company_symbol):
    """Add to database user's telegram id and company's\
    symbol from his portfolio.

    Database's path is src/databases/portfolio.db
    :param telegram_address: user's telegram id as integer.
    :param company_symbol: symbol of company as string.
    """
    current_user = Users(telegram_address=telegram_address,
                         company_symbol=company_symbol)
    session = sessionmaker(bind=engine)()
    session.merge(current_user)
    session.commit()


def list_users_tickers(telegram_address):
    """Find all tickers from user's portfolio.

    :param telegram_address: user's telegram id as integer.
    :return: list of tickers as integers.
    """
    session = sessionmaker(bind=engine)()
    # SQLAlchemy Query object (contains db response)
    q = session.query(Users).filter(Users.telegram_address ==
                                    telegram_address)
    result = [record.company_symbol for record in q]
    session.commit()
    return result


def delete_users_ticker(telegram_address, symbol):
    """Delete a record with user and current ticker.

    :param telegram_address: user's telegram id as integer.
    :param symbol: symbol of company as string.
    """
    session = sessionmaker(bind=engine)()
    # SQLAlchemy Query object (contains db response)
    q = session.query(Users).filter(Users.telegram_address ==
                                    telegram_address,
                                    Users.company_symbol ==
                                    symbol).first()
    if q is not None:
        session.delete(q)
    session.commit()


def add_operation(telegram_address, symbol, count, price, date,
                  operation_type):
    """Add operation to the table.

    Types of parameters:
    :param telegram_address: Integer;
    :param symbol: String;
    :param count: Integer;
    :param price: Integer;
    :param date: String;
    :param operation_type: Integer; 0 of it's buy operation, 1 in another case.
    """

    current_operation = Operations(telegram_address=telegram_address,
                                   company_symbol=symbol, count_of_stocks=
                                   count, price=price, date=date,
                                   operation_type=operation_type)

    session = sessionmaker(bind=engine)()
    session.add(current_operation)
    session.commit()
