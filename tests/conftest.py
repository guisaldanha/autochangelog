import pytest


@pytest.fixture(autouse=True)
def _git_safe_directory_override(monkeypatch):
    """Avoid 'dubious ownership' failures when git repos created by the test
    suite are later touched by a different user/UID (common in CI containers),
    without touching any persisted git config on the machine.
    """
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('GIT_CONFIG_KEY_0', 'safe.directory')
    monkeypatch.setenv('GIT_CONFIG_VALUE_0', '*')
