import os
import shutil
import typing
from typing import Dict

import git

CONTROL_FILE_CONTENT = (
    """
Source: yandex-taxi-adjust-py3

Package: yandex-taxi-adjust-py3
XC-Conductor-Package: yandex-taxi-import
""".strip()
)


class Commit:
    # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            comment,
            files,
            files_content=None,
            submodules=(),
            author=None,
            email=None,
            do_delete=False,
            rename_to=None,
    ):
        self.comment = comment
        self.files = files
        self.files_content = files_content
        self.submodules = submodules
        self.author = author
        self.email = email
        self.do_delete = do_delete
        self.rename_to = rename_to


class SubmoduleCommits:
    def __init__(
            self,
            path: str,
            commits: typing.List[Commit],
            reinit_if_exists: bool = False,
            origin_dir: typing.Optional[str] = None,
            delete_after_update: bool = False,
    ) -> None:
        self.path = path
        self.commits = commits
        self.reinit_if_exists = reinit_if_exists
        self.origin_dir = origin_dir
        self.delete_after_update = delete_after_update


def set_current_user(repo, username, email=None):
    if username:
        repo.git.config('user.name', username)
        if email is not None:
            repo.git.config('user.email', email)
        else:
            repo.git.config('user.email', username + '@yandex-team.ru')


def init_repo(path, username, email, commits=None):
    repo = git.Repo.init(path)
    set_current_user(repo, username, email)
    repo.git.checkout('-b', 'develop')
    if commits:
        apply_commits(repo, commits)
    return repo


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
# pylint: too-many-statements
def apply_commits(repo, commits):
    for commit in commits:
        for filepath in commit.files:
            dirs, filename = os.path.split(filepath)
            dirpath = repo.working_tree_dir
            if dirs:
                dirpath = os.path.join(dirpath, dirs)
                os.makedirs(dirpath, exist_ok=True)
            if filename:
                full_filepath = os.path.join(dirpath, filename)
                content = commit.files_content
                if commit.do_delete:
                    if os.path.isdir(full_filepath):
                        shutil.rmtree(full_filepath)
                    else:
                        os.remove(full_filepath)
                    continue
                if commit.rename_to:
                    dirname = os.path.dirname(full_filepath)
                    new_name = os.path.join(dirname, commit.rename_to)
                    os.rename(full_filepath, new_name)
                    continue
                if content is None:
                    content = commit.comment + full_filepath
                with open(full_filepath, 'w') as fout:
                    fout.write(content)

        if commit.submodules:
            # Write info to .gitconfig in home if exists. Works only for repos
            home_dir = os.path.join(repo.working_tree_dir, '../home/')
            for submodule_commits in commit.submodules:
                if not isinstance(submodule_commits, SubmoduleCommits):
                    submodule_commits = SubmoduleCommits(*submodule_commits)
                path = submodule_commits.path
                origin_sub_dir = (
                    repo.working_tree_dir
                    + '_'
                    + (submodule_commits.origin_dir or path.replace('/', '_'))
                )
                submodule_full_path = os.path.join(repo.working_tree_dir, path)
                if (
                        os.path.exists(submodule_full_path)
                        and not submodule_commits.reinit_if_exists
                ):
                    submodule = repo.submodule(path)
                    submodule_url = submodule.url
                    if os.path.exists(home_dir):
                        instead_urls = repo.git.config(
                            '--file',
                            '../home/.gitconfig',
                            '--get-regexp',
                            r'^url\..*\.insteadof$',
                        )
                        for instead_url, remote_url in map(
                                str.split, instead_urls.splitlines(),
                        ):
                            if remote_url == submodule.url:
                                submodule_url = instead_url.split('.')[1]
                                break

                    sub_repo = git.Repo(submodule_url)
                    before_upd_commit = sub_repo.git.rev_parse('HEAD')
                    if submodule_commits.commits:
                        apply_commits(sub_repo, submodule_commits.commits)
                    submodule.update(to_latest_revision=True)
                    if submodule_commits.delete_after_update:
                        sub_repo.git.reset([before_upd_commit, '--hard'])
                        sub_repo.git.reflog(
                            ['expire', '--expire-unreachable=now', '--all'],
                        )
                        sub_repo.git.gc(['--prune=now'])
                else:
                    if submodule_commits.reinit_if_exists:
                        shutil.rmtree(submodule_full_path, ignore_errors=True)
                    username = repo.git.config('user.name')
                    email = repo.git.config('user.email')
                    init_repo(
                        origin_sub_dir,
                        username,
                        email,
                        submodule_commits.commits,
                    )
                    if submodule_commits.reinit_if_exists:
                        try:
                            submodule = repo.submodule(path)
                            instead_urls = repo.git.config(
                                '--file',
                                '../home/.gitconfig',
                                '--get-regexp',
                                r'^url\..*\.insteadof$',
                            )
                            for instead_url, remote_url in map(
                                    str.split, instead_urls.splitlines(),
                            ):
                                if remote_url == submodule.url:
                                    repo.git.config(
                                        '--file',
                                        '../home/.gitconfig',
                                        '--unset',
                                        instead_url,
                                    )
                                    break
                        except ValueError:
                            pass
                        except git.GitCommandError:
                            pass
                        repo.git.config(
                            'submodule.' + path + '.url',
                            origin_sub_dir,
                            file='.gitmodules',
                        )
                        repo.git.submodule('sync')
                        shutil.rmtree(
                            os.path.join(
                                repo.working_tree_dir, '.git', 'modules', path,
                            ),
                            ignore_errors=True,
                        )
                    repo.git.submodule('add', '-f', origin_sub_dir, path)

                    if os.path.exists(home_dir):
                        last_part_path = path.split('/')[-1]
                        gitmodule_url = 'submodule.%s.url' % path
                        new_url = (
                            'git@github.yandex-team.ru:taxi/%s.git'
                            % last_part_path
                        )
                        repo.git.config(
                            '--file', '.gitmodules', gitmodule_url, new_url,
                        )
                        repo.git.config(
                            '--file',
                            '../home/.gitconfig',
                            'url.' + origin_sub_dir + '.insteadOf',
                            new_url,
                        )
                    sub_repo = git.Repo(submodule_full_path)
                    set_current_user(sub_repo, username, email)

        default_author = repo.git.config('user.name')
        default_email = repo.git.config('user.email')

        set_current_user(repo, commit.author, commit.email)

        repo.git.add('-A')
        repo.index.commit(commit.comment)

        set_current_user(repo, default_author, default_email)


