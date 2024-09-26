import unittest

from mindsdb.integrations.handlers.ckan_handler.ckan_handler import CkanHandler
from mindsdb.api.executor.data_types.response_type import RESPONSE_TYPE


class CkanHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.kwargs = {
            "connection_data": {
                "url": "https://data.gov.au/data/"}
        }
        cls.handler = CkanHandler('test_ckan_handler', **cls.kwargs)

    def test_connect(self):
        self.handler.connect()

    def test_query(self):
        self.handler.query('SELECT * from "5c3914e6-413e-4a2c-b890-bf8efe3eabf2"')

    def test_disconnect(self):
        self.handler.disconnect()

    def test_get_tables(self):
        tables = self.handler.get_tables()
        print(tables)
        assert tables.type is not RESPONSE_TYPE.ERROR
