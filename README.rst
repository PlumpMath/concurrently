.. -*- mode: rst -*-

.. image:: https://travis-ci.org/sirkonst/concurrently.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/sirkonst/concurrently

.. image:: https://coveralls.io/repos/github/sirkonst/concurrently/badge.svg?branch=master
    :alt: Code Coverage
    :target: https://coveralls.io/github/sirkonst/concurrently?branch=master

Concurrently
============

Library helps to easily write concurrent executed code blocks.

Quick example::

    import asyncio
    from concurrently import concurrently


    async def amain(loop):
        """
        How to fetch some web pages with concurrently.
        """
        urls = [  # define pages urls
            'http://test/page_1',
            'http://test/page_2',
            'http://test/page_3',
            'http://test/page_4',
        ]
        results = {}

        # immediately run wrapped function concurrent
        # in 2 thread (asyncio coroutines)
        @concurrently(2)
        async def fetch_urls():
            for url in urls:
                # some function for download page
                page = await fetch_page(url)
                results[url] = page

        # wait until all concurrent threads finished
        await fetch_urls()
        print(results)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(amain(loop))


Documentation
-------------

See https://concurrently.readthedocs.io/
