import asyncio
import time

import pytest

from concurrently import concurrently, AsyncIOEngine, UnhandledExceptions

from . import EngineTest, paramz_conc_count, paramz_data_count


@asyncio.coroutine
def process(data, *, loop):
    yield from asyncio.sleep(data, loop=loop)
    return time.time()


class TestAsyncIOEngine(EngineTest):

    @pytest.mark.asyncio(forbid_global_loop=True)
    @paramz_conc_count
    @paramz_data_count
    def test_concurrently(self, conc_count, data_count, event_loop):
        data = range(data_count)
        i_data = iter(data)
        results = {}
        start_time = time.time()

        @concurrently(conc_count, engine=AsyncIOEngine, loop=event_loop)
        @asyncio.coroutine
        def _parallel():
            for d in i_data:
                res = yield from process(d, loop=event_loop)
                results[d] = res

        yield from _parallel()

        def calc_delta(n):
            if n // conc_count == 0:
                return n
            return n + calc_delta(n - conc_count)

        assert len(results) == data_count
        for n, v in results.items():
            delta = v - start_time
            assert int(delta) == calc_delta(n)

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_stop(self, event_loop):
        data = range(3)
        i_data = iter(data)
        results = {}
        start_time = time.time()

        @concurrently(2, engine=AsyncIOEngine, loop=event_loop)
        @asyncio.coroutine
        def _parallel():
            for d in i_data:
                r = yield from process(d, loop=event_loop)
                results[d] = r

        yield from asyncio.sleep(0.5, loop=event_loop)
        yield from _parallel.stop()

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_exception(self, event_loop):
        data = range(2)
        i_data = iter(data)

        @concurrently(2, engine=AsyncIOEngine, loop=event_loop)
        @asyncio.coroutine
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()

        with pytest.raises(UnhandledExceptions) as exc:
            yield from _parallel()

        assert len(exc.value.exceptions) == 1
        assert isinstance(exc.value.exceptions[0], RuntimeError)

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_exception_suppress(self, event_loop):
        data = range(2)
        i_data = iter(data)
        results = {}
        start_time = time.time()

        @concurrently(2, engine=AsyncIOEngine, loop=event_loop)
        @asyncio.coroutine
        def _parallel():
            for d in i_data:
                if d == 1:
                    raise RuntimeError()
                res = yield from process(d, loop=event_loop)
                results[d] = res

        yield from _parallel(suppress_exceptions=True)

        assert len(results) == 1
        assert int(results[0]) == int(start_time)

        exc_list = _parallel.exceptions()
        assert len(exc_list) == 1
        assert isinstance(exc_list[0], RuntimeError)

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_fail_hard(self, event_loop):
        i_data = iter(range(4))
        results = {}

        @concurrently(3, engine=AsyncIOEngine, loop=event_loop)
        @asyncio.coroutine
        def _parallel():
            for d in i_data:
                yield from asyncio.sleep(d, loop=event_loop)  # fix all tests?
                if d == 1:
                    raise RuntimeError()
                results[d] = True

        with pytest.raises(RuntimeError):
            yield from _parallel(fail_hard=True)

        assert len(results) == 1
        assert results[0]

    def test_decorated_fn_is_coroutine(self, event_loop):
        with pytest.raises(AssertionError) as e:
            @concurrently(1, engine=AsyncIOEngine, loop=event_loop)
            def _no_coroutine():
                pass

        assert str(e.value) \
            == 'Decorated function `_no_coroutine` must be coroutine'
