import os
from githubutilsapi import GithubUtilsApi

gh_user = os.environ.get('GITHUB_USER')
gh_token = os.environ.get('GITHUB_TOKEN')
gh_url = os.environ.get('GITHUB_URL')
organization = os.environ.get('GITHUB_ORGANIZATION')

gh_api_url = gh_url + '/api/v3'
gh_graphql_url = gh_url + '/api/graphql'

github = GithubUtilsApi(user=gh_user, token=gh_token, github_url=gh_api_url, github_url_graphql=gh_graphql_url)

def get_plain_repo_list():
    return github.list_repositories_all(organization)


get_plain_repo_list()
