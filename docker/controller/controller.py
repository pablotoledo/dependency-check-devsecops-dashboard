import os
from githubutilsapi import GithubUtilsApi
from kubernetes import client, config

# K8s configuration
MAX_REPLICAS = int(os.environ.get("ADO_MAX_SELF_HOSTED_AGENTS", 5))
NAMESPACE = 'devops-k8s-ns'
LABEL_SELECTOR = "role=ado-agent"
config.load_incluster_config()
v1 = client.AppsV1Api()




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


def create_k8s_job():
    def load_yaml_file(relative_path):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        yaml_path = os.path.join(script_dir, relative_path)
        
        with open(yaml_path, 'r') as file:
            return yaml.safe_load(file)
        
    api_instance = client.BatchV1Api()
    job_spec = load_yaml_file("job-agent.yaml")
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(generate_name="ado-agent-"),
        spec=job_spec["spec"]
    )
    api_instance.create_namespaced_job(namespace=NAMESPACE, body=job)