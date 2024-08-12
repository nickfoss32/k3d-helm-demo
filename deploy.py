#!/usr/bin/env python

import argparse
import logging
import subprocess
import sys

def is_installed(utility: str) -> bool:
    """Runs 'which' on specified utility to check if it is installed."""
    try:
        subprocess.check_output(['which', utility])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Creates a local k8s cluster using k3d and deploys k8s dashboard service.')
    parser.add_argument('--cluster-name', '-c', help='Name of the k8s cluster to create.', default='local-k8s')
    parser.add_argument('--num-nodes', '-n', help='Number of worker nodes in the cluster.', default='1')
    args = parser.parse_args()

    # setup logging
    # TODO: maybe add an argument to have user set this
    logging.basicConfig(level=logging.INFO)

    # Prerequisites - check for docker, k3d, kubectl, and helm
    deps = ["docker", "k3d", "kubectl", "helm"]
    for dep in deps:
        if is_installed(dep) is False:
            logging.error(f"{dep} is missing! Please install before running.")
            return 1
    
    # delete the cluster if it already exists
    subprocess.run(['k3d', 'cluster', 'delete', args.cluster_name])

    # create the cluster
    logging.info(f"Creating cluster... name: {args.cluster_name}, nodes: {args.num_nodes}")
    try:
        subprocess.check_output(['k3d', 'cluster', 'create', args.cluster_name, '--agents', args.num_nodes])
    except subprocess.CalledProcessError:
        logging.error('Unable to create cluster.')
        return 1

    # check if kubectl can talk to the newly created cluster
    try:
        subprocess.check_output(['kubectl', 'cluster-info'])
    except subprocess.CalledProcessError:
        logging.error('kubectl unable to connect to cluster.')
        return 1
    logging.info('Cluster created!')
    
    # deploy kubernetes dashboard
    logging.info('Deploying kubernetes dashboard to cluster...')

    # add helm repo for k8s dashboard
    try:
        subprocess.check_output(['helm', 'repo', 'add', 'kubernetes-dashboard', 'https://kubernetes.github.io/dashboard'])
    except subprocess.CalledProcessError:
        logging.error('Unable to add k8s helm repo')
        return 1

    # install the helm chart for k8s dashboard
    try:
        subprocess.check_output(['helm', 'install', 'dashboard', 'kubernetes-dashboard/kubernetes-dashboard'])
    except subprocess.CalledProcessError:
        logging.error('Unable to install k8s dashboard chart.')
        return 1
    logging.info('Dashboard deployed!')

    return 0

if __name__ == "__main__":
    sys.exit(main())
