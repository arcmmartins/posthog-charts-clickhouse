import time
import subprocess
import logging
import pytest
from kubernetes import client

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

NAMESPACE="posthog"
HELM_INSTALL_CMD='''
helm upgrade \
    --install \
    -f ../../ci/values/kubetest/test_clickhouse_persistence_enabled.yaml \
    --timeout 30m \
    --create-namespace \
    --namespace posthog \
    posthog ../../charts/posthog \
    --wait-for-jobs \
    --wait
'''

@pytest.fixture
def setup(kube):
    log.debug("🔄 Setting up the k8s cluster...")
    cmd = "kubectl delete all --all -n {namespace}".format(namespace=NAMESPACE)
    cmd_run = subprocess.run(cmd, shell=True)
    cmd_return_code = cmd_run.returncode
    if cmd_return_code:
        pytest.fail("❌ Error while running '{}'. Return code: {}".format(cmd,cmd_return_code))
    log.debug("✅ Done!")

    log.debug("🔄 Deploying PostHog...")
    cmd = HELM_INSTALL_CMD
    cmd_run = subprocess.run(cmd, shell=True)
    cmd_return_code = cmd_run.returncode
    if cmd_return_code:
        pytest.fail("❌ Error while running '{}'. Return code: {}".format(cmd,cmd_return_code))
    log.debug("✅ Done!")

    log.debug("🔄 Waiting for all pods to be ready...")
    time.sleep(30)
    start = time.time()
    timeout = 60
    while time.time() < start + timeout:
        pods = kube.get_pods(namespace="posthog")
        for pod in pods.values():
            if not pod.is_ready():
                continue
        break
    else:
        pytest.fail("❌ Timeout raised while waiting for pods to be ready")
    log.debug("✅ Done!")

def test_volume_claim(setup, kube):
    statefulsets = kube.get_statefulsets(
        namespace="posthog",
        labels={"clickhouse.altinity.com/namespace": "posthog"},
    )
    statefulset = next(iter(statefulsets.values()))
    statefulset_spec = statefulset.obj.spec

    # Verify the spec.volumes configuration
    volumes = statefulset_spec.template.spec.volumes
    expected_volume = client.V1Volume(
        name="volumeclaim-template-default",
        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
            claim_name="volumeclaim-template-default",
        )
    )
    assert expected_volume in volumes, "spec.volumes should include 'volumeclaim-template-default'"

    # Verify the spec.containers.[].volumeMounts
    volume_mounts = statefulset_spec.template.spec.containers[0].volume_mounts
    expected_volume_mount = client.V1VolumeMount(name='volumeclaim-template-default', mount_path="/var/lib/clickhouse")
    assert expected_volume_mount in volume_mounts, "spec.containers.[].volumeMounts should include 'existing-volumeclaim'"
