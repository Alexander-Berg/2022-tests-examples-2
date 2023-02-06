# -*- coding: utf-8 -*-

import json

from passport.backend.core.builders.abc.exceptions import BaseABCError
from passport.backend.core.builders.staff.exceptions import BaseStaffError
from passport.backend.core.builders.yasm_agent import get_yasm_agent
from passport.backend.core.builders.yasm_agent.faker.fake_yasm_agent import (
    FakeYasmAgent,
    TEST_YASM_AGENT_OK_RESPONSE,
)
from passport.backend.vault.api.builders import (
    get_abc,
    get_staff,
)
from passport.backend.vault.api.errors import (
    ABCError,
    StaffError,
)
from passport.backend.vault.api.models import (
    AbcDepartmentInfo,
    AbcRole,
    AbcScope,
    ExternalRecord,
    StaffDepartmentInfo,
    TvmAppInfo,
    UserInfo,
)
from passport.backend.vault.api.stats.golovan import make_golovan_metrics
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.fake_abc import (
    FakeABC,
    TEST_ABC_EMPTY_RESPONSE,
    TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_ABC_GET_ALL_PERSONS_RESPONSE,
    TEST_ABC_GET_ALL_ROLES_RESPONSE,
    TEST_ABC_GET_ALL_TVM_APPS_RESPONSE,
)
from passport.backend.vault.api.test.fake_staff import (
    FakeStaff,
    TEST_DISABLED_STAFF_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_DISABLED_STAFF_GET_ALL_PERSONS_RESPONSE,
    TEST_STAFF_EMPTY_RESPONSE,
    TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_STAFF_GET_ALL_PERSONS_RESPONSE,
)
from passport.backend.vault.api.test.logging_mock import LoggingMock


