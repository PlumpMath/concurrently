import time

import gevent

import pytest

from concurrently import concurrently, GeventEngine, UnhandledExceptions


def process(data):
    gevent.sleep(data)
    return time.time()


@pytest.mark.parametrize(
    'conc_count', range(1, 5), ids=lambda v: 'counc %s' % v
)
@pytest.mark.parametrize(
    'data_count', range(1, 5), ids=lambda v: 'data %s' % v
)
def test_concurrently(conc_count, data_count, ):
    data = range(data_count)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(conc_count, engine=GeventEngine)
    def _parallel():
        for d in i_data:
            res = process(d)
            results[d] = res

    _parallel()

    def calc_delta(n):
        if n // conc_count == 0:
            return n
        return n + calc_delta(n - conc_count)

    assert len(results) == data_count
    for n, v in results.items():
        delta = v - start_time
        assert int(delta) == calc_delta(n)


def test_stop():
    data = range(3)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(2, engine=GeventEngine)
    def _parallel():
        for d in i_data:
            r = process(d)
            results[d] = r

    gevent.sleep(0.5)
    _parallel.stop()

    assert len(results) == 1
    assert int(results[0]) == int(start_time)


def test_exception():
    data = range(2)
    i_data = iter(data)

    @concurrently(2, engine=GeventEngine)
    def _parallel():
        for d in i_data:
            if d == 1:
                raise RuntimeError()

    with pytest.raises(UnhandledExceptions) as exc:
        _parallel()

    assert len(exc.value.exceptions) == 1
    assert isinstance(exc.value.exceptions[0], RuntimeError)


def test_exception_suppress():
    data = range(2)
    i_data = iter(data)
    results = {}
    start_time = time.time()

    @concurrently(2, engine=GeventEngine)
    def _parallel():
        for d in i_data:
            if d == 1:
                raise RuntimeError()
            res = process(d)
            results[d] = res

    _parallel(suppress_exceptions=True)

    assert len(results) == 1
    assert int(results[0]) == int(start_time)

    exc_list = _parallel.exceptions()
    assert len(exc_list) == 1
    assert isinstance(exc_list[0], RuntimeError)


async def test_fail_hard():
    i_data = iter(range(4))
    results = {}

    @concurrently(3, engine=GeventEngine)
    def _parallel():
        for d in i_data:
            if d == 1:
                raise RuntimeError()
            gevent.sleep(d)
            results[d] = True

    with pytest.raises(RuntimeError):
        _parallel(fail_hard=True)

    assert len(results) == 1
    assert results[0]