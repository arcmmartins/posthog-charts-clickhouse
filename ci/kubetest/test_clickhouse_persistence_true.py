import pytest
import subprocess
from typing import Optional
from pprint import pprint
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

NAMESPACE="posthog"
HELM_INSTALL_CMD='''
helm upgrade \
    --install \
    -f ../../ci/values/kubetest/test_clickhouse_persistence_true.yaml \
    --timeout 30m \
    --create-namespace \
    --namespace posthog \
    posthog ../../charts/posthog \
    --wait-for-jobs \
    --wait
'''

@pytest.fixture
def setup():
    log.debug("🔄 Setting up the k8s cluster...")
    cmd = "kubectl delete all --all -n {namespace}".format(namespace=NAMESPACE)
    cmd_run = subprocess.run(cmd, shell=True)
    cmd_return_code = cmd_run.returncode
    if cmd_return_code:
        pytest.fail("Error while running '{}'. Return code: {}".format(cmd,cmd_return_code))
    log.debug("✅ Done!")

    log.debug("🔄 Deploying PostHog...")
    cmd = HELM_INSTALL_CMD
    cmd_run = subprocess.run(cmd, shell=True)
    cmd_return_code = cmd_run.returncode
    if cmd_return_code:
        pytest.fail("Error while running '{}'. Return code: {}".format(cmd,cmd_return_code))
    log.debug("✅ Done!")

def test_clickhouse_pvc_present(setup, kube):
    statefulsets = kube.get_statefulsets(
        namespace="posthog",
        labels={"clickhouse.altinity.com/namespace": "posthog"},
    )
    volume_claim_templates = list(statefulsets.values())[0].obj.spec.volume_claim_templates
    assert len(volume_claim_templates) == 1, "ClickHouse should be using a PVC"

    volume_claim_template_spec = volume_claim_templates[0].spec

    volume_claim_template_storage_class = volume_claim_template_spec.storage_class_name
    assert volume_claim_template_storage_class == None, "ClickHouse PVC should be using the default StorageClass"

    volume_claim_size = volume_claim_template_spec.resources.requests["storage"]
    assert volume_claim_size == "1Gi", "ClickHouse PVC size should be correct"
