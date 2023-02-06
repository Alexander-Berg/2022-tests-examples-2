import os
import yaml
from odoo.addons.lavka.backend.models.ir_model_access import APP_ROLES_MAPPER, ALLOWED_PERMISSION
from odoo.tests.common import HttpSavepointCase, tagged

REL_ACCESSES_PATH = '../../security/access_rules.yaml'
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ACCESSES_PATH = os.path.join(CUR_DIR, REL_ACCESSES_PATH)


@tagged("lavka", "accesses")
class TestAccessRulesFile(HttpSavepointCase):
    def test_access_rules_file(self):
        models_list = []
        with open(ACCESSES_PATH, 'r') as rules_file:
            rules_data = yaml.safe_load(rules_file)
        app_roles = rules_data['app_roles']
        for role in app_roles.values():
            self.env.ref(role)
        mapped_models = rules_data.get('models')
        roles = rules_data.get('roles')
        for role, rules in roles.items():
            group_name = f'lavka.group_{role}'
            self.env.ref(group_name)
            for models_group, permissions in rules.items():
                if models_group == 'apps':
                    for app, app_role in permissions.items():
                        app_group_name = APP_ROLES_MAPPER.get(f'{app}/{app_role}')
                        self.assertTrue(
                            app_group_name,
                            f'No role found in app_roles_mapper for {app}/{app_role}'
                        )
                        self.env.ref(app_group_name)
                    continue
                if 'approve' in permissions:
                    approve_group_name = f'lavka.approve_{models_group}'
                    self.env.ref(approve_group_name)
                models = mapped_models.get(models_group)
                self.assertTrue(models, f'No models specified for group {models_group}')
                perms_set = set(permissions)
                wrong_perms = perms_set - ALLOWED_PERMISSION
                self.assertFalse(
                    wrong_perms,
                    f'Wrong permissions {wrong_perms} for models "{models_group}" in role "{role}"'
                )
                models_list += models
                # for model in models:
                #     if model not in models_list:
                #         models_list.append(models)
        models_set = set(models_list)
        db_models = self.env['ir.model'].search([('model', 'in', models_list)])
        db_models_set = {i.model for i in db_models}
        lost_db_models = models_set - db_models_set
        self.assertEqual(
            len(db_models),
            len(models_set),
            f'Can\'t find models {lost_db_models} in ir.models'
        )


# @tagged("lavka", "accesses")
# class TestUpdateAccessRules(HttpSavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super(TestUpdateAccessRules, cls).setUpClass()
#         cls.factory = cls.env['factory_common']
#         cls.groups = cls.factory.create_groups(qty=5)
# #         TODO: КАК СОЗДАТЬ ТЕСТОВЫЕ РОЛИ КОТОРЫЕ БУДУТ НАХОДИТЬСЯ ЧЕРЕЗ self.env.ref???
