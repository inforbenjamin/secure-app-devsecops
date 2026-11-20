from app import app


def test_hello_ok():
    client = app.test_client()
    resp = client.get('/hello?name=TEST')
    assert resp.status_code == 200
    assert b'Hello, TEST!' in resp.data


def test_xss_is_blocked():
    client = app.test_client()
    resp = client.get('/hello?name=<script>alert(1)</script>')
    assert resp.status_code == 400
    assert b'<script>' not in resp.data


def test_security_headers_present():
    client = app.test_client()
    resp = client.get('/hello?name=TEST')
    assert resp.headers['X-Content-Type-Options'] == 'nosniff'
    assert 'Content-Security-Policy' in resp.headers
    assert resp.headers['X-Frame-Options'] == 'DENY'
