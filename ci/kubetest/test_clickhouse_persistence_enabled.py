import pytest
from kubernetes import client

from utils import cleanup_k8s, helm_install, wait_for_pods_to_be_ready

HELM_INSTALL_CMD = """
helm upgrade \
    --install \
    -f ../../ci/values/kubetest/test_clickhouse_persistence_enabled.yaml \
    --timeout 30m \
    --create-namespace \
    --namespace posthog \
    posthog ../../charts/posthog \
    --wait-for-jobs \
    --wait
"""


@pytest.fixture
def setup(kube):
    cleanup_k8s()
    helm_install(HELM_INSTALL_CMD)
    wait_for_pods_to_be_ready(kube)


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
        ),
    )
    assert expected_volume in volumes, "spec.volumes should include 'volumeclaim-template-default'"

    # Verify the spec.containers.[].volumeMounts
    volume_mounts = statefulset_spec.template.spec.containers[0].volume_mounts
    expected_volume_mount = client.V1VolumeMount(name="volumeclaim-template-default", mount_path="/var/lib/clickhouse")
    assert (
        expected_volume_mount in volume_mounts
    ), "spec.containers.[].volumeMounts should include 'existing-volumeclaim'"