def commit_debian_dir(
        repo, package_name, version='0.0.1', path=None, release_ticket=None,
):
    service_path = repo.working_tree_dir
    if path is not None:
        service_path = os.path.join(service_path, path)
    debian_path = os.path.join(service_path, 'debian')
    os.makedirs(debian_path, exist_ok=True)
    changelog = '%s (%s) unstable; urgency=low\n\n' % (package_name, version)
    if release_ticket is not None:
        changelog += (
            '  Release ticket https://st.yandex-team.ru/%s\n\n'
            % release_ticket
        )
    changelog += '  * Mister Twister | commit message\n\n'
    changelog += ' -- b <f@yandex-team.ru> Thu, 05 Apr 2018 18:52:10 +0300\n'

    changelog_file = os.path.join(debian_path, 'changelog')
    with open(changelog_file, 'w') as fout:
        fout.write(changelog)

    control_file = os.path.join(debian_path, 'control')
    with open(control_file, 'w') as fout:
        fout.write(CONTROL_FILE_CONTENT)

    repo.index.add([changelog_file, control_file])
    repo.index.commit('add %s package' % package_name)


def commit_data(repo: git.Repo, data: Dict[str, str], clean: bool = False):
    if clean:
        for sub in os.listdir(repo.working_dir):
            if sub == '.git':
                continue
            repo.git.rm(sub, '-r')
    for key, value in data.items():
        filename = os.path.join(repo.working_dir, key)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as fout:
            fout.write(value)
        repo.git.add(filename)
    repo.index.commit('commit')


def add_commits_only_to_origin(repo, commits):
    """Add commits to origin of repo - it looks like they came from
    other users
    """
    repo.git.checkout('develop')
    repo.git.branch('original_develop')
    apply_commits(repo, commits)
    repo.git.push('origin', 'develop')
    repo.git.reset('--hard', 'original_develop')
    repo.git.clean('-dff')
