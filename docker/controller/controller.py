import os
import time
from githubutilsapi import GithubUtilsApi
from kubernetes import client, config
import yaml
from queue import Queue
import uuid
import re
import urllib.parse


# K8s configuration
MAX_REPLICAS = int(os.environ.get("ADO_MAX_SELF_HOSTED_AGENTS", 5))
NAMESPACE = 'dependency-check-devsecops-ns'
LABEL_SELECTOR = "app=dpcheck-worker"

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

def sanitize_job_name(name):
    # Convertir a minúsculas y reemplazar caracteres no permitidos con guiones
    sanitized_name = re.sub(r'[^a-z0-9-]', '-', name.lower())

    # Asegurarse de que el nombre comience y termine con un carácter alfanumérico
    sanitized_name = sanitized_name.strip("-")

    # Acortar el nombre si es necesario
    return sanitized_name[:63]


def create_k8s_job(repo_name, repo_url):
    # Read the job description from the YAML file
    with open("/app/k8s-job-worker.yaml") as file:
        job_yaml = yaml.safe_load(file)

    # Generate a unique name for the job
    shortened_repo_name = repo_name[:10]  # Ajusta según sea necesario
    unique_id = str(uuid.uuid4())[:8]    # Usamos solo los primeros 8 caracteres del UUID
    unique_job_name = sanitize_job_name(f"{shortened_repo_name}-{unique_id}")
    if len(unique_job_name) > 63:
        unique_job_name = unique_job_name[:63]

    job_yaml['metadata']['name'] = unique_job_name

    # Insert the GitHub token into the repo URL
    parsed_url = list(urllib.parse.urlparse(repo_url))
    parsed_url[1] = f"{gh_token}@{parsed_url[1]}"

    secure_repo_url = urllib.parse.urlunparse(parsed_url)

    # Modify the environment variables
    for env_var in job_yaml['spec']['template']['spec']['containers'][0]['env']:
        if env_var['name'] == 'GITHUB_REPO_NAME':
            env_var['value'] = repo_name
        elif env_var['name'] == 'GITHUB_URL':
            env_var['value'] = secure_repo_url

    # Create the Job
    k8s_client = client.BatchV1Api()
    job = k8s_client.create_namespaced_job(
        body=job_yaml,
        namespace=NAMESPACE
    )
    print(f"Job {unique_job_name} created")

def get_active_and_pending_jobs_count():
    """
    Return the number of active and pending jobs.
    """
    jobs = batch_v1.list_namespaced_job(NAMESPACE, label_selector=LABEL_SELECTOR)
    
    count = 0
    for job in jobs.items:
        if job.status.active:
            count += 1
        elif not job.status.conditions:  # Job is pending if no conditions are set
            count += 1

    return count


def clean_up_completed_jobs():
    """
    Remove the completed and failed jobs.
    """
    jobs = batch_v1.list_namespaced_job(
        namespace=NAMESPACE, 
        label_selector=LABEL_SELECTOR
    ).items

    for job in jobs:
        if job.status.succeeded or job.status.failed:
            batch_v1.delete_namespaced_job(
                name=job.metadata.name,
                namespace=NAMESPACE,
                body=client.V1DeleteOptions(propagation_policy='Foreground')
            )
            print(f"Deleted job {job.metadata.name}")

def process_repositories():
    """
    Run the process to create the jobs.
    """
    repos = get_plain_repo_list()
    for repo in repos:
        pending_jobs_queue.put(repo)

    while not pending_jobs_queue.empty():
        active_jobs_count = get_active_and_pending_jobs_count()

        if active_jobs_count < MAX_REPLICAS:
            repo = pending_jobs_queue.get()
            create_k8s_job(repo['name'], repo['html_url'])
        else:
            print(f"Reached max replicas limit ({MAX_REPLICAS}). Waiting for available resources...")
            print(f"The length of the queue is {pending_jobs_queue.qsize()}")
            time.sleep(10)

    clean_up_completed_jobs()

# Start the job creation process
process_repositories()