class TestBuildersIdPagination(BaseTestClass):
    fill_database = False
    maxDiff = None

    def make_fake_staff_response(self, start_id=1, end_id=1000):
        return {
            'result': [
                {
                    'id': i,
                    'name': 'fake staff %s' % i,
                }
                for i in range(start_id, end_id + 1)
            ]
        }

    def make_fake_abc_response(self, start_id=1, end_id=1000, next=None):
        return {
            'next': next,
            'results': [
                {
                    'id': i,
                    'name': 'fake abc %s' % i,
                }
                for i in range(start_id, end_id + 1)
            ]
        }

    def test_staff_id_pagination(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_side_effect(
                    'get_all_departments',
                    [
                        self.make_fake_staff_response(1, 100),
                        self.make_fake_staff_response(101, 200),
                        self.make_fake_staff_response(201, 250),
                    ]
                )
                r = get_staff(self.config)._make_request_with_id_pagination(
                    url_suffix='/v3/groups',
                    method='GET',
                    params={
                        '_fields': 'id,name',
                        'type': 'department',
                    },
                    oauth_token='token',
                    page_size=100,
                )
                self.assertEqual(len(r), 250)
                self.assertEqual(len(fake_staff.requests), 3)
                for i, req in enumerate(fake_staff.requests):
                    req.assert_properties_equal(
                        url='https://staff-api.yandex-team.ru/v3/groups?_limit=100&_fields=id%2Cname%2Cid&type=department&_sort=id&'
                            '_query=id%3E{}'.format(i * 100),
                    )

    def test_abc_cursor_pagination(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_side_effect(
                    'get_all_departments',
                    [
                        self.make_fake_abc_response(1, 100, next='https://abc-back.yandex-team.ru/api/v4/services/?cursor=1'),
                        self.make_fake_abc_response(101, 200, next='https://abc-back.yandex-team.ru/api/v4/services/?cursor=2'),
                        self.make_fake_abc_response(201, 250, next=''),
                    ]
                )
                r = get_abc(self.config)._make_request_with_cursor_pagination(
                    url_suffix='v4/services/',
                    method='GET',
                    params={
                        'fields': 'id,name',
                    },
                    oauth_token='token',
                    page_size=100,
                )
                self.assertEqual(len(r), 250)
                self.assertEqual(len(fake_abc.requests), 3)

                urls = [
                    'https://abc-back.yandex-team.ru/api/v4/services/?fields=id%2Cname&page_size=100',
                    'https://abc-back.yandex-team.ru/api/v4/services/?cursor=1',
                    'https://abc-back.yandex-team.ru/api/v4/services/?cursor=2',
                ]
                for i, req in enumerate(fake_abc.requests):
                    req.assert_properties_equal(url=urls[i])


class TestBuilders(BaseTestClass):
    fill_database = False
    maxDiff = None

    def assert_external_filled_with_staff(self):
        self.assertListEqual(
            map(
                repr,
                ExternalRecord.query.filter(
                    ExternalRecord.external_type == 'staff',
                ).order_by(
                    ExternalRecord.external_id,
                    ExternalRecord.uid,
                ).all()
            ),
            [
                '<ExternalRecord #100-staff-1-0-0>',
                '<ExternalRecord #101-staff-1-0-0>',
                '<ExternalRecord #102-staff-1-0-0>',
                '<ExternalRecord #1120000000035620-staff-1-0-0>',
                '<ExternalRecord #1120000000036175-staff-1-0-0>',
                '<ExternalRecord #1120000000038274-staff-1-0-0>',
                '<ExternalRecord #1120000000039954-staff-1-0-0>',
                '<ExternalRecord #1120000000040289-staff-1-0-0>',
                '<ExternalRecord #100-staff-2-0-0>',
                '<ExternalRecord #101-staff-2-0-0>',
                '<ExternalRecord #102-staff-2-0-0>',
                '<ExternalRecord #1120000000035620-staff-62-0-0>',
                '<ExternalRecord #1120000000036175-staff-62-0-0>',
                '<ExternalRecord #1120000000039954-staff-62-0-0>',
                '<ExternalRecord #1120000000040289-staff-62-0-0>',
                '<ExternalRecord #1120000000036175-staff-422-0-0>',
                '<ExternalRecord #1120000000035620-staff-533-0-0>',
                '<ExternalRecord #1120000000036175-staff-533-0-0>',
                '<ExternalRecord #1120000000039954-staff-533-0-0>',
                '<ExternalRecord #1120000000040289-staff-533-0-0>',
                '<ExternalRecord #1120000000038274-staff-1538-0-0>',
                '<ExternalRecord #1120000000038274-staff-2864-0-0>',
                '<ExternalRecord #1120000000038274-staff-3051-0-0>',
                '<ExternalRecord #1120000000035620-staff-3101-0-0>',
                '<ExternalRecord #1120000000036175-staff-3101-0-0>',
                '<ExternalRecord #1120000000039954-staff-3101-0-0>',
                '<ExternalRecord #1120000000040289-staff-3101-0-0>',
                '<ExternalRecord #1120000000040289-staff-3132-0-0>',
                '<ExternalRecord #1120000000035620-staff-3224-0-0>',
                '<ExternalRecord #1120000000036175-staff-3224-0-0>',
                '<ExternalRecord #1120000000039954-staff-3224-0-0>',
                '<ExternalRecord #1120000000040289-staff-3224-0-0>',
                '<ExternalRecord #1120000000039954-staff-3491-0-0>',
                '<ExternalRecord #1120000000035620-staff-4045-0-0>',
                '<ExternalRecord #1120000000035620-staff-4112-0-0>',
                '<ExternalRecord #1120000000036175-staff-4112-0-0>',
                '<ExternalRecord #1120000000038274-staff-4112-0-0>',
                '<ExternalRecord #1120000000039954-staff-4112-0-0>',
                '<ExternalRecord #1120000000040289-staff-4112-0-0>',
                '<ExternalRecord #1120000000038274-staff-5698-0-0>',
            ],
        )

    def assert_external_filled_with_abc(self):
        self.assertListEqual(
            map(
                repr,
                ExternalRecord.query.filter(
                    ExternalRecord.external_type == 'abc',
                ).order_by(
                    ExternalRecord.uid,
                    ExternalRecord.external_id,
                    ExternalRecord.external_scope_id,
                    ExternalRecord.external_role_id,
                ).all()
            ),
            [
                '<ExternalRecord #1120000000000878-abc-50-0-8>',
                '<ExternalRecord #1120000000000878-abc-50-0-16>',
                '<ExternalRecord #1120000000000878-abc-50-5-0>',
                '<ExternalRecord #1120000000000878-abc-50-8-0>',
                '<ExternalRecord #1120000000004890-abc-50-0-8>',
                '<ExternalRecord #1120000000004890-abc-50-5-0>',
                '<ExternalRecord #1120000000005594-abc-14-0-630>',
                '<ExternalRecord #1120000000005594-abc-14-17-0>',
                '<ExternalRecord #1120000000027354-abc-50-0-16>',
                '<ExternalRecord #1120000000027354-abc-50-8-0>',
                '<ExternalRecord #1120000000038274-abc-14-0-8>',
                '<ExternalRecord #1120000000038274-abc-14-5-0>',
            ],
        )

    def assert_external_records_is_empty(self):
        self.assertEqual(
            ExternalRecord.query.order_by(
                ExternalRecord.uid,
                ExternalRecord.external_scope_id,
            ).count(),
            0,
        )

    def assert_departments_filled_with_abc(self, state=0):
        self.assertListEqual(
            list(map(
                repr,
                AbcDepartmentInfo.query.order_by(
                    AbcDepartmentInfo.id,
                ).all()
            )),
            [
                '<AbcDepartmentInfo #2 unique_name:"home", state:{}>'.format(state),
                '<AbcDepartmentInfo #6 unique_name:"mobile", state:{}>'.format(state),
                '<AbcDepartmentInfo #8 unique_name:"phonedetect", state:{}>'.format(state),
                '<AbcDepartmentInfo #11 unique_name:"mobileyandex", state:{}>'.format(state),
                '<AbcDepartmentInfo #14 unique_name:"passp", state:{}>'.format(state),
                '<AbcDepartmentInfo #16 unique_name:"lbs", state:{}>'.format(state),
                '<AbcDepartmentInfo #17 unique_name:"tanker", state:{}>'.format(state),
                '<AbcDepartmentInfo #20 unique_name:"stat", state:{}>'.format(state),
                '<AbcDepartmentInfo #22 unique_name:"custom", state:{}>'.format(state),
                '<AbcDepartmentInfo #25 unique_name:"search-quality", state:{}>'.format(state),
                '<AbcDepartmentInfo #26 unique_name:"buki", state:{}>'.format(state),
                '<AbcDepartmentInfo #28 unique_name:"snippets", state:{}>'.format(state),
                '<AbcDepartmentInfo #29 unique_name:"searchcontent", state:{}>'.format(state),
                '<AbcDepartmentInfo #36 unique_name:"fetcher", state:{}>'.format(state),
                '<AbcDepartmentInfo #37 unique_name:"specprojects", state:{}>'.format(state),
                '<AbcDepartmentInfo #38 unique_name:"rearr", state:{}>'.format(state),
                '<AbcDepartmentInfo #40 unique_name:"sepe", state:{}>'.format(state),
                '<AbcDepartmentInfo #41 unique_name:"golovan", state:{}>'.format(state),
                '<AbcDepartmentInfo #45 unique_name:"serp", state:{}>'.format(state),
                '<AbcDepartmentInfo #50 unique_name:"suggest", state:{}>'.format(state),
            ]
        )

    def assert_scopes_filled_with_abc(self):
        self.assertListEqual(
            list(map(
                repr,
                AbcScope.query.order_by(
                    AbcScope.id,
                ).all()
            )),
            ['<AbcScope #1 id:1, unique_name:"services_management">',
             '<AbcScope #2 id:2, unique_name:"projects_management">',
             '<AbcScope #3 id:3, unique_name:"analitics">',
             '<AbcScope #4 id:4, unique_name:"design">',
             '<AbcScope #5 id:5, unique_name:"development">',
             '<AbcScope #6 id:6, unique_name:"testing">',
             '<AbcScope #7 id:7, unique_name:"support">',
             '<AbcScope #8 id:8, unique_name:"administration">',
             '<AbcScope #9 id:9, unique_name:"content">',
             '<AbcScope #10 id:10, unique_name:"marketing">',
             '<AbcScope #11 id:11, unique_name:"sales_management">',
             '<AbcScope #12 id:12, unique_name:"quality_management">',
             '<AbcScope #13 id:13, unique_name:"other">',
             '<AbcScope #14 id:14, unique_name:"virtual">',
             '<AbcScope #16 id:16, unique_name:"dutywork">',
             '<AbcScope #17 id:17, unique_name:"tvm_management">',
             '<AbcScope #50 id:50, unique_name:"resources_responsible">',
             '<AbcScope #51 id:51, unique_name:"hardware_management">',
             '<AbcScope #84 id:84, unique_name:"devops">',
             '<AbcScope #85 id:85, unique_name:"cert">',
             '<AbcScope #86 id:86, unique_name:"db_management">',
             '<AbcScope #87 id:87, unique_name:"robots_management">',
             '<AbcScope #90 id:90, unique_name:"quotas_management">']
        )

    def assert_roles_filled_with_abc(self):
        self.assertListEqual(
            list(map(
                repr,
                AbcRole.query.order_by(
                    AbcRole.id,
                ).all()
            )),
            [
                '<AbcRole #1 id:1, english_name:"Head of product">',
                '<AbcRole #2 id:2, english_name:"Project manager">',
                '<AbcRole #3 id:3, english_name:"Content manager ">',
                '<AbcRole #4 id:4, english_name:"Analyst">',
                '<AbcRole #5 id:5, english_name:"Marketing manager">',
                '<AbcRole #6 id:6, english_name:"Advertising manager">',
                '<AbcRole #8 id:8, english_name:"Developer">',
                '<AbcRole #11 id:11, english_name:"Frontend developer">',
                '<AbcRole #13 id:13, english_name:"Designer">',
                '<AbcRole #14 id:14, english_name:"Interface researcher">',
                '<AbcRole #16 id:16, english_name:"System administrator">',
                '<AbcRole #17 id:17, english_name:"Database administrator">',
                '<AbcRole #19 id:19, english_name:"Functional tester">',
                '<AbcRole #21 id:21, english_name:"Load tester">',
                '<AbcRole #22 id:22, english_name:"Technical writer">',
                '<AbcRole #24 id:24, english_name:"Support specialist">',
                '<AbcRole #25 id:25, english_name:"Consultant">',
                '<AbcRole #26 id:26, english_name:"Partner relationship manager">',
                '<AbcRole #27 id:27, english_name:"Sales manager">',
                '<AbcRole #28 id:28, english_name:"Undefined role">',
                '<AbcRole #29 id:29, english_name:"Administrator of assessors">',
                '<AbcRole #30 id:30, english_name:"Videographer">',
                '<AbcRole #31 id:31, english_name:"Cartographer">',
                '<AbcRole #32 id:32, english_name:"Leading cartographer">',
                '<AbcRole #33 id:33, english_name:"Senior cartographer">',
                '<AbcRole #34 id:34, english_name:"Content Project Manager">',
                '<AbcRole #35 id:35, english_name:"Product manager">',
                '<AbcRole #36 id:36, english_name:"Lawyer">',
                '<AbcRole #37 id:37, english_name:"Mobile interface developer">',
                '<AbcRole #38 id:38, english_name:"Server component developer">',
                '<AbcRole #39 id:39, english_name:"Security consultant">',
                '<AbcRole #40 id:40, english_name:"Editor">',
                '<AbcRole #41 id:41, english_name:"Speaker">',
                '<AbcRole #42 id:42, english_name:"Photographer">',
                '<AbcRole #43 id:43, english_name:"Author">',
                '<AbcRole #44 id:44, english_name:"DC infrastructure IT specialist">',
                '<AbcRole #45 id:45, english_name:"Autotest developer">',
                '<AbcRole #46 id:46, english_name:"Architect">',
                '<AbcRole #47 id:47, english_name:"Moderator">',
                '<AbcRole #48 id:48, english_name:"Secretary">',
                '<AbcRole #49 id:49, english_name:"Category manager">',
                '<AbcRole #50 id:50, english_name:"Quality manager">',
                '<AbcRole #51 id:51, english_name:"Service manager">',
                '<AbcRole #52 id:52, english_name:"Deputy head of product">',
                '<AbcRole #53 id:53, english_name:"Office infrastructure IT specialist">',
                '<AbcRole #161 id:161, english_name:"HR-partner">',
                '<AbcRole #181 id:181, english_name:"Approver">',
                '<AbcRole #383 id:383, english_name:"Robot">',
                '<AbcRole #413 id:413, english_name:"Duty">',
                '<AbcRole #556 id:556, english_name:"Virtual user (passp)">',
                '<AbcRole #630 id:630, english_name:"TVM manager">',
                '<AbcRole #700 id:700, english_name:"L3 responsible">',
                '<AbcRole #742 id:742, english_name:"Hardware resources manager">',
                '<AbcRole #830 id:830, english_name:"Responsible">',
                '<AbcRole #960 id:960, english_name:"Certificates responsibe">',
                '<AbcRole #967 id:967, english_name:"Xiva manager">',
                '<AbcRole #1097 id:1097, english_name:"DevOps">',
                '<AbcRole #1258 id:1258, english_name:"MDB admin">',
                '<AbcRole #1259 id:1259, english_name:"MDB viewer">',
                '<AbcRole #1260 id:1260, english_name:"Robots manager">',
                '<AbcRole #1261 id:1261, english_name:"Robots user">',
                '<AbcRole #1369 id:1369, english_name:"Maintenance manager">',
                '<AbcRole #1553 id:1553, english_name:"Quotas manager">',
                '<AbcRole #1563 id:1563, english_name:"MDB admin with inheritance">',
                '<AbcRole #1586 id:1586, english_name:"QYP User">',
                '<AbcRole #1735 id:1735, english_name:"Duty Manager">',
                '<AbcRole #1796 id:1796, english_name:"Capacity Planning Manager">',
            ]
        )

        self.assertListEqual(
            list(map(
                repr,
                sorted(
                    AbcDepartmentInfo.query.filter(
                        AbcDepartmentInfo.id == 14,
                    ).one().roles,
                    key=lambda x: x.id,
                ),
            )),
            [
                '<AbcRole #1 id:1, english_name:"Head of product">',
                '<AbcRole #2 id:2, english_name:"Project manager">',
                '<AbcRole #3 id:3, english_name:"Content manager ">',
                '<AbcRole #4 id:4, english_name:"Analyst">',
                '<AbcRole #5 id:5, english_name:"Marketing manager">',
                '<AbcRole #6 id:6, english_name:"Advertising manager">',
                '<AbcRole #8 id:8, english_name:"Developer">',
                '<AbcRole #11 id:11, english_name:"Frontend developer">',
                '<AbcRole #13 id:13, english_name:"Designer">',
                '<AbcRole #14 id:14, english_name:"Interface researcher">',
                '<AbcRole #16 id:16, english_name:"System administrator">',
                '<AbcRole #17 id:17, english_name:"Database administrator">',
                '<AbcRole #19 id:19, english_name:"Functional tester">',
                '<AbcRole #21 id:21, english_name:"Load tester">',
                '<AbcRole #22 id:22, english_name:"Technical writer">',
                '<AbcRole #24 id:24, english_name:"Support specialist">',
                '<AbcRole #25 id:25, english_name:"Consultant">',
                '<AbcRole #26 id:26, english_name:"Partner relationship manager">',
                '<AbcRole #27 id:27, english_name:"Sales manager">',
                '<AbcRole #28 id:28, english_name:"Undefined role">',
                '<AbcRole #29 id:29, english_name:"Administrator of assessors">',
                '<AbcRole #30 id:30, english_name:"Videographer">',
                '<AbcRole #31 id:31, english_name:"Cartographer">',
                '<AbcRole #32 id:32, english_name:"Leading cartographer">',
                '<AbcRole #33 id:33, english_name:"Senior cartographer">',
                '<AbcRole #34 id:34, english_name:"Content Project Manager">',
                '<AbcRole #35 id:35, english_name:"Product manager">',
                '<AbcRole #36 id:36, english_name:"Lawyer">',
                '<AbcRole #37 id:37, english_name:"Mobile interface developer">',
                '<AbcRole #38 id:38, english_name:"Server component developer">',
                '<AbcRole #39 id:39, english_name:"Security consultant">',
                '<AbcRole #40 id:40, english_name:"Editor">',
                '<AbcRole #41 id:41, english_name:"Speaker">',
                '<AbcRole #42 id:42, english_name:"Photographer">',
                '<AbcRole #43 id:43, english_name:"Author">',
                '<AbcRole #44 id:44, english_name:"DC infrastructure IT specialist">',
                '<AbcRole #45 id:45, english_name:"Autotest developer">',
                '<AbcRole #46 id:46, english_name:"Architect">',
                '<AbcRole #47 id:47, english_name:"Moderator">',
                '<AbcRole #48 id:48, english_name:"Secretary">',
                '<AbcRole #49 id:49, english_name:"Category manager">',
                '<AbcRole #50 id:50, english_name:"Quality manager">',
                '<AbcRole #51 id:51, english_name:"Service manager">',
                '<AbcRole #52 id:52, english_name:"Deputy head of product">',
                '<AbcRole #53 id:53, english_name:"Office infrastructure IT specialist">',
                '<AbcRole #161 id:161, english_name:"HR-partner">',
                '<AbcRole #181 id:181, english_name:"Approver">',
                '<AbcRole #383 id:383, english_name:"Robot">',
                '<AbcRole #413 id:413, english_name:"Duty">',
                '<AbcRole #556 id:556, english_name:"Virtual user (passp)">',
                '<AbcRole #630 id:630, english_name:"TVM manager">',
                '<AbcRole #700 id:700, english_name:"L3 responsible">',
                '<AbcRole #742 id:742, english_name:"Hardware resources manager">',
                '<AbcRole #830 id:830, english_name:"Responsible">',
                '<AbcRole #960 id:960, english_name:"Certificates responsibe">',
                '<AbcRole #967 id:967, english_name:"Xiva manager">',
                '<AbcRole #1097 id:1097, english_name:"DevOps">',
                '<AbcRole #1258 id:1258, english_name:"MDB admin">',
                '<AbcRole #1259 id:1259, english_name:"MDB viewer">',
                '<AbcRole #1260 id:1260, english_name:"Robots manager">',
                '<AbcRole #1261 id:1261, english_name:"Robots user">',
                '<AbcRole #1369 id:1369, english_name:"Maintenance manager">',
                '<AbcRole #1553 id:1553, english_name:"Quotas manager">',
                '<AbcRole #1563 id:1563, english_name:"MDB admin with inheritance">',
                '<AbcRole #1586 id:1586, english_name:"QYP User">',
                '<AbcRole #1735 id:1735, english_name:"Duty Manager">',
                '<AbcRole #1796 id:1796, english_name:"Capacity Planning Manager">',
            ],
        )

    def assert_user_info_filled_with_staff(self, state=0):
        self.assertListEqual(
            list(sorted(map(repr, UserInfo.query.all()))),
            list(sorted([
                '<UserInfo #100 login:"vault-test-100", state:{}>'.format(state),
                '<UserInfo #101 login:"vault-test-101", state:{}>'.format(state),
                '<UserInfo #102 login:"vault-test-102", state:{}>'.format(state),
                '<UserInfo #1120000000035620 login:"mesyarik", state:{}>'.format(state),
                '<UserInfo #1120000000036175 login:"ankineri", state:{}>'.format(state),
                '<UserInfo #1120000000038274 login:"ppodolsky", state:{}>'.format(state),
                '<UserInfo #1120000000039954 login:"crossby", state:{}>'.format(state),
                '<UserInfo #1120000000040289 login:"agniash", state:{}>'.format(state),
            ])),
        )

    def assert_departments_filled_with_staff(self, state=0):
        self.assertListEqual(
            map(
                repr,
                StaffDepartmentInfo.query.order_by(
                    StaffDepartmentInfo.id,
                ).all()
            ),
            [
                '<StaffDepartmentInfo #2 unique_name:"_vault_test_group_1", state:{}>'.format(state),
                '<StaffDepartmentInfo #24 unique_name:"yandex_mnt_infra", state:{}>'.format(state),
                '<StaffDepartmentInfo #45 unique_name:"yandex_mnt_infra_itoffice", state:{}>'.format(state),
                '<StaffDepartmentInfo #64 unique_name:"yandex_search_tech_quality", state:{}>'.format(state),
                '<StaffDepartmentInfo #236 unique_name:"yandex_search_tech_spam", state:{}>'.format(state),
                '<StaffDepartmentInfo #2864 unique_name:"yandex_personal_com_aux_sec", state:{}>'.format(state),
                '<StaffDepartmentInfo #4112 unique_name:"_vault_test_group_2", state:{}>'.format(state),
                '<StaffDepartmentInfo #24936 unique_name:"yandex_search_tech_quality_func", state:{}>'.format(state),
                '<StaffDepartmentInfo #29453 unique_name:"yandex_design_search_vertical", state:{}>'.format(state),
                '<StaffDepartmentInfo #32470 unique_name:"yandex_search_tech_ont", state:{}>'.format(state),
                '<StaffDepartmentInfo #38096 unique_name:"yandex_search_tech_sq", state:{}>'.format(state),
                '<StaffDepartmentInfo #38098 unique_name:"yandex_search_tech_sq_analysis", state:{}>'.format(state),
                '<StaffDepartmentInfo #42112 unique_name:"yandex_rkub_taxi_support_supvod", state:{}>'.format(state),
                '<StaffDepartmentInfo #44003 unique_name:"yandex_rkub_taxi_cust", state:{}>'.format(state),
                '<StaffDepartmentInfo #44283 unique_name:"yandex_rkub_taxi_cust_supp", state:{}>'.format(state),
                '<StaffDepartmentInfo #59086 unique_name:"yandex_rkub_discovery_rec_rank", state:{}>'.format(state),
                '<StaffDepartmentInfo #66040 unique_name:"yandex_search_tech_sq_7195", state:{}>'.format(state),
                '<StaffDepartmentInfo #66046 unique_name:"yandex_search_tech_sq_8135", state:{}>'.format(state),
                '<StaffDepartmentInfo #67071 unique_name:"yandex_edu_personel_0289_8372", state:{}>'.format(state),
                '<StaffDepartmentInfo #67600 unique_name:"as_opdir_8255", state:{}>'.format(state),
                '<StaffDepartmentInfo #73680 unique_name:"yandex_distproducts_morda_commercial_prod_7642", state:{}>'.format(state),
                '<StaffDepartmentInfo #74710 unique_name:"yandex_rkub_taxi_dev_5902", state:{}>'.format(state),
                '<StaffDepartmentInfo #78575 unique_name:"yandex_rkub_taxi_support_6923", state:{}>'.format(state),
                '<StaffDepartmentInfo #79093 unique_name:"ext_2027_3589", state:{}>'.format(state),
                '<StaffDepartmentInfo #80036 unique_name:"yandex_search_tech_sq_3452", state:{}>'.format(state),
                '<StaffDepartmentInfo #82381 unique_name:"yandex_distproducts_browserdev_mobile_taxi_9720_2944_9770", state:{}>'.format(state),
                '<StaffDepartmentInfo #82601 unique_name:"yandex_search_tech_sq_interfaceandtools", state:{}>'.format(state),
                '<StaffDepartmentInfo #82679 unique_name:"ext_yataxi_3452", state:{}>'.format(state),
                '<StaffDepartmentInfo #82741 unique_name:"yandex_rkub_taxi_support_supvod_3678", state:{}>'.format(state),
                '<StaffDepartmentInfo #82743 unique_name:"yandex_rkub_taxi_support_supvod_7398", state:{}>'.format(state),
                '<StaffDepartmentInfo #83658 unique_name:"yandex_edu_personel_5537", state:{}>'.format(state),
                '<StaffDepartmentInfo #83659 unique_name:"yandex_edu_personel_5537_0405", state:{}>'.format(state),
                '<StaffDepartmentInfo #83734 unique_name:"yandex_rkub_taxi_dev_3231", state:{}>'.format(state),
                '<StaffDepartmentInfo #84278 unique_name:"yandex_rkub_taxi_dev_5902_7922", state:{}>'.format(state),
                '<StaffDepartmentInfo #84280 unique_name:"yandex_rkub_taxi_dev_3231_1747", state:{}>'.format(state),
                '<StaffDepartmentInfo #84281 unique_name:"yandex_rkub_taxi_dev_3231_6117", state:{}>'.format(state),
                '<StaffDepartmentInfo #84687 unique_name:"yandex_biz_com_8856", state:{}>'.format(state),
                '<StaffDepartmentInfo #84819 unique_name:"yandex_rkub_taxi_5151_8501_8241", state:{}>'.format(state),
                '<StaffDepartmentInfo #84878 unique_name:"outstaff_2289_8265_5357", state:{}>'.format(state),
                '<StaffDepartmentInfo #86477 unique_name:"yandex_rkub_taxi_5151_8501_9053", state:{}>'.format(state),
                '<StaffDepartmentInfo #87495 unique_name:"outstaff_2289_9459_8766_9989", state:{}>'.format(state),
                '<StaffDepartmentInfo #87859 unique_name:"virtual_robots_3137", state:{}>'.format(state),
                '<StaffDepartmentInfo #88933 unique_name:"yandex_rkub_taxi_support_1683", state:{}>'.format(state),
                '<StaffDepartmentInfo #89623 unique_name:"ext_6887", state:{}>'.format(state),
                '<StaffDepartmentInfo #90711 unique_name:"outstaff_2289_8265_6121_1328", state:{}>'.format(state),
                '<StaffDepartmentInfo #92011 unique_name:"yandex_proffice_support_comm_taxi_2913", state:{}>'.format(state),
                '<StaffDepartmentInfo #92013 unique_name:"yandex_rkub_taxi_support_6923_2643", state:{}>'.format(state),
                '<StaffDepartmentInfo #92015 unique_name:"yandex_rkub_taxi_support_6923_5271", state:{}>'.format(state),
                '<StaffDepartmentInfo #92018 unique_name:"yandex_rkub_taxi_support_6035_1229", state:{}>'.format(state),
                '<StaffDepartmentInfo #93278 unique_name:"yandex_rkub_discovery_rec_tech_5431_9475", state:{}>'.format(state),
                '<StaffDepartmentInfo #93447 unique_name:"yandex_edu_personel_5537_dep80665", state:{}>'.format(state),
                '<StaffDepartmentInfo #93448 unique_name:"yandex_edu_personel_5537_dep03987", state:{}>'.format(state),
                '<StaffDepartmentInfo #93796 unique_name:"yandex_mrkt_mediamrkt_media_taxi_6258_0126", state:{}>'.format(state),
            ]
        )

    def assert_tvm_apps_filled_with_abc(self):
        self.assertListEqual(
            map(
                repr,
                TvmAppInfo.query.order_by(
                    TvmAppInfo.tvm_client_id,
                ).all()
            ),
            [
                '<TvmAppInfo #2000079 name:"\xd0\x9f\xd0\xb0\xd1\x81\xd0\xbf\xd0\xbe\xd1\x80\xd1\x82 '
                '[testing]", abc_state:"granted">',
                '<TvmAppInfo #2000196 name:"TestABC2", abc_state:"deprived">',
                '<TvmAppInfo #2000201 name:"sandy-moodle-dev", abc_state:"granted">',
                '<TvmAppInfo #2000220 name:"TestABC3", abc_state:"deprived">',
                '<TvmAppInfo #2000230 name:"push-client-passport", abc_state:"granted">',
                '<TvmAppInfo #2000232 name:"Sentry", abc_state:"granted">',
                '<TvmAppInfo #2000347 name:"\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb5 '
                '\xd1\x82\xd0\xb2\xd0\xbc \xd0\xbf\xd1\x80\xd0\xb8\xd0\xbb\xd0\xbe\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 3", abc_state:"granted">',
                '<TvmAppInfo #2000348 name:"test_tvm25", abc_state:"granted">',
                '<TvmAppInfo #2000353 name:"TestClientToBeDeleted", abc_state:"deprived">',
                '<TvmAppInfo #2000354 name:"\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 '
                '\xd1\x81\xd0\xbe\xd0\xb7\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f TVM2", abc_state:"granted">',
                '<TvmAppInfo #2000355 name:"passport_likers3", abc_state:"granted">',
                '<TvmAppInfo #2000367 name:"social api (dev)", abc_state:"granted">',
                '<TvmAppInfo #2000368 name:"test-moodle", abc_state:"granted">',
                '<TvmAppInfo #2000371 name:"Test app", abc_state:"granted">',
            ]
        )

    def test_abc_get_all_persons(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_persons', TEST_ABC_GET_ALL_PERSONS_RESPONSE)
                fake_abc.set_response_value('get_all_roles', json.dumps(TEST_ABC_GET_ALL_ROLES_RESPONSE))
                fake_abc.set_response_value('get_all_departments', TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE)

                with LoggingMock() as logging_mock:
                    abc = get_abc(self.config)
                    r = abc.get_all_persons_and_scopes(
                        services=abc.get_all_departments(),
                    )
                    self.assertTupleEqual(
                        r,
                        (
                            {
                                1120000000000878: {'group_ids': set([(50, 5), (50, 8)]), 'roles_ids': set([(50, 8), (50, 16)]),
                                                    'login': u'vsavenkov'},
                                1120000000004890: {'group_ids': set([(50, 5)]), 'roles_ids': set([(50, 8)]), 'login': u'alex-sh'},
                                1120000000005594: {'group_ids': set([(14, 17)]), 'roles_ids': set([(14, 630)]), 'login': u'arhibot'},
                                1120000000027354: {'group_ids': set([(50, 8)]), 'roles_ids': set([(50, 16)]), 'login': u'bykanov'},
                                1120000000038274: {'group_ids': set([(14, 5)]), 'roles_ids': set([(14, 8)]), 'login': u'ppodolsky'},
                            },
                            {
                                1: AbcScope(id=1, unique_name="services_management"),
                                2: AbcScope(id=2, unique_name="projects_management"),
                                3: AbcScope(id=3, unique_name="analitics"),
                                4: AbcScope(id=4, unique_name="design"),
                                5: AbcScope(id=5, unique_name="development"),
                                6: AbcScope(id=6, unique_name="testing"),
                                7: AbcScope(id=7, unique_name="support"),
                                8: AbcScope(id=8, unique_name="administration"),
                                9: AbcScope(id=9, unique_name="content"),
                                10: AbcScope(id=10, unique_name="marketing"),
                                11: AbcScope(id=11, unique_name="sales_management"),
                                12: AbcScope(id=12, unique_name="quality_management"),
                                13: AbcScope(id=13, unique_name="other"),
                                14: AbcScope(id=14, unique_name="virtual"),
                                16: AbcScope(id=16, unique_name="dutywork"),
                                17: AbcScope(id=17, unique_name="tvm_management"),
                                50: AbcScope(id=50, unique_name="resources_responsible"),
                                51: AbcScope(id=51, unique_name="hardware_management"),
                                84: AbcScope(id=84, unique_name="devops"),
                                85: AbcScope(id=85, unique_name="cert"),
                                86: AbcScope(id=86, unique_name="db_management"),
                                87: AbcScope(id=87, unique_name="robots_management"),
                                90: AbcScope(id=90, unique_name="quotas_management"),
                            },
                            {
                                14: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 50, 51, 84, 85, 86, 87, 90]),
                                2: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                6: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                8: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                11: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                16: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                17: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                20: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                22: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                25: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                26: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                28: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                29: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                36: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                37: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                38: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                40: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                41: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                45: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                                50: set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 50, 51, 84, 85, 86, 87, 90]),
                            },
                            {
                                1: AbcRole(id=1, english_name="Head of product"),
                                2: AbcRole(id=2, english_name="Project manager"),
                                3: AbcRole(id=3, english_name="Content manager "),
                                4: AbcRole(id=4, english_name="Analyst"),
                                5: AbcRole(id=5, english_name="Marketing manager"),
                                6: AbcRole(id=6, english_name="Advertising manager"),
                                8: AbcRole(id=8, english_name="Developer"),
                                11: AbcRole(id=11, english_name="Frontend developer"),
                                13: AbcRole(id=13, english_name="Designer"),
                                14: AbcRole(id=14, english_name="Interface researcher"),
                                16: AbcRole(id=16, english_name="System administrator"),
                                17: AbcRole(id=17, english_name="Database administrator"),
                                19: AbcRole(id=19, english_name="Functional tester"),
                                21: AbcRole(id=21, english_name="Load tester"),
                                22: AbcRole(id=22, english_name="Technical writer"),
                                24: AbcRole(id=24, english_name="Support specialist"),
                                25: AbcRole(id=25, english_name="Consultant"),
                                26: AbcRole(id=26, english_name="Partner relationship manager"),
                                27: AbcRole(id=27, english_name="Sales manager"),
                                28: AbcRole(id=28, english_name="Undefined role"),
                                29: AbcRole(id=29, english_name="Administrator of assessors"),
                                30: AbcRole(id=30, english_name="Videographer"),
                                31: AbcRole(id=31, english_name="Cartographer"),
                                32: AbcRole(id=32, english_name="Leading cartographer"),
                                33: AbcRole(id=33, english_name="Senior cartographer"),
                                34: AbcRole(id=34, english_name="Content Project Manager"),
                                35: AbcRole(id=35, english_name="Product manager"),
                                36: AbcRole(id=36, english_name="Lawyer"),
                                37: AbcRole(id=37, english_name="Mobile interface developer"),
                                38: AbcRole(id=38, english_name="Server component developer"),
                                39: AbcRole(id=39, english_name="Security consultant"),
                                40: AbcRole(id=40, english_name="Editor"),
                                41: AbcRole(id=41, english_name="Speaker"),
                                42: AbcRole(id=42, english_name="Photographer"),
                                43: AbcRole(id=43, english_name="Author"),
                                44: AbcRole(id=44, english_name="DC infrastructure IT specialist"),
                                45: AbcRole(id=45, english_name="Autotest developer"),
                                46: AbcRole(id=46, english_name="Architect"),
                                47: AbcRole(id=47, english_name="Moderator"),
                                48: AbcRole(id=48, english_name="Secretary"),
                                49: AbcRole(id=49, english_name="Category manager"),
                                50: AbcRole(id=50, english_name="Quality manager"),
                                51: AbcRole(id=51, english_name="Service manager"),
                                52: AbcRole(id=52, english_name="Deputy head of product"),
                                53: AbcRole(id=53, english_name="Office infrastructure IT specialist"),
                                161: AbcRole(id=161, english_name="HR-partner"),
                                181: AbcRole(id=181, english_name="Approver"),
                                383: AbcRole(id=383, english_name="Robot"),
                                413: AbcRole(id=413, english_name="Duty"),
                                556: AbcRole(id=556, english_name="Virtual user (passp)"),
                                630: AbcRole(id=630, english_name="TVM manager"),
                                700: AbcRole(id=700, english_name="L3 responsible"),
                                742: AbcRole(id=742, english_name="Hardware resources manager"),
                                830: AbcRole(id=830, english_name="Responsible"),
                                960: AbcRole(id=960, english_name="Certificates responsibe"),
                                967: AbcRole(id=967, english_name="Xiva manager"),
                                1097: AbcRole(id=1097, english_name="DevOps"),
                                1258: AbcRole(id=1258, english_name="MDB admin"),
                                1259: AbcRole(id=1259, english_name="MDB viewer"),
                                1260: AbcRole(id=1260, english_name="Robots manager"),
                                1261: AbcRole(id=1261, english_name="Robots user"),
                                1369: AbcRole(id=1369, english_name="Maintenance manager"),
                                1553: AbcRole(id=1553, english_name="Quotas manager"),
                                1563: AbcRole(id=1563, english_name="MDB admin with inheritance"),
                                1586: AbcRole(id=1586, english_name="QYP User"),
                                1735: AbcRole(id=1735, english_name="Duty Manager"),
                                1796: AbcRole(id=1796, english_name="Capacity Planning Manager"),
                            },
                            {
                                2: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                        51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                        1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                6: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                        51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                        1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                8: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                        51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                        1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                11: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                14: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 556, 630, 700, 742, 830, 960, 967, 1097, 1258,
                                         1259, 1260, 1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                16: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                17: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                20: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                22: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                25: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                26: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                28: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                29: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                36: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                37: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                38: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                40: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                41: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                45: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796]),
                                50: set([1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30,
                                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                                         51, 52, 53, 161, 181, 383, 413, 700, 742, 830, 960, 967, 1097, 1258, 1259, 1260,
                                         1261, 1369, 1553, 1563, 1586, 1735, 1796])
                            },
                        ),
                    )
                    self.assertListEqual(
                        logging_mock.getLogger('info_logger').entries,
                        [
                            (u"ABC: get_all_persons_and_scopes fetched an unknown members scope. Service id 14. Scope: "
                             u"{'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                             u"'en': u'TVM management'}, 'slug': u'tvm_management'}",
                             'WARNING',
                             None,
                             None),
                            (u"ABC: get_all_persons_and_scopes fetched an unknown members role. Service id 14. Role: "
                             u"{'scope': {'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                             u"'en': u'TVM management'}, 'slug': u'tvm_management'}, 'code': u'tvm_manager', 'id': 630, 'service': None, "
                             u"'name': {'ru': u'TVM \\u043c\\u0435\\u043d\\u0435\\u0434\\u0436\\u0435\\u0440', 'en': u'TVM manager'}}",
                             'WARNING',
                             None,
                             None)
                        ],
                    )

    def test_abc_get_all_departments(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_departments', TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE)
                r = get_abc(self.config).get_all_departments()
                self.assertDictEqual(r, {2: {
                    'name': u'\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 (\u041c\u043e\u0440\u0434\u0430)',
                    'slug': 'home'}, 36: {'name': 'Zora', 'slug': 'fetcher'}, 37: {
                    'name': u'\u041d\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u043e\u043d\u043d\u044b\u0439 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a',
                    'slug': 'specprojects'}, 6: {
                    'name': u'\u041c\u043e\u0431\u0438\u043b\u044c\u043d\u0430\u044f \u041c\u043e\u0440\u0434\u0430',
                    'slug': 'mobile'}, 8: {
                    'name': u'\u041e\u043f\u0440\u0435\u0434\u0435\u043b\u044f\u043b\u043a\u0430 \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0445 '
                            u'\u0442\u0435\u043b\u0435\u0444\u043e\u043d\u043e\u0432',
                    'slug': 'phonedetect'}, 41: {'name': 'YASM', 'slug': 'golovan'}, 11: {
                    'name': u'\u041f\u0440\u043e\u043c\u043e-\u0441\u0430\u0439\u0442 mobile.yandex.ru',
                    'slug': 'mobileyandex'}, 45: {
                    'name': u'\u0412\u044b\u0434\u0430\u0447\u0430 \u043f\u043e\u0438\u0441\u043a\u0430 (SERP)',
                    'slug': 'serp'}, 14: {'name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442', 'slug': 'passp'},
                    16: {'name': u'LBS', 'slug': 'lbs'},
                    17: {'name': u'\u0422\u0430\u043d\u043a\u0435\u0440', 'slug': 'tanker'}, 50: {
                    'name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                    'slug': 'suggest'}, 20: {
                    'name': u'\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u043f\u043e\u0440\u0442\u0430\u043b\u0443 (stat.yandex.ru)',
                    'slug': 'stat'}, 22: {
                    'name': u'\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u043e\u0440\u0442\u0430\u043b\u0430',
                    'slug': 'custom'}, 40: {'name': u'SRE \u043f\u043e\u0438\u0441\u043a\u0430', 'slug': 'sepe'},
                    25: {'name': u'\u041a\u0430\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0438\u0441\u043a\u0430', 'slug': 'search-quality'}, 26: {
                    'name': u'\u0412\u0435\u0431-\u0440\u0430\u043d\u0436\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435',
                    'slug': 'buki'}, 38: {'name': u'\u0421\u0432\u0435\u0436\u0435\u0441\u0442\u044c', 'slug': 'rearr'}, 28: {
                    'name': u'\u0412\u0435\u0431-\u0441\u043d\u0438\u043f\u043f\u0435\u0442\u044b',
                    'slug': 'snippets'}, 29: {
                    'name': u'\u041f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 \u0434\u043b\u044f '
                            u'\u043f\u043e\u0438\u0441\u043a\u0430',
                    'slug': 'searchcontent'}})

    def test_fail_abc_builder(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_side_effect('get_all_persons', BaseABCError)
                self.assertRaises(ABCError, lambda: get_abc(self.config).get_all_persons_and_scopes())

    def test_download_abc(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_persons', json.dumps(TEST_ABC_GET_ALL_PERSONS_RESPONSE))
                fake_abc.set_response_value('get_all_roles', json.dumps(TEST_ABC_GET_ALL_ROLES_RESPONSE))
                fake_abc.set_response_value('get_all_departments', json.dumps(TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE))
                (
                    abc_persons, abc_scopes, abc_services_scopes,
                    abc_roles, abc_services_roles,
                ) = get_abc(self.config).get_all_persons_and_scopes()
                abc_departments = get_abc(self.config).get_all_departments()
                ExternalRecord.insert_abc(
                    abc_persons, abc_scopes, abc_services_scopes, abc_departments,
                    abc_roles, abc_services_roles,
                )
                self.assert_external_filled_with_abc()
                self.assert_departments_filled_with_abc()
                self.assert_scopes_filled_with_abc()
                self.assert_roles_filled_with_abc()

                fake_abc.set_response_side_effect('get_all_persons', BaseABCError)
                fake_abc.set_response_side_effect('get_all_departments', BaseABCError)
                with self.assertRaises(ABCError):
                    (
                        abc_persons, abc_scopes, abc_services_scopes,
                        abc_roles, abc_services_roles,
                    ) = get_abc(self.config).get_all_persons_and_scopes()
                    abc_departments = get_abc(self.config).get_all_departments()
                    ExternalRecord.insert_abc(
                        abc_persons, abc_scopes, abc_services_scopes, abc_departments,
                        abc_roles, abc_services_roles,
                    )
                self.assert_external_filled_with_abc()
                self.assert_departments_filled_with_abc()
                self.assert_scopes_filled_with_abc()
                self.assert_roles_filled_with_abc()

    def test_abc_records_removal_and_restore(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_persons', json.dumps(TEST_ABC_GET_ALL_PERSONS_RESPONSE))
                fake_abc.set_response_value('get_all_roles', json.dumps(TEST_ABC_GET_ALL_ROLES_RESPONSE))
                fake_abc.set_response_value('get_all_departments', json.dumps(TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE))
                (
                    abc_persons, abc_scopes, abc_services_scopes,
                    abc_roles, abc_services_roles,
                ) = get_abc(self.config).get_all_persons_and_scopes()
                abc_departments = get_abc(self.config).get_all_departments()
                ExternalRecord.insert_abc(
                    abc_persons, abc_scopes, abc_services_scopes, abc_departments,
                    abc_roles, abc_services_roles,
                )
                self.assert_external_filled_with_abc()
                self.assert_departments_filled_with_abc()
                self.assert_scopes_filled_with_abc()
                self.assert_roles_filled_with_abc()

                fake_abc.set_response_value('get_all_persons', json.dumps(TEST_ABC_EMPTY_RESPONSE))
                fake_abc.set_response_value('get_all_roles', TEST_ABC_EMPTY_RESPONSE)
                fake_abc.set_response_value('get_all_departments', json.dumps(TEST_ABC_EMPTY_RESPONSE))
                (
                    abc_persons, abc_scopes, abc_services_scopes,
                    abc_roles, abc_services_roles,
                ) = get_abc(self.config).get_all_persons_and_scopes()
                abc_departments = get_abc(self.config).get_all_departments()
                ExternalRecord.insert_abc(
                    abc_persons, abc_scopes, abc_services_scopes, abc_departments,
                    abc_roles, abc_services_roles,
                )
                self.assert_external_records_is_empty()
                self.assert_departments_filled_with_abc(state=1)
                self.assert_scopes_filled_with_abc()
                self.assert_roles_filled_with_abc()

                fake_abc.set_response_value('get_all_persons', json.dumps(TEST_ABC_GET_ALL_PERSONS_RESPONSE))
                fake_abc.set_response_value('get_all_roles', json.dumps(TEST_ABC_GET_ALL_ROLES_RESPONSE))
                fake_abc.set_response_value('get_all_departments', json.dumps(TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE))
                (
                    abc_persons, abc_scopes, abc_services_scopes,
                    abc_roles, abc_services_roles,
                ) = get_abc(self.config).get_all_persons_and_scopes()
                abc_departments = get_abc(self.config).get_all_departments()
                ExternalRecord.insert_abc(
                    abc_persons, abc_scopes, abc_services_scopes, abc_departments,
                    abc_roles, abc_services_roles,
                )
                self.assert_external_filled_with_abc()
                self.assert_departments_filled_with_abc()
                self.assert_scopes_filled_with_abc()
                self.assert_roles_filled_with_abc()

    def test_abc_get_all_tvm_apps(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_tvm_apps', TEST_ABC_GET_ALL_TVM_APPS_RESPONSE)
                r = get_abc(self.config).get_all_tvm_apps()
                self.assertDictEqual(
                    r,
                    {u'2000079': {'abc_id': 14,
                                  'abc_resource_id': 2164691,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442 [testing]',
                                  'tvm_client_id': u'2000079',
                                  'url': None},
                     u'2000196': {'abc_id': 14,
                                  'abc_resource_id': 2164692,
                                  'abc_state': u'deprived',
                                  'abc_state_display_name': u'\u041e\u0442\u043e\u0437\u0432\u0430\u043d',
                                  'name': u'TestABC2',
                                  'tvm_client_id': u'2000196',
                                  'url': None},
                     u'2000201': {'abc_id': 1931,
                                  'abc_resource_id': 2216502,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'sandy-moodle-dev',
                                  'tvm_client_id': u'2000201',
                                  'url': None},
                     u'2000220': {'abc_id': 14,
                                  'abc_resource_id': 2204567,
                                  'abc_state': u'deprived',
                                  'abc_state_display_name': u'\u041e\u0442\u043e\u0437\u0432\u0430\u043d',
                                  'name': u'TestABC3',
                                  'tvm_client_id': u'2000220',
                                  'url': None},
                     u'2000230': {'abc_id': 14,
                                  'abc_resource_id': 2205411,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'push-client-passport',
                                  'tvm_client_id': u'2000230',
                                  'url': None},
                     u'2000232': {'abc_id': 795,
                                  'abc_resource_id': 2205693,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'Sentry',
                                  'tvm_client_id': u'2000232',
                                  'url': None},
                     u'2000347': {'abc_id': 14,
                                  'abc_resource_id': 2214066,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0435 \u0442\u0432\u043c \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 3',
                                  'tvm_client_id': u'2000347',
                                  'url': None},
                     u'2000348': {'abc_id': 1902,
                                  'abc_resource_id': 2214070,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'test_tvm25',
                                  'tvm_client_id': u'2000348',
                                  'url': None},
                     u'2000353': {'abc_id': 14,
                                  'abc_resource_id': 2214454,
                                  'abc_state': u'deprived',
                                  'abc_state_display_name': u'\u041e\u0442\u043e\u0437\u0432\u0430\u043d',
                                  'name': u'TestClientToBeDeleted',
                                  'tvm_client_id': u'2000353',
                                  'url': None},
                     u'2000354': {'abc_id': 14,
                                  'abc_resource_id': 2214468,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f TVM2',
                                  'tvm_client_id': u'2000354',
                                  'url': None},
                     u'2000355': {'abc_id': 14,
                                  'abc_resource_id': 2214524,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'passport_likers3',
                                  'tvm_client_id': u'2000355',
                                  'url': None},
                     u'2000367': {'abc_id': 14,
                                  'abc_resource_id': 2216446,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'social api (dev)',
                                  'tvm_client_id': u'2000367',
                                  'url': None},
                     u'2000368': {'abc_id': 1931,
                                  'abc_resource_id': 2216480,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'test-moodle',
                                  'tvm_client_id': u'2000368',
                                  'url': None},
                     u'2000371': {'abc_id': 848,
                                  'abc_resource_id': 2216892,
                                  'abc_state': u'granted',
                                  'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                  'name': u'Test app',
                                  'tvm_client_id': u'2000371',
                                  'url': None},
                     },
                )

    def test_downloadd_tvm_apps(self):
        with self.app.app_context():
            with FakeABC() as fake_abc:
                fake_abc.set_response_value('get_all_tvm_apps', TEST_ABC_GET_ALL_TVM_APPS_RESPONSE)
                tvm_apps = get_abc(self.config).get_all_tvm_apps()
                TvmAppInfo.insert_tvm_apps(tvm_apps)
                self.assert_tvm_apps_filled_with_abc()

    def test_staff_get_all_persons(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_persons', json.dumps(TEST_STAFF_GET_ALL_PERSONS_RESPONSE))
                r = get_staff(self.config).get_all_persons()
                self.assertDictEqual(r, {
                    100: {
                        'group_ids': [2, 1],
                        'keys': [],
                        'login': 'vault-test-100',
                        'first_name': u'Vault',
                        'last_name': u'Test100',
                        'staff_id': 2,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    101: {
                        'group_ids': [2, 1],
                        'keys': [],
                        'login': 'vault-test-101',
                        'first_name': u'Vault',
                        'last_name': u'Test101',
                        'staff_id': 2,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    102: {
                        'group_ids': [2, 1],
                        'keys': [],
                        'login': 'vault-test-102',
                        'first_name': u'Vault',
                        'last_name': u'Test102',
                        'staff_id': 2,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    1120000000035620: {
                        'group_ids': [4045, 1, 4112, 3224, 3101, 62, 533],
                        'keys': [],
                        'login': u'mesyarik',
                        'first_name': u'Илья',
                        'last_name': u'Мещерин',
                        'staff_id': 4045,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    1120000000036175: {
                        'group_ids': [422, 1, 4112, 3224, 3101, 62, 533],
                        'keys': [
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5WbIQ1CsAfdB1SBlJjC5WYZqkByu4b/CZ5+0EjA7EUdEbd/8Hd'
                            u'8aUXq1no7k24TbsNnSrJ6i+tjDELTv0rstKaqvYKNgG+ZftLGE39N8ga62gyhL2euEjyoIFULKKo+17YrlW4SgNqQ'
                            u'+q3Bwc9Vmwbd+kVDe0J5rgr1JWHxvKEE5rG0p/NI1hitzxTMez75xikB3rw38vr4i/bYSMIlFLX54xAagBQCOWLuc'
                            u'XJ+2R0J2OJW6F5AhpGT2Rtd6almzROib8yYiTYITgW8qEYYN2U3igkRlNxXqck1S05d/1Iu8rjnRjdlQnkWgxKxC6'
                            u'Rrd3zqywuogqq7aJWe/EiKYF ankineri@ankineri-ub14',
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCayrrgZs9rLwhLwoDtmTTr8mmy9d4h5dh8XpPtpGVfBY8MM+jOI'
                            u'DceJDqBQwinBYelm8eIBbXsCFDD3kevW0Qw6xGFnlAwoYe45HGIKeyHcPx6RUmrvBxXFIluMpdM5DV/vz0qy1TIpi'
                            u'uu/HzVAKneKz1+XPB/jchZxHTAA6BFB5WLEmIQDI2cqRY7OdwbpRoOordYSLyxN4zoHAmqJcQNvhWrXGkFd6dmt4L'
                            u'r2eI6pSSoGh0CpDJNFRl5UJyf8zF0b3Ji6ZaNDgG70WR75qWIhJY6d/u+DTkLPWOIfxauY7UMro9GM973fJmUZq/j'
                            u'qcjRX6+eUFVyFTXNxaNMxjNr ankineri@factordev.search.yandex.net',
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqeg+b53lU/ZQFgGx2I3dNuH7NtAfhBOZ7e8mtOkWbTY/dPrXIL'
                            u'QkQlaBL+FgbXSnnopL2BZu0W6bk7TkFjFsll9AZsKCcGgyucePp/5qpULNHzNf3iqtvLi2xlCwdcDKNXxQniP8AMZ'
                            u'mFlV7JPSrVpl2iJNhPTp5g0a9RRmKltBndbxmZ7ie3tDX+0KNPgu6RZURs9xCZSHrJN+ubXyl6Ncn/mkBKZBPufhP'
                            u'B4DhorVgYVFrti01UFJrQMYy6cyMsTXoL/GmFMaXt2ySd3U/m6mjYieEIxEQeKswaMhB0uIsclX6raJg6XuJbtxd8'
                            u'EeS66HttHw5xIVYZ7IAhEtPj ankineri@factordev2.search.yandex.net',
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDg4+GoCypqseVKHW0ZdkMAn5QIRvynteMv+p0kN96MqRYR53VjS'
                            u'OQ6V/OlZ0RNUia1OTqXFN+/rFpJQPt3N7ZhGa2GWUpE2pzGhgUGxtrs57J+gFGSYdnmXbilH6C88g/GTFa+/oIKXB'
                            u'ppUKVHJRFFvH42fKPMgKCBDoksYcmoyNJ6xdybUYyKo9pW5QYuB5qCGGwa2j964ONPqQM8wGrpYk9tZXBF0bXn8KO'
                            u'uRmQnYsdb1RBcanHV52W2cCP3kYWkVGZ1pS9rZs0ShIla2zZzW+e+f8WkWyRx+1OZCr3g4VwK+tfqS5WD3LcWQaDz'
                            u'6d9vXCukoJzuC2iaf1s1m5KqS9iIrjUIjG57Onx26gLzD3p+PfmnIs2rfULnO+/aaXiIN5r4xSSc8rRV4kKo9APcl'
                            u'fME70iIU7KeELoO3vd6HQdxBfE1gJGneTJLM6dH1dAlG3xoFWzcBtxgxu/gxe7s7AwBwpIEVpC4F4H84pdH5l4BZR'
                            u'yaDIC1LxULrxj25OTFNlhhnXy6S2Fm4AmghYmDVi+XqxUPpJZcLuze+GtNCnCyO7H7XXiim0hwVOmG+VxXs8f9X4q'
                            u'cAHn7IV1Ux1visC7SSC5WCGantagGL3WCcvjfKTrgNqwqh1UAmmbCsaRPLJM4k4IEGRwzFquMdon2OfYA3eQBH+v5'
                            u'0zJtSi8LRQ== ankineri@lenstra.search.yandex.net',
                        ],
                        'login': u'ankineri',
                        'first_name': u'Андрей',
                        'last_name': u'Молчанов',
                        'staff_id': 422,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    1120000000038274: {
                        'group_ids': [2864, 1, 4112, 5698, 1538, 3051],
                        'keys': [
                            'strange-key ororo ppodolsky@213.180.218.205-red.dhcp.yndx.net',
                            'ecdsa-sha2-nistp384 AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbm'
                            'lzdHAzODQAAABhBMNu9svIGzrY4FInPdoLhe60WfKBMmfMZkllIEiFrTyu'
                            'uNKUnX0gM77yNQJaqBLxdPzhkmW+eiCp7uvmHRwmH/UTXSkFp9espCnIee'
                            'Cd0WTn55NSZrPccv8cGr/WflBrwg== ppodolsky@213.180.218.205-red.dhcp.yndx.net',
                            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7EPwGIBqO4FUBoeQRcJLK/0dSMMjEik+pKIGV9eyUfm+5QhkAz8'
                            'X2H86AzM+/l9YmjyRnSDgq2umfVWfo/Kj61fvFwiO32MMuAAhU3mzwBH/d+7xVRJTkkeDvsXluuMIBkZUsIJKecuhA'
                            'FoHlDL6aG0fMZaeORKVajt7UIh9Jqudvafceay7hMh3HsyZmKkh0oNHojqAwDNHPDfGZ/Rw78fyy/W5p0NLcMeOYzm'
                            '8LdRRkSRUUJX23ujh2TbwWpa9AKO9oz/OpDcuDl/+QmvRbq7HFZCDGUdQuSogd2xDWV73cWBw8h2ZDo+Dm1qGmVpv8'
                            'Zimh8GhNqNPEVtlw2SOL ppodolsky@yandex-team.ru',
                        ],
                        'login': u'ppodolsky',
                        'first_name': u'Паша',
                        'last_name': u'Переведенцев',
                        'staff_id': 2864,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    1120000000039954: {
                        'group_ids': [3491, 1, 4112, 3224, 3101, 62, 533],
                        'keys': [
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwlsvK/ujXg1YcMSxjQZSEltZPzKqbgZimQc7S63GxWRa2bTApA'
                            u'9/jji6CYw89XvbRY8j/2qF4Oay49zJ9h3E9WUOEe4jA0JoUoA5Jjxd05RynSDTK+gFCEw87xG32H8sdYC/vF1t2+3'
                            u'RcWGwGs8VSkHmMddDb0LvCa83/XZYjSPwSlFpkZ8eVPYZLUUlZowdGQrdQpvA2CvSS65PYbhcK/fPdb72Ll6AwEhZ'
                            u'Oyw8Nfc/foEZ6bOdnSCGDHWpkDNWql67h18kSsWPPYNiJwESMfSlPBTRc8XuJ1L6Vwt0+wnJ7UaFfuhyHn+GvFspH'
                            u'OOkeDvxmqMc8b7AEaa12d4yB crossby@yandex-team.ru',
                        ],
                        'login': u'crossby',
                        'first_name': u'Валерий',
                        'last_name': u'Дужик',
                        'staff_id': 3491,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                    1120000000040289: {
                        'group_ids': [3132, 1, 4112, 3224, 3101, 62, 533],
                        'keys': [
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCx8Yc4+4RzhnUixVwixWlWvr0JuBgwJsPPiop4xF8MsgOu2FrOa'
                            u'5xksLd+xdzCqP+noJ87VEeIQxZY7uGar7wBf/wJ2QrjzA8iJZkFVa1XOxE3yvPxOpRVIN6HQPRbf3fbZzuCCGmAEO'
                            u'j1fGYe5xu8T3tXcoe0KTtn5KNuS2rhz9tfWfEJKnlFH0tShZBsrWBlib1GRGTjymot4SPpvCs7bYs32fiS2j8IjQ5'
                            u'b3O6tLbz+fPh7gwRViLNOjixNRYRDHCf2KrTlz7lv/CoGwn17FADugLHRyDUliLlhcRrc1q/rR1nNfGR10ZNVWt60'
                            u'hBd0hCvxGknIEHR3+4o5CCcB agniash@yandex-team.ru',
                            u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC30WOYKUzi09C8tRRt5HPcFBpGe8qhunSqKAio3b6SKdFrxopS3'
                            u'xc4UbCOzQkaStcTPVLTAUXxMgC+B1ORru5A5NCbyG7rNUkVnamZOeLFkpiMD9gnMzDp6sAsI5WHLARkoZCYIErZwf'
                            u'O+ZH7mqHU9hB2gpwKiwk8+CMxvVdZDmK31fmCpBZVwIhu3vKKKYTXiLnc4t4MqkgI+vyszAHhqZF4xvn1WfdHYB+N'
                            u'mF1HOZNXGQiGd0oFe0ZIkba1uz/79uvVQxfU2fLbxE3f/adfLAOIfuiYg6/aeBaHJ2i5L6qKuA92uC0QtWT1oM82S'
                            u'RZratUWtrD5ODOR2hkMatcFX agniash@yandex-team.ru',
                        ],
                        'login': u'agniash',
                        'first_name': u'Павел',
                        'last_name': u'Агниашвили',
                        'staff_id': 3132,
                        'is_dismissed': False,
                        'is_deleted': False,
                        '_disabled': False,
                    },
                })

    def test_staff_get_all_departments(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_departments',
                                              json.dumps(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE))
                r = get_staff(self.config).get_all_departments()
                self.assertDictEqual(r, {
                    2: {
                        "is_deleted": False,
                        "name": u"Тестовая группа Секретницы 1",
                        "url": "_vault_test_group_1",
                    },
                    4112: {
                        "is_deleted": False,
                        "name": u"Тестовая группа Секретницы 2",
                        "url": "_vault_test_group_2",
                    },
                    42112: {
                        'is_deleted': False,
                        'url': u'yandex_rkub_taxi_support_supvod',
                        'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043f\u043e\u0434\u0434'
                                u'\u0435\u0440\u0436\u043a\u0438 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u043e\u0432'
                    },
                    74710: {
                        'is_deleted': False,
                        'url': u'yandex_rkub_taxi_dev_5902',
                        'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u0440\u0435\u0433\u0438\u043e\u043d'
                                u'\u0430\u043b\u044c\u043d\u044b\u0445 \u0446\u0435\u043d\u0442\u0440\u043e\u0432 '
                                u'\u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 \u0441 \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044f\u043c\u0438'
                    },
                    93447: {
                        'is_deleted': False,
                        'url': u'yandex_edu_personel_5537_dep80665',
                        'name': u'\u042f\u043d\u0434\u0435\u043a\u0441.\u041d\u0430\u0432\u044b\u043a\u0438'
                    },
                    93448: {
                        'is_deleted': False,
                        'url': u'yandex_edu_personel_5537_dep03987',
                        'name': u'\u042f\u043d\u0434\u0435\u043a\u0441.\u0428\u043a\u043e\u043b\u0430'
                    },
                    29453: {
                        'is_deleted': False,
                        'url': u'yandex_design_search_vertical',
                        'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0434\u0438\u0437\u0430\u0439\u043d\u0430 '
                                u'\u0432\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0445 '
                                u'\u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 \u043f\u043e\u0438\u0441\u043a\u0430'
                    },
                    84878: {
                        'is_deleted': False,
                        'url': u'outstaff_2289_8265_5357',
                        'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043b\u043e\u0433\u0438\u0441\u0442\u0438'
                                u'\u043a\u0438 \u042f\u043d\u0434\u0435\u043a\u0441.\u0415\u0434\u044b (Outstaff)'
                    },
                    67600: {
                        'is_deleted': False,
                        'url': u'as_opdir_8255',
                        'name': u'\u041f\u043e\u0434\u0433\u0440\u0443\u043f\u043f\u0430 \u043e\u043f\u0435\u0440'
                                u'\u0430\u0442\u043e\u0440\u043e\u0432 \u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u0430 5 (Outstaff)'
                    },
                    83734: {'url': u'yandex_rkub_taxi_dev_3231',
                            'is_deleted': False,
                            'name': u'\u041e\u0442\u0434\u0435\u043b \u0430\u043a\u0442\u0438\u0432\u0430\u0446\u0438'
                                    u'\u0438 \u0438 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u044f \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u0435\u0439'},
                    89623: {'url': u'ext_6887',
                            'is_deleted': False,
                            'name': u'\u0412\u043d\u0435\u0448\u043d\u0438\u0435 \u043a\u043e\u043d\u0441\u0443\u043b'
                                    u'\u044c\u0442\u0430\u043d\u0442\u044b \u042f\u043d\u0434\u0435\u043a\u0441.\u0415\u0434\u044b'},
                    24: {'url': u'yandex_mnt_infra',
                         'is_deleted': False,
                         'name': u'\u0418\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u043d'
                                 u'\u044b\u0439 \u043e\u0442\u0434\u0435\u043b'},
                    86477: {'url': u'yandex_rkub_taxi_5151_8501_9053',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043c\u0430\u0440\u043a\u0435\u0442\u0438'
                                    u'\u043d\u0433\u0430 \u042f\u043d\u0434\u0435\u043a\u0441.\u0415\u0434\u044b'},
                    92015: {'url': u'yandex_rkub_taxi_support_6923_5271',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043a\u043e\u043d\u0442\u0435\u043d\u0442'
                                    u'\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439'},
                    80036: {'url': u'yandex_search_tech_sq_3452',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u0433\u0435\u043e\u043f\u043e\u0438\u0441\u043a\u0430 '
                                    u'\u0438 \u0441\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u0430'},
                    82601: {'url': u'yandex_search_tech_sq_interfaceandtools',
                            'is_deleted': False,
                            'name': u'\u041f\u043e\u0438\u0441\u043a\u043e\u0432\u044b\u0435 \u0438\u043d\u0442\u0435'
                                    u'\u0440\u0444\u0435\u0439\u0441\u044b \u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u044b '
                                    u'\u0434\u043b\u044f \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0439'},
                    45: {'url': u'yandex_mnt_infra_itoffice',
                         'is_deleted': False,
                         'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 IT \u0438\u043d\u0444\u0440\u0430\u0441\u0442'
                                 u'\u0440\u0443\u043a\u0442\u0443\u0440\u044b \u043e\u0444\u0438\u0441\u043e\u0432'},
                    87859: {'url': u'virtual_robots_3137', 'name': u'Mssngr',
                            'is_deleted': False},
                    82741: {'url': u'yandex_rkub_taxi_support_supvod_3678',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438 '
                                    u'\u043f\u0430\u0440\u0442\u043d\u0435\u0440\u043e\u0432 \u043f\u043e '
                                    u'\u0432\u043e\u043f\u0440\u043e\u0441\u0430\u043c'
                                    u' \u043f\u0440\u0430\u0432\u043e\u0441\u0443\u0434\u0438\u044f '
                                    u'\u0438 \u0441\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043e\u0432 '
                                    u'\u0441\u0435\u0440\u0432\u0438\u0441\u0430'},
                    84278: {'url': u'yandex_rkub_taxi_dev_5902_7922',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 '
                                    u'\u043c\u0435\u0436\u0434\u0443\u043d\u0430\u0440\u043e\u0434\u043d\u043e\u0433\u043e '
                                    u'\u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044f \u0446\u0435\u043d\u0442\u0440\u043e\u0432'},
                    82743: {'url': u'yandex_rkub_taxi_support_supvod_7398',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438 '
                                    u'\u0444\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0445 '
                                    u'\u043e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u0439 '
                                    u'\u043f\u0430\u0440\u0442\u043d\u0435\u0440\u043e\u0432'},
                    84280: {'url': u'yandex_rkub_taxi_dev_3231_1747',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e '
                                    u'\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u044f\u043c \u0441 '
                                    u'\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044f\u043c\u0438'},
                    84281: {'url': u'yandex_rkub_taxi_dev_3231_6117',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 '
                                    u'\u0441\u0442\u0440\u0430\u0442\u0435\u0433\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e'
                                    u' \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044f \u0438 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438'},
                    64: {'url': u'yandex_search_tech_quality',
                         'is_deleted': False,
                         'name': u'\u041e\u0442\u0434\u0435\u043b \u0440\u0430\u043d\u0436\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f'},
                    87495: {'url': u'outstaff_2289_9459_8766_9989',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043c\u0435\u0436\u0434\u0443'
                                    u'\u043d\u0430\u0440\u043e\u0434\u043d\u043e\u0439 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438 '
                                    u'\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 (Outstaff)'},
                    83658: {'url': u'yandex_edu_personel_5537',
                            'is_deleted': False,
                            'name': u'\u042f\u043d\u0434\u0435\u043a\u0441.\u041e\u0431\u0440\u0430\u0437'
                                    u'\u043e\u0432\u0430\u043d\u0438\u0435'},
                    83659: {'url': u'yandex_edu_personel_5537_0405',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u0440\u0430\u0437\u0440\u0430'
                                    u'\u0431\u043e\u0442\u043a\u0438 online \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b'},
                    82381: {'url': u'yandex_distproducts_browserdev_mobile_taxi_9720_2944_9770',
                            'is_deleted': False,
                            'name': u'\u041f\u043e\u0434\u0433\u0440\u0443\u043f\u043f\u0430 \u0440\u0430'
                                    u'\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 '
                                    u'\u044d\u0444\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b 3'},
                    59086: {'url': u'yandex_rkub_discovery_rec_rank',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043a\u0430\u0447\u0435\u0441'
                                    u'\u0442\u0432\u0430 \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0439 '
                                    u'\u0438 \u0430\u043d\u0430\u043b\u0438\u0437\u0430 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430'},
                    84687: {'url': u'yandex_biz_com_8856',
                            'is_deleted': False,
                            'name': u'\u041f\u043e\u0434\u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d'
                                    u'\u0438\u0435 \u043f\u043e \u0432\u0437\u0430\u0438\u043c\u043e\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044e '
                                    u'\u0441 \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430\u043c\u0438 \u0420\u0421\u042f'},
                    38096: {'url': u'yandex_search_tech_sq',
                            'is_deleted': False,
                            'name': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430 '
                                    u'\u043f\u043e\u0438\u0441\u043a\u043e\u0432\u044b\u0445 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u0432'},
                    38098: {'url': u'yandex_search_tech_sq_analysis',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u0430\u043d\u0430\u043b'
                                    u'\u0438\u0442\u0438\u043a\u0438 \u0438 '
                                    u'\u043a\u043e\u043d\u0432\u0435\u0439\u0435\u0440\u0438\u0437\u0430\u0446\u0438\u0438'},
                    84819: {'url': u'yandex_rkub_taxi_5151_8501_8241',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043c\u0430\u0440\u043a'
                                    u'\u0435\u0442\u0438\u043d\u0433\u043e\u0432\u044b\u0445 '
                                    u'\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0439 \u042f\u043d\u0434\u0435\u043a\u0441.\u0415\u0434\u044b'},
                    32470: {'url': u'yandex_search_tech_ont',
                            'is_deleted': False,
                            'name': u'\u041e\u0442\u0434\u0435\u043b Web \u043e\u043d\u0442\u043e\u043b\u043e\u0433\u0438\u0438'},
                    90711: {'url': u'outstaff_2289_8265_6121_1328',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 \u0441'
                                    u' \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f\u043c\u0438 (Outstaff)'},
                    93278: {'url': u'yandex_rkub_discovery_rec_tech_5431_9475',
                            'is_deleted': False,
                            'name': u'\u041f\u043e\u0434\u0433\u0440\u0443\u043f\u043f\u0430 '
                                    u'\u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u043e\u0432 '
                                    u'\u043f\u0430\u0431\u043b\u0438\u0448\u0438\u043d\u0433\u043e\u0432\u043e\u0439 '
                                    u'\u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b \u0414\u0437\u0435\u043d\u0430'},
                    73680: {'url': u'yandex_distproducts_morda_commercial_prod_7642',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432 '
                                    u'\u0441\u0447\u0430\u0441\u0442\u044c\u044f \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044f'},
                    44003: {'url': u'yandex_rkub_taxi_cust',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 '
                                    u'\u0441 \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044f\u043c\u0438'
                                    u' \u042f\u043d\u0434\u0435\u043a\u0441.\u0422\u0430\u043a\u0441\u0438'},
                    93796: {'url': u'yandex_mrkt_mediamrkt_media_taxi_6258_0126',
                            'is_deleted': False,
                            'name': u'\u041f\u043e\u0434\u0433\u0440\u0443\u043f\u043f\u0430 \u0437\u0430\u043a\u0443\u043f\u043a\u0438'
                                    u' \u043d\u0430\u0440\u0443\u0436\u043d\u043e\u0439 \u0440\u0435\u043a\u043b\u0430\u043c\u044b '
                                    u'\u0438 \u0431\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f '},
                    88933: {'url': u'yandex_rkub_taxi_support_1683',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438 \u0432 '
                                    u'\u0412\u043e\u0440\u043e\u043d\u0435\u0436\u0435'},
                    24936: {'url': u'yandex_search_tech_quality_func',
                            'is_deleted': False,
                            'name': u'\u041e\u0442\u0434\u0435\u043b '
                                    u'\u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 '
                                    u'\u043f\u043e\u0438\u0441\u043a\u0430'},
                    92011: {'url': u'yandex_proffice_support_comm_taxi_2913',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u0438\u0441\u044c\u043c\u0435\u043d\u043d\u043e\u0439 '
                                    u'\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438'
                                    u' \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 Uber'},
                    236: {'url': u'yandex_search_tech_spam',
                          'is_deleted': False,
                          'name': u'\u041e\u0442\u0434\u0435\u043b \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0433\u043e '
                                    u'\u043f\u043e\u0438\u0441\u043a\u0430'},
                    92013: {'url': u'yandex_rkub_taxi_support_6923_2643',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u044f'},
                    78575: {'url': u'yandex_rkub_taxi_support_6923',
                            'is_deleted': False,
                            'name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430 '
                                    u'\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438'},
                    92018: {'url': u'yandex_rkub_taxi_support_6035_1229',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 '
                                    u'\u0440\u0430\u0431\u043e\u0442\u044b \u0441 \u0438\u043d\u0446\u0438\u0434\u0435\u043d\u0442\u0430\u043c\u0438'},
                    79093: {'url': u'ext_2027_3589',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 '
                                    u'\u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u0432 \u042f\u043d\u0434\u0435\u043a\u0441.'
                                    u'\u041f\u0440\u043e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435 \u0421\u041f'},
                    82679: {'url': u'ext_yataxi_3452',
                            'is_deleted': False,
                            'name': u'\u0412\u043d\u0435\u0448\u043d\u0438\u0435 '
                                    u'\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442\u044b '
                                    u'\u041a\u043e\u043b\u043b-\u0446\u0435\u043d\u0442\u0440\u0430'},
                    66040: {'url': u'yandex_search_tech_sq_7195',
                            'is_deleted': False,
                            'name': u'\u041e\u0442\u0434\u0435\u043b '
                                    u'\u042f\u043d\u0434\u0435\u043a\u0441.\u0412\u0438\u0434\u0435\u043e'},
                    44283: {'url': u'yandex_rkub_taxi_cust_supp',
                            'is_deleted': False,
                            'name': u'\u0426\u0435\u043d\u0442\u0440\u044b \u042f\u043d\u0434\u0435\u043a\u0441.\u0422\u0430\u043a\u0441\u0438'},
                    66046: {'url': u'yandex_search_tech_sq_8135',
                            'is_deleted': False,
                            'name': u'\u041e\u0442\u0434\u0435\u043b \u042f\u043d\u0434\u0435\u043a\u0441.\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0438'},
                    67071: {'url': u'yandex_edu_personel_0289_8372',
                            'is_deleted': False,
                            'name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u0432 '
                                    u'\u042f\u043d\u0434\u0435\u043a\u0441.\u041f\u0440\u043e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435'},
                    2864: {'url': u'yandex_personal_com_aux_sec',
                           'is_deleted': False,
                           'name': u'Группа аналитики и безопасности систем авторизации'},
                    })

    def test_fail_staff_builder(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_side_effect('get_all_persons', BaseStaffError)
                self.assertRaises(StaffError, lambda: get_staff(self.config).get_all_persons())

    def test_fail_staff_builder_2(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_side_effect('get_all_departments', BaseStaffError)
                self.assertRaises(StaffError, lambda: get_staff(self.config).get_all_departments())

    def test_staff_empty_response(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_persons', TEST_STAFF_EMPTY_RESPONSE)
                r1 = get_staff(self.config).get_all_persons()
                self.assertDictEqual(r1, {})

    def test_staff_empty_departments_response(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_departments', TEST_STAFF_EMPTY_RESPONSE)
                r1 = get_staff(self.config).get_all_departments()
                self.assertDictEqual(r1, {})

    def test_download_staff(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_persons', json.dumps(TEST_STAFF_GET_ALL_PERSONS_RESPONSE))
                fake_staff.set_response_value('get_all_departments',
                                              json.dumps(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE))
                staff_persons = get_staff(self.config).get_all_persons()
                staff_departments = get_staff(self.config).get_all_departments()
                ExternalRecord.insert_staff(staff_persons, staff_departments)
                self.assert_external_filled_with_staff()
                self.assert_departments_filled_with_staff()
                self.assert_user_info_filled_with_staff()

                fake_staff.set_response_side_effect('get_all_persons', BaseStaffError)
                fake_staff.set_response_side_effect('get_all_departments', BaseStaffError)
                with self.assertRaises(StaffError):
                    staff_persons = get_staff(self.config).get_all_persons()
                    staff_departments = get_staff(self.config).get_all_departments()
                    ExternalRecord.insert_staff(staff_persons, staff_departments)
                self.assert_external_filled_with_staff()
                self.assert_departments_filled_with_staff()
                self.assert_user_info_filled_with_staff()

    def test_staff_records_removal_and_restore(self):
        with self.app.app_context():
            with FakeStaff() as fake_staff:
                fake_staff.set_response_value('get_all_persons', json.dumps(TEST_STAFF_GET_ALL_PERSONS_RESPONSE))
                fake_staff.set_response_value('get_all_departments',
                                              json.dumps(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE))
                staff_persons = get_staff(self.config).get_all_persons()
                staff_departments = get_staff(self.config).get_all_departments()
                ExternalRecord.insert_staff(staff_persons, staff_departments)
                self.assert_external_filled_with_staff()
                self.assert_departments_filled_with_staff()
                self.assert_user_info_filled_with_staff()

                # Проверяем, что мы меняем только state, но не удаляем записи из базы
                fake_staff.set_response_value('get_all_persons', json.dumps(TEST_DISABLED_STAFF_GET_ALL_PERSONS_RESPONSE))
                fake_staff.set_response_value('get_all_departments',
                                              json.dumps(TEST_DISABLED_STAFF_GET_ALL_DEPARTMENTS_RESPONSE))
                staff_persons = get_staff(self.config).get_all_persons()
                staff_departments = get_staff(self.config).get_all_departments()
                ExternalRecord.insert_staff(staff_persons, staff_departments)
                self.assert_departments_filled_with_staff(state=1)
                self.assert_user_info_filled_with_staff(state=1)
                self.assert_external_filled_with_staff()

                # Проверяем, что state восстановился
                fake_staff.set_response_value('get_all_persons', json.dumps(TEST_STAFF_GET_ALL_PERSONS_RESPONSE))
                fake_staff.set_response_value('get_all_departments',
                                              json.dumps(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE))
                staff_persons = get_staff(self.config).get_all_persons()
                staff_departments = get_staff(self.config).get_all_departments()
                ExternalRecord.insert_staff(staff_persons, staff_departments)
                self.assert_external_filled_with_staff()
                self.assert_departments_filled_with_staff()
                self.assert_user_info_filled_with_staff()

    def test_yasm_agent_ok(self):
        with self.app.app_context():
            with FakeYasmAgent() as fake_yasm_agent:
                fake_yasm_agent.set_response_value('', json.dumps(TEST_YASM_AGENT_OK_RESPONSE))
                request_data = make_golovan_metrics(
                    self.config,
                    {
                        'count_secrets_max': 4,
                        'count_active_secrets_max': 4,
                    },
                )

                self.assertListEqual(
                    request_data,
                    [{'tags': {'ctype': 'development',
                               'geo': self.config['application']['current_dc'] or 'none',
                               'itype': 'yav',
                               'prj': 'vault-api'},
                      'ttl': 60,
                      'values': [{'name': 'count_secrets_max', 'val': 4},
                                 {'name': 'count_active_secrets_max', 'val': 4}]}],
                )

                response = get_yasm_agent().push_metrics(request_data)
                self.assertDictEqual(response, TEST_YASM_AGENT_OK_RESPONSE)

                self.assertEqual(len(fake_yasm_agent.requests), 1)
                fake_yasm_agent.requests[0].assert_properties_equal(
                    url='http://localhost:11005',
                    method='POST',
                    post_args=json.dumps(request_data, sort_keys=True),
                )
