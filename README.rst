``confluence-cloud``: a minimalist Confluence Cloud REST API client
===================================================================

::

    pip install git+ssh@github.com:darrenpmeyer/confluence-cloud.git#subdirectory=src

(**NB**: the above doesn't work yet, but will eventually)

.. code-block:: python

    import confluence-cloud

    con_client = confluence-cloud.ConfluenceConnection(
        url='https://youraccount.atlassian.net/wiki',
        userid='youremail@yourdomain.com',
        token=confluence-cloud.api_token_from_file('myapitoken.secret')
    )

    results = con_client.search(
        'type = pages\
         AND (title ~ "instructions" OR text ~ "instructions")'
    )

    for pages in results:
        print(f"Page '{pages.title}' found")

``confluence-cloud`` implements just the portions of the Confluence Cloud REST API that are essential for most searching and content-publishing scripts. It is meant as a lighter-weight, easier-to-use alternative to `Atlassian's official Python module <https://pypi.org/project/atlassian-python-api/>`_ for basic pages operations:

* searching, with the aim of getting a link to a pages
* downloading a pages's content
* moving a pages
* publishing a new pages or a new version of a pages
* removing a pages
* manipulating pages labels


Status
~~~~~~

**Alpha**: still being actively developed. Interface subject to change without notice or tag

Working:

* Connect and authenticate
* Get current user info
* Search for pages by title
* Retrieve pages by IDs
* Update pages (with limitations - mainly no Draft support)
* Create pages (with limitations - mainly no Draft support)

