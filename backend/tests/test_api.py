from io import BytesIO


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_auth_register_login_and_duplicate(client):
    payload = {"email": "person@example.com", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409
    assert client.post("/api/auth/login", json=payload).status_code == 200
    assert client.post("/api/auth/login", json={**payload, "password": "bad"}).status_code == 401


def test_rejects_bad_token(client):
    response = client.get("/api/files", headers={"Authorization": "Bearer nope"})
    assert response.status_code == 401


def test_upload_audio_chat_timestamps_and_media(client, auth_headers):
    upload = client.post(
        "/api/files/upload",
        headers=auth_headers,
        files={"upload": ("meeting.mp3", BytesIO(b"fake audio"), "audio/mpeg")},
    )
    assert upload.status_code == 200
    file_id = upload.json()["id"]
    assert upload.json()["transcription_status"] == "unavailable"
    assert "Media uploaded successfully" in upload.json()["summary"]

    listed = client.get("/api/files", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["filename"] == "meeting.mp3"

    summary = client.get(f"/api/files/{file_id}/summary", headers=auth_headers)
    assert summary.json()["summary"]

    answer = client.post(
        "/api/chat/ask",
        headers=auth_headers,
        json={"file_id": file_id, "question": "What was discussed?"},
    )
    assert answer.status_code == 200
    assert answer.json()["citations"] == []

    timestamps = client.get(
        f"/api/files/{file_id}/timestamps?topic=transcription",
        headers=auth_headers,
    )
    assert timestamps.status_code == 200
    assert timestamps.json()["matches"] == []

    media = client.get(f"/api/files/{file_id}/media", headers=auth_headers)
    assert media.status_code == 200
    assert media.content == b"fake audio"


def test_upload_rejects_unsupported_file(client, auth_headers):
    response = client.post(
        "/api/files/upload",
        headers=auth_headers,
        files={"upload": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_file_ownership_is_enforced(client, auth_headers):
    uploaded = client.post(
        "/api/files/upload",
        headers=auth_headers,
        files={"upload": ("clip.mp4", BytesIO(b"fake video"), "video/mp4")},
    )
    file_id = uploaded.json()["id"]
    second = client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "password": "password123"},
    ).json()["access_token"]
    response = client.get(f"/api/files/{file_id}/summary", headers={"Authorization": f"Bearer {second}"})
    assert response.status_code == 404


def test_missing_media_file_returns_404(client, auth_headers):
    uploaded = client.post(
        "/api/files/upload",
        headers=auth_headers,
        files={"upload": ("clip.mp4", BytesIO(b"fake video"), "video/mp4")},
    )
    file_id = uploaded.json()["id"]
    from app.database import SessionLocal
    from app.models import UploadedFile

    with SessionLocal() as db:
        record = db.get(UploadedFile, file_id)
        assert record
        record.storage_path = "missing-file.mp4"
        db.commit()

    response = client.get(f"/api/files/{file_id}/media", headers=auth_headers)
    assert response.status_code == 404


def test_streaming_chat(client, auth_headers):
    uploaded = client.post(
        "/api/files/upload",
        headers=auth_headers,
        files={"upload": ("lesson.wav", BytesIO(b"fake audio"), "audio/wav")},
    )
    file_id = uploaded.json()["id"]
    with client.stream(
        "GET",
        f"/api/chat/stream?file_id={file_id}&question=transcription",
        headers=auth_headers,
    ) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert "data:" in body
    assert "[DONE]" in body
