from src.lib.installations import single_instance as si


def test_read_lock_file_returns_none_when_missing(monkeypatch, tmp_path):
    lock_path = tmp_path / "missing.lock"
    monkeypatch.setattr(si, "LOCK_FILE", str(lock_path))
    monkeypatch.setattr(si.log, "log", lambda *args, **kwargs: None)

    assert si._read_lock_file() is None


def test_write_and_read_lock_file(monkeypatch, tmp_path):
    lock_path = tmp_path / "instance.lock"
    monkeypatch.setattr(si, "LOCK_FILE", str(lock_path))
    monkeypatch.setattr(si.log, "log", lambda *args, **kwargs: None)

    si._write_lock_file(12345)

    assert lock_path.exists()
    assert si._read_lock_file() == 12345


def test_remove_lock_file(monkeypatch, tmp_path):
    lock_path = tmp_path / "instance.lock"
    lock_path.write_text("999", encoding="utf-8")

    monkeypatch.setattr(si, "LOCK_FILE", str(lock_path))
    monkeypatch.setattr(si.log, "log", lambda *args, **kwargs: None)

    si._remove_lock_file()

    assert not lock_path.exists()
