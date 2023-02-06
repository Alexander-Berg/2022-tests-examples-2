from collections import namedtuple
from django.test import TestCase
from unittest.mock import patch
from random import shuffle
from copy import copy

from ..models import ABCService
from ..utils import pull_abc_service_info

ABCServiceInfo = namedtuple(
    "ABCServiceInfo",
    [
        "id",
        "slug",
        "parent",
    ],
)

TEST_ABC_SERVICES = {
    10: ABCServiceInfo(10, "test_service_10", None),
    11: ABCServiceInfo(11, "test_service_11", None),
    12: ABCServiceInfo(12, "test_service_12", None),
    13: ABCServiceInfo(13, "test_service_13", None),
    14: ABCServiceInfo(14, "test_service_14", None),
    15: ABCServiceInfo(15, "test_service_15", None),
    16: ABCServiceInfo(16, "test_service_16", None),
    17: ABCServiceInfo(17, "test_service_17", None),
    18: ABCServiceInfo(18, "test_service_18", None),
    19: ABCServiceInfo(19, "test_service_19", None),
    20: ABCServiceInfo(20, "test_service_20", None),
    1100: ABCServiceInfo(1100, "invalid_parent", 1000),
    2000: ABCServiceInfo(2000, "childfree", None),
    3000: ABCServiceInfo(3000, "parent_onechild", None),
    3100: ABCServiceInfo(3100, "child_onechild", 3000),
    4000: ABCServiceInfo(4000, "parent_two_childs", None),
    4100: ABCServiceInfo(4100, "child1_two_childs", 4000),
    4200: ABCServiceInfo(4200, "child2_two_childs", 4000),
    5000: ABCServiceInfo(5000, "great_ancestor", None),
    5100: ABCServiceInfo(5100, "descendant_no_childs", 5000),
    5200: ABCServiceInfo(5200, "descendant_one_child", 5000),
    5210: ABCServiceInfo(5210, "grandchild_one_child", 5200),
    5300: ABCServiceInfo(5300, "descendant_two_childs", 5000),
    5310: ABCServiceInfo(5310, "grandchild_two_childs_1", 5300),
    5320: ABCServiceInfo(5320, "grandchild_two_childs_2", 5300),
}


