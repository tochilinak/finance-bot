from abc import ABC, abstractmethod
import logging
import datetime


class APIQuery(ABC):

    @property
    def error_return(self):
        """Make sure error_return is implemented."""
        raise NotImplementedError

    @abstractmethod
    def get_server_response(self):
        """Make query and return JSON with response."""
        pass

    @abstractmethod
    def result(self, resp):
        """Process response and return needed data."""
        pass

    report_list = []

    def make_query(self):
        """Make query and report error."""
        resp = ""
        try:
            resp = self.get_server_response()
            return self.result(resp)
        except Exception as e:
            logging.error(f"Query failed: {self.__class__.__name__} "
                          f"with parameters {self.report_list}\n"
                          f"Exception: {type(e).__name__} {e}\n"
                          "response:\n" + str(resp)[:150])
            return self.error_return


def query_function_factory(QueryClass):
    def func(*args):
        query_object = QueryClass(*args)
        return query_object.make_query()
    return func


def parse_date(date):
    """Parse string with date to datetime object.

    :param date: type - string.
    :return: type - datetime.
    """
    date_list = list(map(int, date.split('-')))
    return datetime.datetime(date_list[0], date_list[1], date_list[2])
