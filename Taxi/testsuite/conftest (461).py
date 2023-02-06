# root conftest for service invoices-archive
pytest_plugins = [
    'invoices_archive_plugins.pytest_plugins',
    'tests_invoices_archive.mocks.invoices_archive',
    'tests_invoices_archive.mocks.order_archive',
]
