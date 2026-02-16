# Copyright (c) 2026 Xist.GG LLC

from fastapi.testclient import TestClient
from app.main import app
from app import storage
import shutil
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_storage():
    """Clean storage before each test."""
    shutil.rmtree("data", ignore_errors=True)
    storage.init_storage()
    yield
    shutil.rmtree("data", ignore_errors=True)

def test_create_and_reveal_secret():
    # 1. Create Secret
    content = "This is a super secret message."
    response = client.post("/create", data={"content": content})
    assert response.status_code == 200
    assert "Your secret link is ready." in response.text
    
    # Extract secret UUID and Key from link in HTML?
    # Or just mock the random/uuid generation?
    # The response is HTML, parsing is hard.
    # But wait, the template renders `{{ link }}`.
    # We can inspect `storage` directly to find the UUID.
    
    # Extract secret UUID and Key from link in HTML using regex
    import re
    # Look for http://testserver/secret/...
    match = re.search(r'http://testserver/secret/([a-fA-F0-9-]+)#([\w=-]+)', response.text)
    assert match, "Generated link not found in response"
    
    secret_uuid = match.group(1)
    key = match.group(2)
    
    # 2. Visit Secret Page (GET)
    response = client.get(f"/secret/{secret_uuid}")
    assert response.status_code == 200
    assert "Reveal Secret" in response.text

    # 3. Reveal (POST)
    response = client.post(f"/secret/{secret_uuid}", data={"key": key})
    assert response.status_code == 200
    assert content in response.text
    
    # 4. Burn Check
    # Try to reveal again
    response = client.post(f"/secret/{secret_uuid}", data={"key": key})
    # Should show error or 404 (my code returns 200 with error message)
    # The message is "Secret not found or already burned."
    assert "Secret not found or already burned." in response.text
    
    # Check file is gone
    if storage.STORAGE_DIR.exists():
        assert not (storage.STORAGE_DIR / secret_uuid).exists()

def test_invalid_key():
    # Create manually
    content = "test"
    # We need to use app internals to setup state if we don't go through /create
    from app import crypto
    key = crypto.generate_key()
    encrypted = crypto.encrypt(content, key)
    import uuid
    u = str(uuid.uuid4())
    storage.save(u, encrypted)
    
    # Attempt reveal with wrong key
    wrong_key = crypto.generate_key()
    response = client.post(f"/secret/{u}", data={"key": wrong_key})
    
    # Should show error
    assert "Invalid key or data corruption" in response.text
    # And file should be gone (burn on attempt?)
    # My code: `storage.delete(uuid)` happens BEFORE decryption attempt.
    # So yes, burned.
    assert not (storage.STORAGE_DIR / u).exists()
