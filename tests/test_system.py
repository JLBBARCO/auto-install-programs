import src.lib.system as system


def test_name_so_windows(monkeypatch):
    monkeypatch.setattr(system.platform, "system", lambda: "Windows")
    assert system.nameSO() == "Windows"
    assert system.installation() == "bat"


def test_name_so_linux(monkeypatch):
    monkeypatch.setattr(system.platform, "system", lambda: "Linux")
    assert system.nameSO() == "Linux"
    assert system.installation() == "sh"


def test_name_so_unknown(monkeypatch):
    monkeypatch.setattr(system.platform, "system", lambda: "Solaris")
    assert system.nameSO() == "Unknown"
    assert system.installation() == "Unknown"
