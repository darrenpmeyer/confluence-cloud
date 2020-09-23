``confluence-cloud``: a minimalist Confluence Cloud REST API client
===================================================================

::

    pip install git+ssh@github.com:darrenpmeyer/confluence-cloud.git

.. code-block:: python

    import confluence-cloud

    con_client = confluence-cloud.ConfluenceConnection(
        url='https://youraccount.atlassian.net/wiki',
        userid='youremail@yourdomain.com',
        token=confluence-cloud.api_token_from_file('myapitoken.secret')
    )

    results = con_client.search(
        'type = page\
         AND (title ~ "instructions" OR text ~ "instructions")'
    )

    for page in results:
        print(f"Page '{page.title}' found")

``confluence-cloud`` implements just the portions of the Confluence Cloud REST API that are essential for most searching and content-publishing scripts. It is meant as a lighter-weight, easier-to-use alternative to `Atlassian's official Python module <https://pypi.org/project/atlassian-python-api/>`_ for basic page operations:

* searching, with the aim of getting a link to a page
* downloading a page's content
* moving a page
* publishing a new page or a new version of a page
* removing a page
* manipulating page labels


Status
~~~~~~

**Alpha**: still being actively developed. Interface subject to change without notice or tag

