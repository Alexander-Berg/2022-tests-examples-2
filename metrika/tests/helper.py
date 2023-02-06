import django.test
import django.contrib.auth.models as auth_models

import metrika.pylib.structures.dotdict as mdd
import metrika.pylib.noodle.response as nresponse

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.bishop.management.commands.sync_permissions as sp


class BishopBaseTestCase(object):
    fixtures = ('metrika/admin/python/bishop/frontend/bishop/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()
        self.user = auth_models.User.objects.get(username='volozh')
        sp.Command().assign_permissions({})
        group = auth_models.Group.objects.get(name='users')
        self.user.groups.add(group)

    @property
    def _request(self):
        return mdd.DotDict.from_dict({
            'user': self.user,
            'META': mdd.DotDict(),
        })


class BishopTestCase(BishopBaseTestCase, django.test.TestCase):
    @property
    def _response(self):
        return nresponse.NoodleResponse()

    def _update_template(self, name, **kwargs):
        template = bp_models.Template.objects.get(name=name)

        if not kwargs.get('format'):
            kwargs['format'] = template.format

        text = template.text + '\n' + kwargs.get('text', 'justvalue')
        kwargs['text'] = text

        response = template.update(
            response=self._response,
            request=self._request,
            **kwargs
        )
        self.assertTrue(response.result)

    def _get_template(self, name=None, **kwargs):
        if name is None:
            name = self.template_name
        return bp_models.Template.objects.get(
            name=name,
            **kwargs
        )

    def _get_program(self, name=None, **kwargs):
        if name is None:
            name = self.program_name
        return bp_models.Program.objects.get(
            name=name,
            **kwargs
        )

    def _get_environment(self, name=None, **kwargs):
        if name is None:
            name = self.environment_name
        return bp_models.Environment.objects.get(
            name=name,
            **kwargs
        )


class BishopApiTestCase(BishopBaseTestCase, django.test.TestCase):
    @property
    def _response(self):
        return nresponse.NoodleApiResponse()


class BishopHtmlTestCase(BishopBaseTestCase, django.test.TestCase):
    def _assert(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class BishopAjaxTestCase(BishopBaseTestCase, django.test.TestCase):
    def _assert(self, url, http_type='get'):
        response = getattr(self.client, http_type)(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            tests_api_schemas.BishopAjaxSchema(data).validate()
        )
