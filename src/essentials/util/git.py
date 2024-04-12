# -*- coding: utf-8 -*-

"""

@author Kami-Kaze
"""

_GIT_URL = 'https://github.com'
_GIT_USER_CONTENT_URL = 'raw.githubusercontent.com'


def repo_url(base_url: str, owner: str, repo: str, branch: str = None) -> str:
    return f'https://{base_url}/{owner}/{repo}{f"/{branch}" if branch else ""}'


def releases_url(owner: str, repo: str, latest: bool) -> str:
    return f'{repo_url(_GIT_URL, owner, repo)}/releases{"/latest" if latest else ""}'


def file_url(owner: str, repo: str, path: str, branch: str = 'main') -> str:
    return f'{repo_url(_GIT_USER_CONTENT_URL, owner, repo, branch)}/{path}'
