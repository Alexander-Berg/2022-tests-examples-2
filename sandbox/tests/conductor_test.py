import unittest
import requests_mock
import requests
import urlparse

from sandbox.projects.common import conductor


class ApiTest(unittest.TestCase):
    api = None
    secret = "test_oauth_key"

    def setUp(self):
        task_mock = DummyObject()
        task_mock.url = "http://example.com"

        self.api = conductor.Api(task_mock, conductor.NoAuth())

    @requests_mock.mock()
    def test_ticket_status_passing_ticket_query(self, rmock):
        ticket_id = 31337

        def req_callback(request, context):
            self.assertIn("ticket", request.qs)
            self.assertEqual(request.qs["ticket"][0], str(ticket_id))

        rmock.get("/api/generator/glader.ticket_status", content=req_callback)

        self.api.ticket_status(ticket_id)

    @requests_mock.mock()
    def test_ticket_status_returning_content_on_200(self, rmock):
        ticket_id = 31337
        test_response = "testok"

        rmock.get("/api/generator/glader.ticket_status", text=test_response)

        res = self.api.ticket_status(ticket_id)

        self.assertEqual(res, test_response)

    @requests_mock.mock()
    def test_ticket_status_raising_on_non_200(self, rmock):
        ticket_id = 31337

        rmock.get("/api/generator/glader.ticket_status", status_code=400)

        with self.assertRaises(requests.HTTPError):
            self.api.ticket_status(ticket_id)

    @requests_mock.mock()
    def test_ticket_status_raising_on_timeout(self, rmock):
        ticket_id = 31337

        rmock.get("/api/generator/glader.ticket_status", exc=requests.ConnectTimeout)

        with self.assertRaises(requests.ConnectTimeout):
            self.api.ticket_status(ticket_id)

    def test_ticket_add_raising_on_empty_packages(self):
        with self.assertRaises(Exception) as cm:
            self.api.ticket_add({}, conductor.BRANCHES[0])
            e = cm.exception
            self.assertRegexpMatches(e.message, "No packages")

    def test_ticket_add_raising_on_wrong_branch(self):
        with self.assertRaises(Exception) as cm:
            self.api.ticket_add({"abc": "123"}, "lol")
            e = cm.exception
            self.assertRegexpMatches(e.message, "Incorrect branch")

    @requests_mock.mock()
    def test_ticket_add_packages_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        def req_callback(request, context):
            body = self.prepare_body(request)

            for i, (k, v) in enumerate(packages.items()):
                p_id = "package[%d]" % i
                v_id = "version[%d]" % i

                self.assertTrue(p_id in body)
                self.assertEqual(unicode(k), body[p_id])

                self.assertTrue(v_id in body)
                self.assertEqual(unicode(v), body[v_id])

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable")

    @requests_mock.mock()
    def test_ticket_add_workflow(self, rmock):
        packages = {"package1": "ver1", "package2": "ver2"}
        workflows = [('project1', 'wf1'), ('project1', 'wf2')]

        def req_callback(request, context):
            body = self.prepare_body(request)

            for i, (project, workflow) in enumerate(workflows):
                workflow_key = "filters[workflows][%d][workflow]" % i
                project_key = "filters[workflows][%d][project]" % i

                self.assertTrue(workflow_key in body)
                self.assertEqual(unicode(workflow), body[workflow_key])

                self.assertTrue(project_key in body)
                self.assertEqual(unicode(project), body[project_key])

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", workflows=workflows)

    @requests_mock.mock()
    def test_ticket_add_remove_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        rm_idx = 1
        remove = [packages.keys()[rm_idx]]

        def req_callback(request, context):
            body = self.prepare_body(request)

            rm_id = "remove[%s]" % rm_idx
            self.assertTrue(rm_id in body)
            self.assertEqual(body[rm_id], "1")

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", remove=remove)

    @requests_mock.mock()
    def test_ticket_add_mailcc_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        mailcc = ["test1@test.com", "test2@test.com"]
        mailcc_idx = "ticket[mailcc]"

        def req_callback(request, context):
            body = self.prepare_body(request)

            self.assertTrue(mailcc_idx in body)
            self.assertEqual(body[mailcc_idx], ",".join(mailcc))

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", mailcc=mailcc)

    @requests_mock.mock()
    def test_ticket_add_skip_restart_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        skip_restart_idx = "ticket[skip_restart]"

        def req_callback(request, context):
            body = self.prepare_body(request)

            self.assertTrue(skip_restart_idx in body)
            self.assertEqual(body[skip_restart_idx], "1")

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", skip_restart=True)

    @requests_mock.mock()
    def test_ticket_add_no_autoinstall_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        no_autoinstall_idx = "ticket[do_not_autoinstall]"

        def req_callback(request, context):
            body = self.prepare_body(request)

            self.assertTrue(no_autoinstall_idx in body)
            self.assertEqual(body[no_autoinstall_idx], "1")

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", no_autoinstall=True)

    @requests_mock.mock()
    def test_ticket_add_projects_passed(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        projects = ["test1", "test2"]
        projects_idx = "filters[projects][]"

        def req_callback(request, context):
            body = self.prepare_body(request)

            self.assertTrue(projects_idx in body)
            self.assertEqual(body[projects_idx], ",".join(projects))

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable", projects=projects)

    @requests_mock.mock()
    def test_ticket_add_raises_on_non_200(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        rmock.post("/auth_update/ticket_add", status_code=400)

        with self.assertRaises(requests.HTTPError):
            self.api.ticket_add(packages, "stable")

    @requests_mock.mock()
    def test_ticket_add_raises_on_timeout(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        rmock.post("/auth_update/ticket_add", exc=requests.ConnectTimeout)

        with self.assertRaises(requests.ConnectTimeout):
            self.api.ticket_add(packages, "stable")

    @requests_mock.mock()
    def test_ticket_add_returning_content_on_200(self, rmock):
        packages = {"package1": "1", "package2": "2"}
        content = "test"

        rmock.post("/auth_update/ticket_add", text=content)

        res = self.api.ticket_add(packages, "stable")
        self.assertEqual(res, content)

    @requests_mock.mock()
    def test_ticket_add_oauth_headers(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        self.api.auth = conductor.OauthAuth(self.secret)

        def req_callback(request, context):
            self.assertTrue("Authorization" in request.headers)
            self.assertTrue(self.secret in request.headers["Authorization"])

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable")

    @requests_mock.mock()
    def test_ticket_add_session_cookie(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        self.api.auth = conductor.SessionAuth(self.secret)

        def req_callback(request, context):
            self.assertTrue("Session_id=test_oauth_key" in request.headers["Cookie"])

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable")

    @requests_mock.mock()
    def test_ticket_add_auth_cookie(self, rmock):
        packages = {"package1": "1", "package2": "2"}

        self.api.auth = conductor.AuthCookie(self.secret)

        def req_callback(request, context):
            self.assertTrue("conductor_auth=test_oauth_key" in request.headers["Cookie"])

        rmock.post("/auth_update/ticket_add", content=req_callback)

        self.api.ticket_add(packages, "stable")

    @staticmethod
    def prepare_body(request):
        return dict(map(lambda (k, v): (str(k), v[0]), urlparse.parse_qs(request.text).items()))


class DummyObject(object):
    id = "testid"
    pass
