import subprocess as sp
import re
from jinja2 import Template
import sys
import os
from template import template


class AutoChangelog(object):
    """Generate changelog from git log"""

    def __init__(self, git_path=None, template_path=None, output_path='.', remote_git=None, amend=False, push=False, changelog_file=None, force=False, remove_message=False):
        """Initialize changelog generator
        git_path: path to git repository
        template_path: path to template file
        """
        self.changelog_file = changelog_file if changelog_file is not None else 'CHANGELOG.md'
        self.git_path = git_path if git_path else '.'
        self.template_path = template_path
        self.remove_message = remove_message
        self.changelog = []
        self.changelog_rendered = ''
        self.generate()
        self.setTemplate()
        self.remote_git = remote_git
        self.getRepositoryURL()
        self.render()
        self.output_path = output_path if output_path else '.'
        self.save()
        self.force = force
        if amend:
            self.amend()
        if push:
            self.push()

    def generate(self):
        """Generate model"""

        tagDate = ''
        currentTag = 'unreleased'

        commits = self.getGitHistory()

        for commit in commits:
            parts = re.search('(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*)', commit)
            hash, date, user, tag, message = parts.groups()

            user = '' if user.find(' ') != -1 else user
            currentTag = self.getTag(tag, currentTag)
            tagDate = tagDate if tag == '' else date
            tagMessage = self.getTagMessage(currentTag)
            if self.valueInDictList(currentTag, self.changelog) == False:
                self.changelog.append({
                    'tag': currentTag,
                    'date': tagDate,
                    'message': tagMessage,
                    'changes': {self.getChangeType(message): [{'hash': hash, 'date': date, 'user': user, 'message': self.getCommitMessage(message)}]}
                })
            else:
                for dict in self.changelog:
                    if currentTag in dict.values():
                        if self.getChangeType(message) in dict['changes']:
                            dict['changes'][self.getChangeType(message)].append(
                                {'hash': hash, 'date': date, 'user': user, 'message': self.getCommitMessage(message)})
                        else:
                            dict['changes'][self.getChangeType(message)] = [
                                {'hash': hash, 'date': date, 'user': user, 'message': self.getCommitMessage(message)}]
        # order changes by date
        for dict in self.changelog:
            for changeType in dict['changes']:
                dict['changes'][changeType] = sorted(
                    dict['changes'][changeType], key=lambda k: k['date'], reverse=True)
        # order changes by type
        for dict in self.changelog:
            dict['changes'] = {k: v for k, v in sorted(
                dict['changes'].items(), key=lambda item: item[0])}

        return self.changelog

    def getChangeType(self, message):
        """Get change type from commit message"""
        changeType = ''
        if ': ' in message:
            changeType = message.split(': ')[0].strip().capitalize()
        return changeType

    def getCommitMessage(self, message):
        if ': ' in message:
            message = message[message.index(': ') + 1:]
            return message.strip()
        else:
            return message

    def valueInDictList(self, value, dictList):
        for dict in dictList:
            if value in dict.values():
                return True
        return False

    def getTag(self, tag, currentTag):
        if 'tag' not in tag:
            return currentTag
        else:
            if tag == '':
                return currentTag
            else:
                tag = tag.split('tag: ').pop().removesuffix(')')
                if ',' in tag:
                    tag = tag.split(',')[0]
                return tag

    def getTagMessage(self, tag):
        if (tag == 'unreleased'):
            return ''
        output = sp.check_output(
            'cd ' + self.git_path +
            '&& git tag -l --format="%(subject)" ' + tag, shell=True)
        subject = output.decode('utf-8')
        return subject.strip()

    def getGitHistory(self):
        """Get git log and parse it"""
        try:
            # PARTES: hash, date, author, tag, message
            output = sp.check_output('cd ' + self.git_path +
                                    '&& git log --pretty="%h%x09%cs%x09%an%x09%d%x09%s"', text=False, shell=True)
            output = output.decode('utf-8')
            
            if output.startswith('fatal'):
                print(output)
                sys.exit()

            gitChangeLog = list(filter(None, output.split('\n')))

            return gitChangeLog
        except sp.CalledProcessError as e:
            pass
            sys.exit()

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
            output = sp.check_output(
                'cd ' + self.git_path +
                '&& git config --get remote.origin.url', shell=True, text=True)
            output = str(output).strip()
            if output.strip() != '':
                remote_git = output.removesuffix('.git')
        except sp.CalledProcessError as e:
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
            with open(self.output_path + '/' + self.changelog_file, 'w', encoding='UTF-8') as changelogFile:
                changelogFile.write(self.changelog_rendered)
            print('Changelog saved to ' + self.output_path +
                  '/' + self.changelog_file)
        except Exception as e:
            print('Error saving file: ' + str(e))
            sys.exit(1)

    def amend(self):
        """Amend changelog file"""
        try:
            hash = sp.check_output(
                'cd ' + self.git_path +
                '&& git rev-parse HEAD', shell=True, text=True).strip()

            # check if tag exists in hash
            output = sp.check_output(
                'cd ' + self.git_path +
                '&& git tag --points-at ' + hash, shell=True, text=True)
            tag = str(output).strip()
            if tag != '':
                tagMessage = self.getTagMessage(tag)
                # remove tag
                sp.check_output(
                'cd ' + self.git_path +
                '&& git tag -d ' + tag, shell=True, text=True)
                print('Tag removed: ' + tag)

            # amend changelog
            sp.check_output(
                'cd ' + self.git_path +
                '&& git reset ' + hash +
                '&& git add  ' + self.changelog_file + ''
                '&& git commit --amend --no-edit', shell=True)
            print('Changelog amended to commit ' + hash)
            
                
                # if tag exists, add tag again
            if tag != '':
                sp.check_output(
                    'cd ' + self.git_path +
                    '&& git tag -a ' + tag + ' -m "' + tagMessage + '"', shell=True, text=True)
                print('Tag ' + tag + ' added again')

        except sp.CalledProcessError as e:
            print('Error amending file: ' + str(e))
            sys.exit(1)

    def push(self):
        """Push changes to remote repository"""
        try:
            force = '' if self.force == False else ' -f'
            if self.remote_git != '':
                sp.check_output(
                    'cd ' + self.git_path +
                    '&& git push ' + force +
                    '&& git push origin --tags' + force, shell=True)
                print('Remote repository updated')
            else:
                print('No remote repository configured')
                sys.exit(1)
        except sp.CalledProcessError as e:
            print('Error pushing file: ' + str(e))
            sys.exit(1)
