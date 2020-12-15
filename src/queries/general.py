from abc import ABC, abstractmethod
import logging
import datetime
from requests import Session


class APIQuery(ABC):

    def __init__(self, session):
        self.session = session

    @property
    def error_return(self):
        """Make sure error_return is implemented."""
        raise NotImplementedError

    @abstractmethod
    def get_server_response(self):
        """Make query and record into self.response."""
        pass

    @abstractmethod
    def process_json(self, resp):
        """Process JSON and return needed data."""
        pass

    report_list = []

    def get_result(self, future=False):
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
            return self.error_return


def query_function_factory(QueryClass):
    def func(*args):
        query_object = QueryClass(Session(), *args)
        query_object.get_server_response()
        return query_object.get_result()
    return func


def parse_date(date):
    """Parse string with date to datetime object.

    :param date: type - string.
    :return: type - datetime.
    """
    date_list = list(map(int, date.split('-')))
    return datetime.datetime(date_list[0], date_list[1], date_list[2])
