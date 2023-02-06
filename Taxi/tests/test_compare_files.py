import filecmp
import os

SERVICES_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)


def _path_to_definitions(current_dir):
    return os.path.join(current_dir, 'docs', 'yaml', 'definitions.yaml')


def test_compare_files():
    pdp_dir = os.path.join(SERVICES_DIR, 'pricing_data_preparer')
    pricing_fallback_dir = os.path.join(SERVICES_DIR, 'pricing_fallback')

    pdp_definitions = _path_to_definitions(pdp_dir)
    pricing_fallback_definitions = _path_to_definitions(pricing_fallback_dir)
    assert filecmp.cmp(pdp_definitions, pricing_fallback_definitions)
