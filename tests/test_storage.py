from storage import save_to_txt


def test_save_creates_directory_and_appends(tmp_path):
    file = tmp_path / "outputs" / "research_output.txt"
    save_to_txt('{"topic": "Sample"}', file)
    save_to_txt('{"topic": "Second"}', file)
    content = file.read_text(encoding="utf-8")
    assert content.count("--- Research Output ---") == 2
    assert '"topic": "Sample"' in content
    assert '"topic": "Second"' in content
