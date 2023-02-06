import textwrap

from sandbox.projects.autocheck.lib.core import errors


error_types = [
    (errors.DistbuildRepositoryError, textwrap.dedent('''distbuild{297,300,343,382,404,409,458,476,489,496,513,530,541,542,568,641,651,668,676,693}.search.yandex.net -
    Repository acquisition failed, build_uid = a9e7affb-b1efa9cd-d32235c-d57f5e-0 repository = $(SOURCE_ROOT)=svn://arc/trunk/arcadia@4234323
    message = Unable to acquire repository, status is failed, message is Unable to acquire revision because Code = ESE_ACQUITION_FAILED,
    message = Code = ESE_INCORRECT_REVISION, message = Revision 4234323 is too old''')),
    (errors.YmakeCrashedError, textwrap.dedent('''
    Downloading https://proxy.sandbox.yandex-team.ru/2600180957 [..] OK
    Warn: Failed to get token: No SSH keys could be found for sandbox
    Configuring dependencies for Java
    YMake crashed
    ''')),
]


def test_retriable():
    for error_type, message in error_types:
        found_err = errors.is_none_retriable(message)
        assert found_err is not None
        assert isinstance(found_err, error_type)

    retriable_error = 'SomeError: AAAAA'
    err = errors.is_none_retriable(retriable_error)
    assert err is None
