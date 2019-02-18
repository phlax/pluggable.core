
import pytest

from pluggable.core.worker import CoreWorkerPlugin


def test_worker_signature():

    with pytest.raises(TypeError):
        CoreWorkerPlugin()
