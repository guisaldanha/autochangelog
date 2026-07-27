import subprocess as sp
import re
from jinja2 import Template
import sys
import os
from template import template


class AutoChangelog(object):
    """Generate changelog from git log"""

    COMMIT_PATTERN = re.compile(r'(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*)')

    def __init__(self, git_path=None, template_path=None, output_path='.', remote_git=None, amend=False, push=False, changelog_file=None, force=False, remove_message=False):
        """Configure the changelog generator.

        This only stores configuration - no git or filesystem I/O happens
        until build() or run() is called.
        """
        self.changelog_file = changelog_file if changelog_file is not None else 'CHANGELOG.md'
        self.git_path = git_path if git_path else '.'
        self.template_path = template_path
        self.output_path = output_path if output_path else '.'
        self.remote_git = remote_git
        self.remove_message = remove_message
        self.force = force
        self.amend_requested = amend
        self.push_requested = push
        self.changelog = []
        self.changelog_rendered = ''

    def build(self):
        """Read git history and render the changelog in memory.

        No files are written and no git state is changed by this method.
        """
        self.generate()
        self.setTemplate()
        self.getRepositoryURL()
        self.render()
        return self.changelog_rendered

    def run(self):
        """Build the changelog and apply the requested side effects (save/amend/push)."""
        self.build()
        self.save()
        if self.amend_requested:
            self.amend()
        if self.push_requested:
            self.push()
        return self.changelog_rendered

    def _git(self, *args):
        """Run a git command against the target repository and return its stdout as text."""
        return sp.check_output(['git', *args], cwd=self.git_path, encoding='utf-8')

    def generate(self):
        """Generate model"""

        tagDate = ''
        currentTag = 'unreleased'

        commits = self.getGitHistory()
        changelogByTag = {}

        # When --amend is requested, HEAD's commit hash is about to change
        # (amending changes the tree, which changes the commit hash), so the
        # hash we'd embed for it right now would already be stale the moment
        # the amend finishes. Flag that entry so the template can skip its
        # (necessarily wrong) hash link instead of rendering a dead link.
        headHash = self._git(
            'rev-parse', '--short', 'HEAD').strip() if self.amend_requested else None

        for commit in commits:
            parts = self.COMMIT_PATTERN.search(commit)
            assert parts is not None
            hash, date, user, tag, message = parts.groups()

            user = '' if ' ' in user else user
            currentTag = self.getTag(tag, currentTag)
            tagDate = tagDate if tag == '' else date
            changeType = self.getChangeType(message)
            commitEntry = {
                'hash': hash,
                'date': date,
                'user': user,
                'message': self.getCommitMessage(message),
                'pending_amend': hash == headHash
            }

            if currentTag not in changelogByTag:
                # tag message is only ever needed the first time we see this tag
                changelogByTag[currentTag] = {
                    'tag': currentTag,
                    'date': tagDate,
                    'message': self.getTagMessage(currentTag),
                    'changes': {changeType: [commitEntry]}
                }
            else:
                changes = changelogByTag[currentTag]['changes']
                changes.setdefault(changeType, []).append(commitEntry)

        self.changelog = list(changelogByTag.values())

        # order changes by date
        for entry in self.changelog:
            for changeType in entry['changes']:
                entry['changes'][changeType] = sorted(
                    entry['changes'][changeType], key=lambda k: k['date'], reverse=True)
            # order changes by type
            entry['changes'] = dict(
                sorted(entry['changes'].items(), key=lambda item: item[0]))

        return self.changelog

    def getChangeType(self, message):
        """Get change type from commit message"""
        if ': ' in message:
            return message.split(': ', 1)[0].strip().capitalize()
        return ''

    def getCommitMessage(self, message):
        if ': ' in message:
            message = message[message.index(': ') + 1:]
            return message.strip().capitalize()
        else:
            return message.capitalize()

    def getTag(self, tag, currentTag):
        if 'tag' not in tag:
            return currentTag
        tag = tag.split('tag: ').pop().removesuffix(')')
        if ',' in tag:
            tag = tag.split(',')[0]
        return tag

    def getTagMessage(self, tag):
        if tag == 'unreleased':
            return ''
        output = self._git('tag', '-l', '--format=%(subject)', tag)
        return output.strip()

    def getGitHistory(self):
        """Get git log and parse it"""
        try:
            output = self._git(
                'log', '--pretty=%h%x09%cs%x09%an%x09%d%x09%s')
        except sp.CalledProcessError:
            print('Error: "' + self.git_path +
                  '" is not a git repository, or it has no commits yet.', file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print('Error running git (is it installed and on PATH?): ' +
                  str(e), file=sys.stderr)
            sys.exit(1)

        return list(filter(None, output.split('\n')))

    def setTemplate(self):
        if self.template_path is not None:
            # check if template exists
            if os.path.exists(self.template_path) == False:
                print('Template file not found: ' + self.template_path)
                sys.exit(1)
            # read template file
            with open(self.template_path, 'r', encoding='UTF-8') as templateFile:
                self.template = templateFile.read()
        else:
            self.template = template

    def getRepositoryURL(self):
        if self.remote_git is not None:
            return self.remote_git
        remote_git = ''
        try:
            output = self._git(
                'config', '--get', 'remote.origin.url').strip()
            if output != '':
                remote_git = output.removesuffix('.git')
        except sp.CalledProcessError:
            pass
        self.remote_git = remote_git

    def render(self):
        """Render template"""
        template = Template(self.template)
        # replace many \n with \n
        rendered = template.render(
            remote_git=self.remote_git, changelog=self.changelog, remove_message=self.remove_message)
        self.changelog_rendered = re.sub(
            r'(\n\s*\n)+', '\n\n', rendered).strip() + '\n'

    def save(self):
        try:
            # check directory
            if os.path.exists(self.output_path) == False:
                os.makedirs(self.output_path)
            # save file
            self.changelog_full_path = os.path.abspath(
                os.path.join(self.output_path, self.changelog_file))
            with open(self.changelog_full_path, 'w', encoding='UTF-8') as changelogFile:
                changelogFile.write(self.changelog_rendered)
            print('Changelog saved to ' + self.changelog_full_path)
        except Exception as e:
            print('Error saving file: ' + str(e))
            sys.exit(1)

    def amend(self):
        """Amend changelog file"""
        try:
            hash = self._git('rev-parse', 'HEAD').strip()

            # check if tag exists in hash
            tag = self._git('tag', '--points-at', hash).strip()
            if tag != '':
                tagMessage = self.getTagMessage(tag)
                # remove tag
                self._git('tag', '-d', tag)
                print('Tag removed: ' + tag)

            # amend changelog
            self._git('reset', hash)
            self._git('add', self.changelog_full_path)
            self._git('commit', '--amend', '--no-edit')
            newHash = self._git('rev-parse', 'HEAD').strip()
            print('Changelog amended to commit ' + newHash)

            # if tag exists, add tag again
            if tag != '':
                self._git('tag', '-a', tag, '-m', tagMessage)
                print('Tag ' + tag + ' added again')

        except sp.CalledProcessError as e:
            print('Error amending file: ' + str(e))
            sys.exit(1)

    def push(self):
        """Push changes to remote repository"""
        try:
            if self.remote_git == '':
                print('No remote repository configured')
                sys.exit(1)
            forceArgs = ['-f'] if self.force else []
            self._git('push', *forceArgs)
            self._git('push', 'origin', '--tags', *forceArgs)
            print('Remote repository updated')
        except sp.CalledProcessError as e:
            print('Error pushing file: ' + str(e))
            sys.exit(1)
