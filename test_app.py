from app import app


def test_hello_ok():
    client = app.test_client()
    resp = client.get('/hello?name=TEST')
    assert resp.status_code == 200
    assert b'Hello, TEST!' in resp.data