class ABCPullTestCase(TestCase):
    @patch("l3abc.utils._ABC_API")
    def test_pull_abc_service_info(self, abc_api_mock):
        # initial pull
        # shuffled randomly on purpose
        test_abc_services_list = list(TEST_ABC_SERVICES.values())
        total_nodes = len(test_abc_services_list)
        total_roots = len([node for node in test_abc_services_list if not node.parent])
        shuffle(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, 0)
        self.assertEqual(pull_result.created, total_nodes)
        self.assertEqual(pull_result.updated, 0)
        self.assertEqual(pull_result.deleted, 0)
        abc_invalid_parent = ABCService.objects.get(abc_id=1100)
        self.assertEqual(abc_invalid_parent.abc_slug, "invalid_parent")
        self.assertIsNone(abc_invalid_parent.parent)
        # invalid_parent has no real parent, that's why +1
        self.assertEqual(ABCService.objects.root_nodes().count(), total_roots + 1)
        great_ancestor = ABCService.objects.get(abc_id=5000)
        self.assertEqual(great_ancestor.get_children().count(), 3)
        self.assertEqual(great_ancestor.get_descendant_count(), 6)
        self.assertEqual(ABCService.objects.get(abc_id=5320).get_ancestors().count(), 2)
        self.assertEqual(ABCService.objects.get(abc_id=5210).get_root(), great_ancestor)
        self.assertTrue(abc_invalid_parent.is_root_node())
        self.assertTrue(abc_invalid_parent.is_leaf_node())
        descendant_one_child = ABCService.objects.get(abc_id=5200)
        self.assertTrue(descendant_one_child.is_child_node())
        self.assertFalse(descendant_one_child.is_leaf_node())

        # add new root node (8000)
        # add new child node (2100)
        # delete one child node (5320)
        # 4000 -> 8000 (new parent)
        # 5210 -> 4200 (new parent)
        # 5100 -> None (now it's root node)
        test_abc_services = copy(TEST_ABC_SERVICES)
        test_abc_services[8000] = ABCServiceInfo(8000, "new_root", None)
        test_abc_services[2100] = ABCServiceInfo(2100, "parent_in_db_already", 2000)
        del test_abc_services[5320]
        test_abc_services[4000] = ABCServiceInfo(4000, "parent_two_childs", 8000)
        test_abc_services[5210] = ABCServiceInfo(5210, "grandchild_one_child", 4200)
        test_abc_services[5100] = ABCServiceInfo(5100, "descendant_no_childs", None)
        test_abc_services_list = list(test_abc_services.values())
        shuffle(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, total_nodes)  # created in previous run
        self.assertEqual(pull_result.created, 2)
        self.assertEqual(pull_result.updated, 3)
        self.assertEqual(pull_result.deleted, 1)
        total_nodes += 2 - 1  # previous num + created - deleted
        new_arrival = ABCService.objects.get(abc_id=2100)
        self.assertEqual(new_arrival.parent, ABCService.objects.get(abc_id=2000))
        self.assertTrue(new_arrival.is_child_node())
        self.assertTrue(new_arrival.is_leaf_node())
        self.assertFalse(ABCService.objects.filter(abc_id=5320).exists())
        self.assertEqual(ABCService.objects.get(abc_id=5210).parent, ABCService.objects.get(abc_id=4200))
        new_root = ABCService.objects.get(abc_id=8000)
        self.assertEqual(ABCService.objects.get(abc_id=4000).parent, new_root)
        self.assertTrue(new_root.is_root_node())
        self.assertEqual(new_root.get_descendant_count(), 4)
        svc_became_root = ABCService.objects.get(abc_id=5100)
        self.assertTrue(svc_became_root.is_root_node())
        self.assertEqual(svc_became_root.get_descendant_count(), 0)

        # delete big number of nodes; this must fail and do no deletion at all
        abc_api_mock.fetch_services.return_value = [
            ABCServiceInfo(2000, "childfree", None),
            ABCServiceInfo(3000, "onechild_p", None),
        ]
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, total_nodes)
        self.assertEqual(pull_result.created, 0)
        self.assertEqual(pull_result.updated, 0)
        self.assertEqual(pull_result.deleted, 0)

        # force deletion of big number of nodes
        abc_api_mock.fetch_services.return_value = [
            ABCServiceInfo(2000, "childfree", None),
            ABCServiceInfo(3000, "onechild_p", None),
        ]
        pull_result = pull_abc_service_info(force=True)
        self.assertEqual(pull_result.stored, total_nodes)
        self.assertEqual(pull_result.created, 0)
        self.assertEqual(pull_result.updated, 0)
        self.assertEqual(pull_result.deleted, total_nodes - 2)

        # return to initial state
        test_abc_services_list = list(TEST_ABC_SERVICES.values())
        shuffle(test_abc_services_list)
        # restore total_nodes
        total_nodes = len(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, 2)
        self.assertEqual(pull_result.created, total_nodes - 2)
        self.assertEqual(pull_result.updated, 0)
        self.assertEqual(pull_result.deleted, 0)

        # in 5000 --- 5200 --- 5210 tree delete middle node, i.e. 5200
        # we must get 5210 in it's own tree as leaf and root
        # do same for 5000 --- 5300 --- 5310
        #                       |------ 5320 tree, but retain info about 53*0 parents
        # they will be deleted by on_delete=CASCADE
        test_abc_services = copy(TEST_ABC_SERVICES)
        del test_abc_services[5200]
        test_abc_services[5210] = ABCServiceInfo(5210, "grandchild_one_child", None)
        del test_abc_services[5300]
        test_abc_services_list = list(test_abc_services.values())
        shuffle(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        # forcing as we will delete 2 objects out of 25, which is more than threshold
        pull_result = pull_abc_service_info(force=True)
        self.assertEqual(pull_result.stored, total_nodes)
        self.assertEqual(pull_result.created, 0)
        # 1 for 5210 deletion
        # 5310 wasn't updated because it still states it has a parent
        self.assertEqual(pull_result.updated, 1)
        self.assertEqual(pull_result.deleted, 2)
        great_ancestor = ABCService.objects.get(abc_id=5000)
        grand_child_5210 = ABCService.objects.get(abc_id=5210)
        self.assertNotIn(5310, [x.abc_id for x in ABCService.objects.all()])
        self.assertNotEqual(great_ancestor.tree_id, grand_child_5210.tree_id)
        self.assertTrue(grand_child_5210.is_root_node())
        self.assertTrue(grand_child_5210.is_leaf_node())
        self.assertEqual(len(grand_child_5210.get_family()), 1)

        # return middle (5200 and 5300) and leaves (5310 and 5320) nodes back and confirm that trees are consistent
        test_abc_services_list = list(TEST_ABC_SERVICES.values())
        shuffle(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, total_nodes - 4)
        # 5200, 5300, 5310 and 5320 was deleted on previous step; leaves was
        # deleted by on_delete=CASCADE
        self.assertEqual(pull_result.created, 4)
        self.assertEqual(pull_result.updated, 1)  # 5210 parent change
        self.assertEqual(pull_result.deleted, 0)
        great_ancestor = ABCService.objects.get(abc_id=5000)
        grand_child_5210 = ABCService.objects.get(abc_id=5210)
        grand_child_5310 = ABCService.objects.get(abc_id=5310)
        self.assertEqual(great_ancestor.tree_id, grand_child_5210.tree_id)
        self.assertEqual(great_ancestor.tree_id, grand_child_5310.tree_id)
        self.assertEqual(grand_child_5210.parent, ABCService.objects.get(abc_id=5200))
        self.assertFalse(grand_child_5210.is_root_node())
        self.assertTrue(grand_child_5210.is_leaf_node())
        self.assertEqual(len(grand_child_5210.get_ancestors()), 2)
        self.assertEqual(grand_child_5310.parent, ABCService.objects.get(abc_id=5300))
        self.assertFalse(grand_child_5310.is_root_node())
        self.assertTrue(grand_child_5310.is_leaf_node())
        self.assertEqual(len(grand_child_5310.get_ancestors()), 2)

        # convert this
        # 3000 --- 3100
        # 5000 --- 5200 --- 5210
        # into this
        # 3000 --- 5200 --- 3100
        # 5000 --- 5210
        test_abc_services = copy(TEST_ABC_SERVICES)
        test_abc_services[5210] = ABCServiceInfo(5210, "grandchild_one_child", 5000)
        test_abc_services[3100] = ABCServiceInfo(3100, "child_onechild", 5200)
        test_abc_services[5200] = ABCServiceInfo(5200, "descendant_one_child", 3000)
        test_abc_services_list = list(test_abc_services.values())
        shuffle(test_abc_services_list)
        abc_api_mock.fetch_services.return_value = test_abc_services_list
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, total_nodes)
        self.assertEqual(pull_result.created, 0)
        self.assertEqual(pull_result.updated, 3)
        self.assertEqual(pull_result.deleted, 0)
        great_ancestor = ABCService.objects.get(abc_id=5000)
        descendant_5200 = ABCService.objects.get(abc_id=5200)
        child_3100 = ABCService.objects.get(abc_id=3100)
        grand_child_5210 = ABCService.objects.get(abc_id=5210)
        self.assertNotEqual(great_ancestor.tree_id, descendant_5200.tree_id)
        self.assertIn(descendant_5200, child_3100.get_family())
        self.assertIn(great_ancestor, grand_child_5210.get_ancestors())

    @patch("l3abc.utils._ABC_API")
    def test_pull_abc_service_info_changes_in_many_trees(self, abc_api_mock):
        # check how delay_mptt manages many trees updates
        all_abc_dict = {}
        # create 100 trees with 6 members chained to one another
        for tree_id in range(1, 101):
            root_abc_id = tree_id * 100
            all_abc_dict[root_abc_id] = ABCServiceInfo(root_abc_id, f"test_service_{tree_id}_{root_abc_id}", None)
            for member_id in range(1, 6):
                member_abc_id = root_abc_id + member_id
                all_abc_dict[member_abc_id] = ABCServiceInfo(
                    member_abc_id, f"test_service_{tree_id}_{member_abc_id}", member_abc_id - 1
                )
        all_abc_list = list(all_abc_dict.values())
        shuffle(all_abc_list)
        abc_api_mock.fetch_services.return_value = list(all_abc_dict.values())
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, 0)
        self.assertEqual(pull_result.created, 600)
        # in case of incosistency this will fail
        for obj in ABCService.objects.all():
            obj.get_root()

        # put new member in a middle of the chain for half of trees
        for tree_id in range(1, 51):
            new_member_id = tree_id * 100 + 6
            all_abc_dict[new_member_id] = ABCServiceInfo(
                new_member_id, f"test_service_{tree_id}_{new_member_id}", new_member_id - 3
            )
            all_abc_dict[new_member_id - 2] = ABCServiceInfo(
                new_member_id - 2, f"test_service_{tree_id}_{new_member_id-2}", new_member_id
            )
        shuffle(all_abc_list)
        abc_api_mock.fetch_services.return_value = list(all_abc_dict.values())
        pull_result = pull_abc_service_info()
        self.assertEqual(pull_result.stored, 600)
        self.assertEqual(pull_result.created, 50)
        self.assertEqual(pull_result.updated, 50)
        # in case of incosistency this will fail
        for obj in ABCService.objects.all():
            obj.get_root()
