import pytest

def test_api_returns_test_2(client):
    response = client.get("/test-2")
    
def test_hello_returns_correct_text(client):
    response = client.get("/hello")
    assert "Hello" in response.textx