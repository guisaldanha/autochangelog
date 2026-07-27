import subprocess

import pytest

from AutoChangelog import AutoChangelog


def run_git(repo_path, *args):
    subprocess.check_call(['git', *args], cwd=str(repo_path))


@pytest.fixture
def git_repo(tmp_path):
    """A throwaway git repository, isolated from the user's global git config."""
    repo = tmp_path / 'repo'
    repo.mkdir()
    run_git(repo, 'init', '-q')
    run_git(repo, 'config', 'user.email', 'test@example.com')
    run_git(repo, 'config', 'user.name', 'Test User')
    run_git(repo, 'config', 'commit.gpgsign', 'false')
    return repo


def commit(repo, message, tag=None, author=None):
    """Create a commit with a unique file change, optionally tagging it."""
    marker = repo / 'file.txt'
    marker.write_text((marker.read_text() if marker.exists() else '') + 'x')
    run_git(repo, 'add', '.')
    args = ['commit', '-q', '-m', message]
    if author:
        args += ['--author', author]
    run_git(repo, *args)
    if tag:
        run_git(repo, 'tag', '-a', tag, '-m', 'Release ' + tag)


class TestPureHelpers:
    """These don't touch git or the filesystem - the constructor no longer does I/O."""

    def setup_method(self):
        self.ac = AutoChangelog()

    def test_getChangeType_with_prefix(self):
        assert self.ac.getChangeType('Added: something new') == 'Added'

    def test_getChangeType_without_prefix(self):
        assert self.ac.getChangeType('just a message') == ''

    def test_getChangeType_uses_first_colon_only(self):
        assert self.ac.getChangeType('Fixed: issue with a: colon') == 'Fixed'

    def test_getCommitMessage_with_prefix(self):
        assert self.ac.getCommitMessage('Added: something new') == 'Something new'

    def test_getCommitMessage_without_prefix(self):
        assert self.ac.getCommitMessage('just a message') == 'Just a message'

    def test_getTag_no_decoration_keeps_current(self):
        assert self.ac.getTag('', 'unreleased') == 'unreleased'

    def test_getTag_decoration_without_tag_keeps_current(self):
        assert self.ac.getTag(' (HEAD -> main)', '1.0.0') == '1.0.0'

    def test_getTag_extracts_tag_name(self):
        assert self.ac.getTag(
            ' (HEAD -> main, tag: 1.2.3, origin/main)', 'unreleased') == '1.2.3'


class TestGenerate:
    def test_groups_commits_by_tag_and_change_type(self, git_repo):
        commit(git_repo, 'Initial commit')
        commit(git_repo, 'Added: feature A', tag='1.0.0')
        commit(git_repo, 'Fixed: bug B')
        commit(git_repo, 'Added: feature C', tag='1.1.0')
        commit(git_repo, 'Docs: update readme')

        ac = AutoChangelog(git_path=str(git_repo))
        changelog = ac.generate()

        tags = [entry['tag'] for entry in changelog]
        assert tags == ['unreleased', '1.1.0', '1.0.0']

        unreleased = changelog[0]
        assert list(unreleased['changes'].keys()) == ['Docs']
        assert unreleased['changes']['Docs'][0]['message'] == 'Update readme'

        v1_1_0 = changelog[1]
        assert v1_1_0['message'] == 'Release 1.1.0'
        assert set(v1_1_0['changes'].keys()) == {'Added', 'Fixed'}
        assert v1_1_0['changes']['Added'][0]['message'] == 'Feature c'
        assert v1_1_0['changes']['Fixed'][0]['message'] == 'Bug b'

        v1_0_0 = changelog[2]
        assert v1_0_0['message'] == 'Release 1.0.0'
        # commits without a ': ' prefix are grouped under the empty change type
        assert set(v1_0_0['changes'].keys()) == {'', 'Added'}
        assert v1_0_0['changes'][''][0]['message'] == 'Initial commit'
        assert v1_0_0['changes']['Added'][0]['message'] == 'Feature a'

    def test_author_with_space_is_blanked_username_is_kept(self, git_repo):
        commit(git_repo, 'First commit',
               author='Test User <test@example.com>')
        commit(git_repo, 'Second commit', author='octocat <octocat@example.com>')

        ac = AutoChangelog(git_path=str(git_repo))
        changelog = ac.generate()

        commits_by_message = {
            c['message']: c
            for entry in changelog
            for changes in entry['changes'].values()
            for c in changes
        }
        assert commits_by_message['First commit']['user'] == ''
        assert commits_by_message['Second commit']['user'] == 'octocat'


