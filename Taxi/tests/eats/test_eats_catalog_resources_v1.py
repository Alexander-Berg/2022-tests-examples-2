# # coding: utf-8
#
# import os
#
# import pytest
#
# from cprojects.eats.catalog.resources.v1 import StaticResources
#
# pytestmark = [pytest.mark.filterwarnings('ignore::DeprecationWarning')]
#
#
# SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
#
#
# def test_orders_cube_api_raw():
#     StaticResources.load_from_dir(
#         os.path.join(
#             SCRIPT_DIR,
#             'static',
#             'eats_catalog_resources_v1',
#             'static_resources',
#         ),
#     )
#
#     with pytest.raises(RuntimeError):
#         StaticResources.load_from_dir(
#             os.path.join(
#                 SCRIPT_DIR,
#                 'static',
#                 'eats_catalog_resources_v1',
#                 'broken_static_resources',
#             ),
#         )
