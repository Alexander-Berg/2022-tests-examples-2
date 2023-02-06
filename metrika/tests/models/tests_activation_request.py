import metrika.admin.python.bishop.frontend.tests.helper as tests_helper

import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.exceptions as bp_exceptions


class TestDeploy(tests_helper.BishopTestCase):
    def test_normal(self):
        self._update_template('template.txt')
        self._update_template('template.txt')

        activation_requests = bp_models.ActivationRequest.objects.filter(
            config__program__name='plaintext_program',
            config__environment__name='root.programs.plaintext_program.production',
            status='opened',
        )
        to_deploy = activation_requests[1]
        to_obsolete = activation_requests[0]

        self.assertEqual(to_obsolete.status, 'opened')
        self.assertTrue(to_obsolete.is_opened)
        self.assertTrue(to_obsolete.is_deployable)
        self.assertFalse(to_obsolete.config.active)

        self.assertEqual(to_deploy.status, 'opened')
        self.assertTrue(to_deploy.is_opened)
        self.assertTrue(to_deploy.is_deployable)
        self.assertFalse(to_deploy.config.active)

        to_deploy.deploy(
            request=self._request,
            response=self._response,
        )
        to_obsolete.refresh_from_db()

        self.assertEqual(to_deploy.status, 'deployed')
        self.assertTrue(to_deploy.is_deployed)
        self.assertFalse(to_deploy.is_deployable)

        self.assertEqual(to_obsolete.status, 'obsolete')
        self.assertTrue(to_obsolete.is_obsolete)
        self.assertFalse(to_obsolete.is_deployable)

        config = to_deploy.config
        self.assertEqual(
            bp_models.Config.objects.filter(program=config.program, environment=config.environment, active=True).count(),
            1
        )


class TestUpdate(tests_helper.BishopTestCase):
    def test_normal(self):
        self._update_template('template.txt')
        ar = bp_models.ActivationRequest.objects.filter(status='opened')[0]
        response = ar.update(
            request=self._request,
            response=self._response,
            status='declined',
        )
        self.assertTrue(
            response.result,
        )
        ar.refresh_from_db()
        self.assertEqual(
            ar.status,
            'declined',
        )

    def test_invalid_status(self):
        self._update_template('template.txt')
        ar = bp_models.ActivationRequest.objects.filter(status='opened')[0]
        with self.assertRaises(bp_exceptions.BishopError):
            ar.update(
                request=self._request,
                response=self._response,
                status='000pened',
            )
