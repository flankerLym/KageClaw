import json
import time

from shibaclaw.brain.manager import PackManager, Session


def test_pack_manager_reloads_cached_session_when_file_changes(tmp_path):
    manager = PackManager(tmp_path)
    session = Session(key="webui:test")
    session.metadata["model"] = "openrouter/google/gemma-4-31b-it"
    manager.save(session)

    cached = manager.get_or_create("webui:test")
    assert cached.metadata["model"] == "openrouter/google/gemma-4-31b-it"

    path = manager._get_session_path("webui:test")
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata = json.loads(lines[0])
    metadata["metadata"]["model"] = "github_copilot/gpt-4.1"
    time.sleep(0.05)
    path.write_text("\n".join([json.dumps(metadata, ensure_ascii=False), *lines[1:]]) + "\n", encoding="utf-8")

    reloaded = manager.get_or_create("webui:test")

    assert reloaded.metadata["model"] == "github_copilot/gpt-4.1"


def test_pack_manager_save_append_vs_full_rewrite(tmp_path):
    manager = PackManager(tmp_path)
    session = manager.get_or_create("webui:test")
    session.add_message("user", "Hello first")
    session.add_message("assistant", "Hi there")
    manager.save(session)

    path = manager._get_session_path("webui:test")
    content_after_save1 = path.read_text(encoding="utf-8")
    lines1 = content_after_save1.splitlines()
    assert len(lines1) == 3  # 1 metadata + 2 messages
    assert "_type" in lines1[0]
    assert "Hello first" in lines1[1]

    # Adding more messages should trigger fast append-only pathway
    session.add_message("user", "Hello second")
    manager.save(session)

    content_after_save2 = path.read_text(encoding="utf-8")
    lines2 = content_after_save2.splitlines()
    assert len(lines2) == 4  # 1 metadata + 3 messages
    assert "Hello second" in lines2[3]

    # Verify that metadata line at block 0 was not re-written/duplicated at list end
    meta_count = sum(1 for line in lines2 if "_type" in line)
    assert meta_count == 1

    # Now change metadata (should trigger safe full rewrite)
    session.metadata["modified"] = True
    manager.save(session)

    content_after_save3 = path.read_text(encoding="utf-8")
    lines3 = content_after_save3.splitlines()
    assert len(lines3) == 4
    assert '"modified": true' in lines3[0]
