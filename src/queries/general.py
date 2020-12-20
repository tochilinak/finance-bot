from abc import ABC, abstractmethod
import logging
import datetime
from requests import Session
from dataclasses import dataclass, field


@dataclass
class QueryData:
    """Class for stroring data that is needed to make requests."""

    symbol: str = None
    start_date: str = None
    end_date: str = None
    name: str = None
    result: dict = field(default_factory=dict) # for asynchronous requests


class APIQuery(ABC):

    def set_report(self):
        self.report_list = []

    def __init__(self, session, query_data, query_data_id=-1, query_type=None):
        self.session = session
        if query_data.symbol:
            self.symbol = query_data.symbol.upper()
        self.start = query_data.start_date
        self.end = query_data.end_date
        self.name = query_data.name
        self.query_data_id = query_data_id
        self.query_type = query_type
        self.set_report()

    @property
    def empty_return(self):
        """Make sure empty_return is implemented."""
        raise NotImplementedError

    @abstractmethod
    def get_server_response(self):
        """Make query and record into self.response."""
        pass

    @abstractmethod
    def process_json(self, resp):
        """Process JSON and return needed data."""
        pass

    def get_result(self):
        """Try to process and report error."""
        resp = ""
        try:
            resp = self.response.json()
            return self.process_json(resp)
        except Exception as e:
            logging.error(f"Query failed: {self.__class__.__name__} "
                          f"with parameters {self.report_list}\n"
                          f"Exception: {type(e).__name__} {e}\n"
                          "response:\n" + str(resp)[:150])
            return self.empty_return


def query_function_factory(QueryClass):
    def func(query_data):
        query_object = QueryClass(Session(), query_data)
        query_object.get_server_response()
        return query_object.get_result()
    return func
