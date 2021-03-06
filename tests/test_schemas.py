from os import getenv
import pytest
from dj_gui_api_server.DJGUIAPIServer import app
import datajoint as dj


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def token(client):
    yield client.post('/api/login', json=dict(databaseAddress=getenv('TEST_DB_SERVER'),
                                              username=getenv('TEST_DB_USER'),
                                              password=getenv('TEST_DB_PASS'))).json['jwt']


@pytest.fixture
def connection():
    dj.config['safemode'] = False
    connection = dj.conn(host=getenv('TEST_DB_SERVER'),
                         user=getenv('TEST_DB_USER'),
                         password=getenv('TEST_DB_PASS'), reset=True)
    schema1 = dj.Schema('schema1', connection=connection)
    @schema1
    class TableA(dj.Manual):
        definition = """
        id: int
        ---
        name: varchar(30)
        """

    schema2 = dj.Schema('schema2', connection=connection)
    @schema2
    class TableB(dj.Manual):
        definition = """
        id: int
        ---
        number: float
        """
    yield connection
    schema1.drop()
    schema2.drop()
    connection.close()
    dj.config['safemode'] = True


def test_schemas(token, client, connection):
    REST_schemas = client.get('/api/list_schemas',
                              headers=dict(
                                  Authorization=f'Bearer {token}')).json['schemaNames']
    expected_schemas = dj.list_schemas(connection=connection)
    assert set(REST_schemas) == set(expected_schemas)
