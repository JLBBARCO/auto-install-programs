import src.lib.json as json_lib


def test_normalize_json_payload_handles_invalid_programs():
    payload = {"name": "Essentials", "description": "d", "programs": "invalid"}
    normalized = json_lib._normalize_json_payload(payload)

    assert normalized["name"] == "Essentials"
    assert normalized["description"] == "d"
    assert normalized["programs"] == []


def test_build_repo_raw_url_normalizes_backslashes_and_leading_slash():
    url = json_lib._build_repo_raw_url(r"/install\windows\essentials.json")
    assert url.endswith("install/windows/essentials.json")


def test_merge_programs_deduplicates_by_id_case_insensitive():
    primary = [
        {"name": "Git", "id": "Git.Git"},
        {"name": "VSCode", "id": "Microsoft.VisualStudioCode"},
    ]
    secondary = [
        {"name": "Git 2", "id": "git.git"},
        {"name": "7zip", "id": "7zip.7zip"},
        "invalid",
        {"name": "", "id": "bad"},
    ]

    merged = json_lib._merge_programs(primary, secondary)
    ids = [item["id"] for item in merged]

    assert ids == ["Git.Git", "Microsoft.VisualStudioCode", "7zip.7zip"]
