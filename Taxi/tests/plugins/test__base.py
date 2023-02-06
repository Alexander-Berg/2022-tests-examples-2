# this test must be always first!


def test_base(repo_comparator, default_repository, default_base):
    repo_comparator(default_repository, default_base, 'base')


def test_multi_unit_base(
        repo_comparator, multi_unit_repository, multi_unit_base,
):
    repo_comparator(multi_unit_repository, multi_unit_base, 'multi_unit_base')
