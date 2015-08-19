Info
------------

Tornado project which monitors urls provided.
As for now it supports file based url reader and persist information in memory.


Manual
------------

1. Clone project

.. code-block:: bash

    $ git clone git@github.com:jnosal/tormon.git .

2. Install virtualenv

.. code-block:: bash

    $ virtualenv env/ && source env/bin/activate

3. Install requirements

.. code-block:: bash

    $ pip install -r requirements.txt

4. Run tormon providing path to file which has list of urls (each in separate line) to monitor:

.. code-block:: bash

    $ python run.py --host=0.0.0.0 --port=8081 --filename=/tmp/urls.txt --debug=true

5. Go to localhost:8081 in your web browser to see self refreshing UI with meta information

6. Query api to get information:

.. code-block:: bash

    $ curl http://localhost:8081/api/urls/
    $ curl http://localhost:8081/api/stats/
    $ curl http://localhost:8081/api/url/\?url\=<url>