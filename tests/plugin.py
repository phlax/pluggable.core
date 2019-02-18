
import pytest

from pluggable.core.plugin import Plugin


def test_plugin_signature():

    with pytest.raises(TypeError):
        Plugin()
