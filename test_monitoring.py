import monitoring.clientSideMonitoring.utils as u


def test_is_linux():
    assert u.is_linux(), 'Should be linux'

