Info
------------

Tornado project which monitors urls provided.
As for now it supports file based url reader and persist information in memory.


Manual
------------

1. Install tormon

.. code-block:: bash

    $ pip install tormon


2. Run tormon providing path to file which has list of urls (each in separate line) to monitor:

.. code-block:: bash

    $ tor-mon --host=0.0.0.0 --port=8081 --config=/tmp/config.yml --debug=true

3. Query api to get information:

.. code-block:: bash

    $ curl http://localhost:8081/api/urls/
    $ curl http://localhost:8081/api/stats/
    $ curl http://localhost:8081/api/url/\?url\=<url>


4. Optionally You can install redis and hiredis