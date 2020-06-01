from unittest.mock import MagicMock

from cortex.utils import decorators

def test_cache_res_calls_once_per_args():
    m = MagicMock(return_value=1)
    func = decorators.cache_res(m)
    ret_val = func(1,2,3, 4)
    assert ret_val == func(1, 2, 3, 4)
    m.assert_called_once()
