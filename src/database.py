from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from enum import IntEnum
from api_requests import get_currency, current_cost, get_period_data_of_cost
import csv
import datetime


engine = create_engine("sqlite:///portfolio.db")
Base = declarative_base()


class Users(Base):
    """Class of database table."""

    __tablename__ = 'Users'

    telegram_address = Column(Integer, primary_key=True)
    company_symbol = Column(String, primary_key=True)


class OperationType(IntEnum):
    BUY_OPERATION = 0
    SELL_OPERATION = 1


class Operations(Base):
    """Table with buy-sell operations."""

    __tablename__ = 'Operations'

    id = Column(Integer, primary_key=True)
    telegram_address = Column(Integer)
    company_symbol = Column(String)
    count_of_stocks = Column(Integer)
    price = Column(Integer)
    currency = Column(String)
    date = Column(String)
    operation_type = Column(Integer)


# deleting table(s)
# Base.metadata.drop_all(bind=engine, tables=[Operations.__table__])

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
    q = session.query(Users).get([telegram_address, symbol])
    if q is not None:
        session.delete(q)
    session.commit()


def add_operation(telegram_address, symbol, count, date, operation_type):
    """Add operation to the table.

    Types of parameters:
    :param telegram_address: Integer;
    :param symbol: String;
    :param count: Integer;
    :param date: String;
    :param operation_type: enum operation_type object.
    """
    price = get_period_data_of_cost(date, date, symbol)[1][0]
    currency = get_currency(symbol)
    current_operation = Operations(telegram_address=telegram_address,
                                   company_symbol=symbol,
                                   count_of_stocks=count, price=price,
                                   currency=currency, date=date,
                                   operation_type=operation_type.value)

    session = sessionmaker(bind=engine)()
    session.add(current_operation)
    session.commit()


def delete_operation(operation_id):
    """Delete operation with current id.

    :param operation_id: id of operation.
    """
    session = sessionmaker(bind=engine)()
    # SQLAlchemy Query object (contains db response)
    q = session.query(Operations).get(operation_id)
    if q is not None:
        session.delete(q)
    session.commit()


def get_list_of_operations(telegram_address):
    """Make .csv file with all user's operations.

    :param telegram_address: user's address.
    """
    session = sessionmaker(bind=engine)()
    headers = [x.name for x in Operations.__table__.columns]
    q = session.query(Operations).filter(Operations.telegram_address
                                         == telegram_address)
    content = [[x.id, x.telegram_address, x.company_symbol,
                x.count_of_stocks, x.price, x.currency, x.date, x.operation_type]
               for x in q]
    with open("out.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows([headers] + content)
    session.commit()


def get_period_balance(user_data):
    companies_tickers = [x.company_symbol for x in user_data]
    balance = dict.fromkeys(companies_tickers, 0)
    for record in user_data:
        if record.operation_type == OperationType.BUY_OPERATION:
            balance[record.company_symbol] -= record.price * record.count_of_stocks
        else:
            balance[record.company_symbol] += record.price * record.count_of_stocks
    return balance


def get_period_count_of_stocks(user_data):
    companies_tickers = [x.company_symbol for x in user_data]
    count_of_stocks = dict.fromkeys(companies_tickers, 0)
    for record in user_data:
        if record.operation_type == OperationType.BUY_OPERATION:
            count_of_stocks[record.company_symbol] += record.count_of_stocks
        else:
            count_of_stocks[record.company_symbol] -= record.count_of_stocks
    return count_of_stocks



def get_current_profit(telegram_address):
    session = sessionmaker(bind=engine)()
    user_data = session.query(Operations).filter(Operations.telegram_address
                                                 == telegram_address)
    session.commit()
    companies_tickers = [x.company_symbol for x in user_data]
    balance = get_period_balance(user_data)
    count_of_stocks = get_period_count_of_stocks(user_data)
    companies_info = dict.fromkeys(companies_tickers)
    for ticker in companies_tickers:
        ticker_stocks_info = current_cost(ticker)
        current_stock_cost = ticker_stocks_info[0] * count_of_stocks[ticker]
        last_update = ticker_stocks_info[1]
        companies_info[ticker] = [current_stock_cost, current_stock_cost + balance[ticker], last_update]
    currencies = [x.currency for x in user_data]
    currencies_info = {x: [0, 0] for x in currencies}
    for ticker in companies_info:
        current_currency = get_currency(ticker)
        currencies_info[current_currency][0] += companies_info[ticker][0]
        currencies_info[current_currency][1] += companies_info[ticker][1]
    return companies_info, currencies_info


def get_period_profit(begin_date, end_date, telegram_address):
    session = sessionmaker(bind=engine)()
    user_data = session.query(Operations).filter(and_(Operations.telegram_address
                                                 == telegram_address, Operations.date
                                                      >= begin_date, Operations.date
                                                      <= end_date)).order_by(Operations.date)
    session.commit()
    result = {x.currency: [[], []] for x in user_data}
    start_ordinal = datetime.datetime.strptime(begin_date, "%Y-%m-%d").toordinal()
    end_ordinal = datetime.datetime.strptime(end_date, "%Y-%m-%d").toordinal()
    for date_ordinal in range(start_ordinal, end_ordinal + 1):
        current_balance = get_period_balance(user_data)
        current_count_of_stocks = get_period_count_of_stocks(user_data)
        for x in result:
            result[x][0].append(datetime.datetime.fromordinal(date_ordinal))
            result[x][1].append(current_balance[x] if x in current_balance.keys() else 0)
        for ticker in current_count_of_stocks:
            current_currency = get_currency(ticker)
            current_cost = get_period_data_of_cost(datetime.datetime.
                                                   fromordinal(date_ordinal - 14)
                                                   .isoformat()[:10], datetime.datetime
                                                   .fromordinal(date_ordinal)
                                                   .isoformat()[:10], ticker)[1]
            result[current_currency][1][-1] += current_count_of_stocks[ticker] * current_cost[-1]
    return result

