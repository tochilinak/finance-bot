from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from enum import IntEnum
from api_requests import *
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
    if len(get_period_data_of_cost(date, date, symbol)[1]) == 0:
        # Date isn't a trade day.
        return False
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
    return True


def delete_operation(telegram_address, operation_id):
    """Delete operation with current id.

    :param operation_id: id of operation.
    return True if successful and False otherwise.
    """
    session = sessionmaker(bind=engine)()
    # SQLAlchemy Query object (contains db response)
    q = session.query(Operations).get(operation_id)

    success = False
    if q is not None and q.telegram_address == telegram_address:
        session.delete(q)
        success = True

    session.commit()
    return success


def get_list_of_operations(telegram_address):
    """Make .csv file with all user's operations.

    :param telegram_address: user's address.
    """
    session = sessionmaker(bind=engine)()
    headers = [x.name for x in Operations.__table__.columns]
    q = session.query(Operations).filter(Operations.telegram_address
                                         == telegram_address)
    content = [[x.id, x.telegram_address, x.company_symbol,
                x.count_of_stocks, x.price, x.currency, x.date,
                OperationType(x.operation_type).name] for x in q]
    with open("out.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows([headers] + content)
    session.commit()


def get_prefix_balance(user_data, end_date="9999-99-99"):
    """Get user's balance by a period contained in user_data.

    :param user_data: SQLAlchemy query object.
    :param end_date: date till we watch values.
    :return: dictionary {company symbol: user's balance}.
    """
    companies_tickers = [x.company_symbol for x in user_data]
    balance = dict.fromkeys(companies_tickers, 0)
    for record in user_data:
        if record.date > end_date:
            break
        if record.operation_type == OperationType.BUY_OPERATION:
            balance[record.company_symbol] -= record.price *\
                                              record.count_of_stocks
        else:
            balance[record.company_symbol] += record.price *\
                                              record.count_of_stocks
    return balance


def get_prefix_count_of_stocks(user_data, end_date="9999-99-99"):
    """Get count of stocks from every company from a\
    period contained in user_data.

    :param user_data: SQLAlchemy query object.
    :param end_date: date till we watch values.
    :return: dictionary {company symbol: count of stocks bought by user}.
    """
    companies_tickers = [x.company_symbol for x in user_data]
    count_of_stocks = dict.fromkeys(companies_tickers, 0)
    for record in user_data:
        if record.date > end_date:
            break
        if record.operation_type == OperationType.BUY_OPERATION:
            count_of_stocks[record.company_symbol] += record.count_of_stocks
        else:
            count_of_stocks[record.company_symbol] -= record.count_of_stocks
    return count_of_stocks


def get_current_profit(telegram_address):
    """Get last updated stocks' costs and user's profit.

    :return: Dict. companies_info {company symbol, [actual cost of
    stocks, user's profit, date of last update]}, dict. curriencies_info
    {currency: [summary actual costs of stocks bought in this currency,
    user's profit on this currency]}.
    """
    session = sessionmaker(bind=engine)()
    user_data = session.query(Operations).filter(Operations.telegram_address
                                                 == telegram_address)
    session.commit()
    companies_tickers = set(x.company_symbol for x in user_data)
    balance = get_prefix_balance(user_data)
    count_of_stocks = get_prefix_count_of_stocks(user_data)
    companies_info = dict.fromkeys(companies_tickers)

    query_data_list = [QueryData(symbol=x) for x in companies_tickers]
    async_request(query_data_list, [QueryType.CURRENCY, QueryType.CURRENT_COST])

    for query_data in query_data_list:
        ticker = query_data.symbol
        ticker_stocks_info = query_data.result[QueryType.CURRENT_COST]
        current_stock_cost = ticker_stocks_info[0] * count_of_stocks[ticker]
        last_update = ticker_stocks_info[1]
        companies_info[ticker] = [current_stock_cost, current_stock_cost +
                                  balance[ticker], last_update]
    currencies_info = {x.currency: [0, 0] for x in user_data}
    for query_data in query_data_list:
        ticker = query_data.symbol
        current_currency = query_data.result[QueryType.CURRENCY]
        currencies_info[current_currency][0] += companies_info[ticker][0]
        currencies_info[current_currency][1] += companies_info[ticker][1]
    return companies_info, currencies_info


def get_period_profit(begin_date, end_date, telegram_address):
    """Get period data of user's profit.

    :return: dict. {currency: list of datetime objects, list of user's profit}.
    """
    session = sessionmaker(bind=engine)()
    user_data = session.query(Operations).\
        filter(and_(Operations.telegram_address == telegram_address,
                    Operations.date <= end_date)).order_by(Operations.date)
    session.commit()
    companies_symbols = {x.company_symbol for x in user_data}
    if len(companies_symbols) == 0:
        # User hadn't bought any stock by this period, so profit
        # is constant 0. Not interesting.
        return None
    # To make less api requests.
    query_data_list = [QueryData(symbol=x, start_date=begin_date,
                                 end_date=end_date) for x in companies_symbols]
    async_request(query_data_list, [QueryType.CURRENCY, QueryType.PERIOD_COST])
    currencies_for_companies = {x.symbol: x.result[QueryType.CURRENCY] for x
                                in query_data_list}
    companies_stocks_period_cost = {x.symbol: x.result[QueryType.PERIOD_COST]
                                    for x in query_data_list}
    result = {x.currency: [[], []] for x in user_data}
    # Make the Ox values by dates from union of Ox values from each company.
    dates_set = set()
    for symbol in companies_symbols:
        dates_set = dates_set.union(set(companies_stocks_period_cost[symbol][0]))
    dates_list = list(dates_set)
    dates_list.sort()

    def get_cost_by_date(date_cost, symbol):
        """Get cost of stocks of a company bu current date.

        :param date_cost: date from which we want to know stock cost.
        :param symbol: owner of stocks cost which we want to know.
        :return: closely cost of stock.
        """
        current_costs = companies_stocks_period_cost[symbol]
        result_cost = current_costs[1][0]
        for i in range(len(current_costs[0])):
            if current_costs[0][i] <= date_cost:
                result_cost = current_costs[1][i]
        return result_cost

    for date in dates_list:
        current_balance = get_prefix_balance(user_data, date.isoformat()[:10])
        current_count_of_stocks = get_prefix_count_of_stocks(user_data, date.
                                                             isoformat()[:10])
        for x in result:
            result[x][0].append(date)
            result[x][1].append(0)
        for ticker in current_count_of_stocks:
            current_currency = currencies_for_companies[ticker]
            current_cost = get_cost_by_date(date, ticker)
            result[current_currency][1][-1] += current_balance[ticker]
            result[current_currency][1][-1] +=\
                current_count_of_stocks[ticker] * current_cost
    return result