class TestBuildHasNoSideEffects:
    def test_build_does_not_write_any_file(self, git_repo, tmp_path):
        commit(git_repo, 'Added: something', tag='1.0.0')

        output_dir = tmp_path / 'output'
        ac = AutoChangelog(git_path=str(git_repo),
                            output_path=str(output_dir))
        rendered = ac.build()

        assert '1.0.0' in rendered
        assert not output_dir.exists()

    def test_constructor_alone_does_no_io(self, git_repo, tmp_path):
        output_dir = tmp_path / 'output'
        AutoChangelog(git_path=str(git_repo), output_path=str(output_dir))
        assert not output_dir.exists()


class TestRun:
    def test_run_saves_changelog_file(self, git_repo, tmp_path):
        commit(git_repo, 'Added: something', tag='1.0.0')

        output_dir = tmp_path / 'output'
        ac = AutoChangelog(git_path=str(git_repo),
                            output_path=str(output_dir))
        ac.run()

        saved = output_dir / 'CHANGELOG.md'
        assert saved.exists()
        assert '1.0.0' in saved.read_text(encoding='utf-8')

    def test_remove_message_flag_hides_autogenerated_note(self, git_repo, tmp_path):
        commit(git_repo, 'Added: something', tag='1.0.0')

        with_message = AutoChangelog(git_path=str(git_repo)).build()
        without_message = AutoChangelog(
            git_path=str(git_repo), remove_message=True).build()

        assert 'automatically generated' in with_message
        assert 'automatically generated' not in without_message


def head_short_hash(repo):
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD'], cwd=str(repo), encoding='utf-8').strip()


class TestAmend:
    """Amending changes the commit's hash (it rewrites the tree, which the
    changelog file is part of), so a hash baked into the file for that same
    commit would be stale the instant the amend finishes. These verify the
    entry is flagged and the built-in template skips its hash link instead of
    rendering a dead link, without affecting any other entry.
    """

    def test_pending_commit_is_flagged_only_when_amend_requested(self, git_repo):
        commit(git_repo, 'Added: something new')
        head_hash = head_short_hash(git_repo)

        without_amend = AutoChangelog(git_path=str(git_repo))
        without_amend.generate()
        assert all(not c['pending_amend']
                   for entry in without_amend.changelog
                   for changes in entry['changes'].values()
                   for c in changes)

        with_amend = AutoChangelog(git_path=str(git_repo), amend=True)
        with_amend.generate()
        all_commits = [c for entry in with_amend.changelog
                       for changes in entry['changes'].values() for c in changes]
        pending = [c for c in all_commits if c['pending_amend']]
        assert len(pending) == 1
        assert pending[0]['hash'] == head_hash

    def test_hash_link_omitted_in_rendered_output_only_when_amending(self, git_repo):
        commit(git_repo, 'Initial commit')
        commit(git_repo, 'Added: something new')
        head_hash = head_short_hash(git_repo)

        rendered_normal = AutoChangelog(git_path=str(git_repo)).build()
        rendered_amend = AutoChangelog(
            git_path=str(git_repo), amend=True).build()

        assert head_hash in rendered_normal
        assert head_hash not in rendered_amend

    def test_end_to_end_amend_leaves_no_dead_hash_link(self, git_repo):
        commit(git_repo, 'Initial commit')
        commit(git_repo, 'Added: something new')
        pre_amend_hash = head_short_hash(git_repo)

        ac = AutoChangelog(git_path=str(git_repo),
                            output_path=str(git_repo), amend=True)
        ac.run()

        new_hash = head_short_hash(git_repo)
        assert new_hash != pre_amend_hash

        saved = (git_repo / 'CHANGELOG.md').read_text(encoding='utf-8')
        assert pre_amend_hash not in saved

        # the changelog file itself must be part of the amended commit
        files_in_commit = subprocess.check_output(
            ['git', 'show', '--name-only', '--pretty=format:', 'HEAD'],
            cwd=str(git_repo), encoding='utf-8')
        assert 'CHANGELOG.md' in files_in_commit
