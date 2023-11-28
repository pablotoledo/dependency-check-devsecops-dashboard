import os
import time
from githubutilsapi import GithubUtilsApi
from kubernetes import client, config
import yaml
from queue import Queue

# K8s configuration
MAX_REPLICAS = int(os.environ.get("ADO_MAX_SELF_HOSTED_AGENTS", 5))
NAMESPACE = 'dependency-check-devsecops-ns'
LABEL_SELECTOR = "role=dcheck-node"

# Load K8s configuration
config.load_incluster_config()

# Create the K8s API clients
v1 = client.AppsV1Api()
batch_v1 = client.BatchV1Api()

# Create the queue for pending jobs
pending_jobs_queue = Queue()

#### GITHUB API ####

gh_user = os.environ.get('GITHUB_USER')
gh_token = os.environ.get('GITHUB_TOKEN')
gh_url = os.environ.get('GITHUB_URL')
organization = os.environ.get('GITHUB_ORGANIZATION')

gh_api_url = gh_url + '/api/v3'
gh_graphql_url = gh_url + '/api/graphql'

github = GithubUtilsApi(user=gh_user, token=gh_token, github_url=gh_api_url, github_url_graphql=gh_graphql_url)

def get_plain_repo_list():
    return github.list_repositories_all(organization)

#### K8S API ####

def create_k8s_job(repo_name, repo_url):
    # Load the kubeconfig file
    config.load_kube_config()

    # Read the job description from the YAML file
    with open("/app/k8s-job-worker.yaml") as file:
        job_yaml = yaml.safe_load(file)

    # Modify the environment variables
    for env_var in job_yaml['spec']['template']['spec']['containers'][0]['env']:
        if env_var['name'] == 'GITHUB_REPO_NAME':
            env_var['value'] = repo_name
        elif env_var['name'] == 'GITHUB_URL':
            env_var['value'] = repo_url

    # Create the Job
    k8s_client = client.BatchV1Api()
    job = k8s_client.create_namespaced_job(
        body=job_yaml,
        namespace="default"
    )
    print("Job created")

def get_active_jobs_count():
    """
    Return the number of active jobs.
    """
    jobs = batch_v1.list_namespaced_job(NAMESPACE, label_selector=LABEL_SELECTOR)
    active_jobs = [job for job in jobs.items if job.status.active]
    return len(active_jobs)

def clean_up_completed_jobs():
    """
    Remove the completed jobs.
    """
    completed_jobs = batch_v1.list_namespaced_job(
        namespace=NAMESPACE, 
        label_selector=LABEL_SELECTOR
    ).items

    for job in completed_jobs:
        if job.status.succeeded or job.status.failed:
            batch_v1.delete_namespaced_job(
                name=job.metadata.name,
                namespace=NAMESPACE,
                body=client.V1DeleteOptions(propagation_policy='Foreground')
            )

def process_repositories():
    """
    Run the process to create the jobs.
    """
    repos = get_plain_repo_list()
    for repo in repos:
        pending_jobs_queue.put(repo)

    while not pending_jobs_queue.empty():
        active_jobs_count = get_active_jobs_count()
        
        if active_jobs_count < MAX_REPLICAS:
            repo = pending_jobs_queue.get()
            create_k8s_job(repo['name'], repo['html_url'])
        else:
            print("Waiting available resources...")
            time.sleep(10)  # Await 10 seconds

        clean_up_completed_jobs()

# Start the job creation process
process_repositories()
