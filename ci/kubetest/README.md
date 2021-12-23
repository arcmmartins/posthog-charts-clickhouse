# Kubetest
This directory contains the integration tests for our Helm chart. We use [`kubetest`](https://kubetest.readthedocs.io/en/latest/) that is a `pytest` plugin that makes it easier to write integration tests on Kubernetes.
x
## How-to
1. `pip install -r requirements.txt`
1. `pytest -s .`

# Useful examples
- https://kubetest.readthedocs.io/en/latest

- https://github.com/vapor-ware/kubetest/tree/master/examples

- https://github.com/express42/otus-platform-tests/tree/9bfe761c1c7728498f84e9356eba020ba524744d/homeworks/kubernetes-intro

- https://github.com/opsani/servox/blob/9a6f2a8b6ae0383d48a2259daa7a5b25a3321bc0/tests/conftest.py
