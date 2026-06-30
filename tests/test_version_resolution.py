import sys


def test_version_prefers_pyproject_for_source_checkout(tmp_path, monkeypatch):
    import KAGECLAW

    repo_root = tmp_path / "repo"
    package_dir = repo_root / "KAGECLAW"
    package_dir.mkdir(parents=True, exist_ok=True)
    (repo_root / "README.md").write_text("# KAGECLAW\n", encoding="utf-8")
    (repo_root / "pyproject.toml").write_text(
        '[project]\nname = "KAGECLAW"\nversion = "1.2.3"\n',
        encoding="utf-8",
    )
    (package_dir / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(KAGECLAW, "__file__", str(package_dir / "__init__.py"))
    monkeypatch.setattr("importlib.metadata.version", lambda name: "9.9.9")
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert KAGECLAW._get_version() == "1.2.3"



def test_version_prefers_installed_metadata_over_packaged_manifest(tmp_path, monkeypatch):
    import KAGECLAW

    package_dir = tmp_path / "site-packages" / "KAGECLAW"
    (package_dir / "updater").mkdir(parents=True, exist_ok=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "updater" / "update_manifest.json").write_text(
        '{"version": "0.2.1"}',
        encoding="utf-8",
    )

    monkeypatch.setattr(KAGECLAW, "__file__", str(package_dir / "__init__.py"))
    monkeypatch.setattr("importlib.metadata.version", lambda name: "0.3.8")
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert KAGECLAW._get_version() == "0.3.8"


def test_version_prefers_manifest_for_frozen_bundle(tmp_path, monkeypatch):
    import KAGECLAW

    package_dir = tmp_path / "bundle" / "KAGECLAW"
    (package_dir / "updater").mkdir(parents=True, exist_ok=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "updater" / "update_manifest.json").write_text(
        '{"version": "0.4.0"}',
        encoding="utf-8",
    )

    monkeypatch.setattr(KAGECLAW, "__file__", str(package_dir / "__init__.py"))
    monkeypatch.setattr("importlib.metadata.version", lambda name: "0.3.8")
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    assert KAGECLAW._get_version() == "0.4.0"

