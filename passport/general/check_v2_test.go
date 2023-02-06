package handlers

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcontext"
)

var ValidRolesWithUser = `{"revision":"GYYTKYZRMVSDC","born_date":1633427153,"tvm":{"11":{"/role/factors_by_number/":[{}]}},"user":{"100500":{"/role/everything/":[{"foo": "bar"}]},"100501":{"/role/something/":[{}]}}}`

func TestCheckHandlerV2(t *testing.T) {
	cache := newTestCheckState()
	handler := CheckHandlerV2(createComplexConfigWithEnv(tvm.BlackboxProdYateam), cache)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-Service-Ticket": `"YYY"`}),
		&errs.InvalidParam{Message: "missing parameter 'self'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": `"YYY"`}),
		&errs.InvalidParam{Message: "missing parameter 'self'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "nothing to do: there is no Service- or User-Ticket"},
	)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest(
			"self=kokoko&required_service_roles=/role/factors_by_number/&required_user_roles=/role/everything/",
			map[string]string{
				"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgQICxBv:A_Cki3A0jo6uMpyiVShpmZq_BZYwYYgKRfux7B5oSobiDaJFtgJ4LERijeIqI8784o_yXwGYhVbP7xcbidk6taptyNqvYt8oPrcYuqw9SLlNYZax8h_gcmuj_sGZCsDAs0u0SbshZmATGJXW4eyJOSlyIxwDViykX5OwlRwiL2M",
				"X-Ya-User-Ticket":    "kek",
			},
		),
		`{"status":"CHECK_FAILED","error":"invalid user ticket","service":{"status":"OK","debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=11;dst=111;scope=;","logging_string":"3:serv:CBAQ__________9_IgQICxBv:","src":11,"roles":{"/role/factors_by_number/":[]}},"user":{"status":"INVALID_TICKET","error":"invalid ticket format","debug_string":"","logging_string":"kek","default_uid":"","uids":null,"scopes":null,"roles":null}}
`,
		http.StatusForbidden)
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest(
			"self=kokoko&required_service_roles=/role/factors_by_number/&required_user_roles=/role/everything/",
			map[string]string{
				"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgQICxBv:A_Cki3A0jo6uMpyiVShpmZq_BZYwYYgKRfux7B5oSobiDaJFtgJ4LERijeIqI8784o_yXwGYhVbP7xcbidk6taptyNqvYt8oPrcYuqw9SLlNYZax8h_gcmuj_sGZCsDAs0u0SbshZmATGJXW4eyJOSlyIxwDViykX5OwlRwiL2M",
				"X-Ya-User-Ticket":    "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:IlRiyBNH1umPvcFOAdo5Zt7RlEvHNsWv1QO7sywC-Wsyl_mgveKGvcvfW-iw0Y-NnKmiiqBmCs78572dtlEMHvGCK7bGTlqWAmaZK6HL_gEa2IsJMyPx4fPQ5vILhBDdXIp5kUtKGm5LiBCf10-XtPZ7vl-umLqp4uc9Zh09nk8",
			},
		),
		`{"status":"OK","service":{"status":"OK","debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=11;dst=111;scope=;","logging_string":"3:serv:CBAQ__________9_IgQICxBv:","src":11,"roles":{"/role/factors_by_number/":[]}},"user":{"status":"OK","debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;","logging_string":"3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:","default_uid":"100500","uids":["100500"],"scopes":["some:scope"],"roles":{"100500":{"/role/everything/":[{"foo":"bar"}]}}}}
`,
		http.StatusOK)
}

func TestCheckServiceTicket(t *testing.T) {
	serviceTicket := "3:serv:CBAQ__________9_IgQICxBv:A_Cki3A0jo6uMpyiVShpmZq_BZYwYYgKRfux7B5oSobiDaJFtgJ4LERijeIqI8784o_yXwGYhVbP7xcbidk6taptyNqvYt8oPrcYuqw9SLlNYZax8h_gcmuj_sGZCsDAs0u0SbshZmATGJXW4eyJOSlyIxwDViykX5OwlRwiL2M"
	cfg := createComplexConfig()

	t.Run("invalid params", func(t *testing.T) {
		res, err := checkServiceTicket(url.Values{}, "", cfg, newTestCheckState())
		require.EqualError(t, err, "missing parameter 'self'")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("no service context", func(t *testing.T) {
		cache := newTestCheckState()
		cache.err = xerrors.New("kek")

		res, err := checkServiceTicket(
			url.Values{"self": []string{"kekeke"}},
			"",
			cfg,
			cache,
		)
		require.EqualError(t, err, "kek")
		require.IsType(t, &errs.Temporary{}, err)
		require.Nil(t, res)
	})

	t.Run("bad ticket", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kekeke"}},
			"kek",
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseService{
				checkResponseCommon: checkResponseCommon{
					Status:        "INVALID_TICKET",
					Error:         "invalid ticket format",
					LoggingString: "kek",
					topLevelError: "invalid service ticket",
				},
			},
			*res,
		)
	})

	t.Run("valid ticket, no roles required", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kekeke"}},
			"3:serv:CBAQ__________9_IgQIKhBw:E8ltCpcTZ4DvLkDyHQjmbYo5Ci2PistbtQ1ygK1KfU2_868J3kgqhjXLKGQnHCiQCA8C8r8qE3A9pR4Y85ZzlMOt_ebImqGtSWjK0IDh6VKLpb9rL6KOAm4XqdlFFvx8QCGKVk4msRIPwWq339y3U6la0zBPNyQQSkwQEb6nQLQ",
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseService{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=42;dst=112;scope=;",
					LoggingString: "3:serv:CBAQ__________9_IgQIKhBw:",
				},
				Src: 42,
			},
			*res,
		)
	})

	t.Run("invalid params, roles required", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kokoko"}},
			serviceTicket,
			cfg,
			newTestCheckState(),
		)
		require.EqualError(t, err, "missing parameter 'required_service_roles'")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("no roles", func(t *testing.T) {
		cache := newTestCheckState()
		cache.err = xerrors.New("kek")

		res, err := checkServiceTicket(
			url.Values{"self": []string{"kekeke2"}, "required_service_roles": []string{"any"}},
			serviceTicket,
			cfg,
			cache,
		)
		require.EqualError(t, err, "failed to get roles for alias: 'kekeke2': kek")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("any role required", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kokoko"}, "required_service_roles": []string{"any"}},
			serviceTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseService{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=11;dst=111;scope=;",
					LoggingString: "3:serv:CBAQ__________9_IgQICxBv:",
				},
				Src: 11,
				Roles: checkResponseRoles{
					"/role/factors_by_number/": []map[string]string{},
				},
			},
			*res,
		)
	})

	t.Run("missing exact role", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kokoko"}, "required_service_roles": []string{"foo"}},
			serviceTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseService{
				checkResponseCommon: checkResponseCommon{
					Status:        "NO_ROLES",
					Error:         "missing role 'foo'",
					DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=11;dst=111;scope=;",
					LoggingString: "3:serv:CBAQ__________9_IgQICxBv:",
					topLevelError: "no roles for service",
				},
				Src: 11,
				Roles: checkResponseRoles{
					"/role/factors_by_number/": []map[string]string{},
				},
			},
			*res,
		)
	})

	t.Run("has exact role", func(t *testing.T) {
		res, err := checkServiceTicket(
			url.Values{"self": []string{"kokoko"}, "required_service_roles": []string{"/role/factors_by_number/"}},
			serviceTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseService{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=11;dst=111;scope=;",
					LoggingString: "3:serv:CBAQ__________9_IgQICxBv:",
				},
				Src: 11,
				Roles: checkResponseRoles{
					"/role/factors_by_number/": []map[string]string{},
				},
			},
			*res,
		)
	})
}

func TestCheckUserTicket(t *testing.T) {
	userTicket := "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:IlRiyBNH1umPvcFOAdo5Zt7RlEvHNsWv1QO7sywC-Wsyl_mgveKGvcvfW-iw0Y-NnKmiiqBmCs78572dtlEMHvGCK7bGTlqWAmaZK6HL_gEa2IsJMyPx4fPQ5vILhBDdXIp5kUtKGm5LiBCf10-XtPZ7vl-umLqp4uc9Zh09nk8"
	cfg := createComplexConfigWithEnv(tvm.BlackboxProdYateam)

	t.Run("invalid params", func(t *testing.T) {
		res, err := checkUserTicket(url.Values{}, "", cfg, newTestCheckState())
		require.EqualError(t, err, "missing parameter 'self'")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("no roles", func(t *testing.T) {
		cache := newTestCheckState()
		cache.err = xerrors.New("kek")

		res, err := checkUserTicket(
			url.Values{"self": []string{"kekeke2"}, "required_user_roles": []string{"any"}},
			userTicket,
			cfg,
			cache,
		)
		require.EqualError(t, err, "failed to get roles for alias: 'kekeke2': kek")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("no user context", func(t *testing.T) {
		cache := newTestCheckState()
		cache.err = xerrors.New("kek")

		res, err := checkUserTicket(
			url.Values{"self": []string{"kekeke"}},
			"",
			cfg,
			cache,
		)
		require.EqualError(t, err, "kek")
		require.IsType(t, &errs.Temporary{}, err)
		require.Nil(t, res)
	})

	t.Run("bad env", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kekeke"}, "override_env": []string{"kek"}},
			"",
			cfg,
			newTestCheckState(),
		)
		require.EqualError(t, err, "overridden env failed to be parsed: blackbox env is unknown: 'kek'")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("bad ticket", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kekeke"}},
			"kek",
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "INVALID_TICKET",
					Error:         "invalid ticket format",
					LoggingString: "kek",
					topLevelError: "invalid user ticket",
				},
			},
			*res,
		)
	})

	t.Run("valid ticket, no roles required", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kekeke"}},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
			},
			*res,
		)
	})

	t.Run("invalid params, roles required", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kokoko"}},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.EqualError(t, err, "missing parameter 'required_user_roles'")
		require.IsType(t, &errs.InvalidParam{}, err)
		require.Nil(t, res)
	})

	t.Run("any role required", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kokoko"}, "required_user_roles": []string{"any"}},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": []map[string]string{{"foo": "bar"}}},
				},
			},
			*res,
		)
	})

	t.Run("missing exact role", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kokoko"}, "required_user_roles": []string{"foo"}},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "NO_ROLES",
					Error:         "missing role 'foo'",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
					topLevelError: "no roles for user",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": []map[string]string{{"foo": "bar"}}},
				},
			},
			*res,
		)
	})

	t.Run("has exact role", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{"self": []string{"kokoko"}, "required_user_roles": []string{"/role/everything/"}},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": []map[string]string{{"foo": "bar"}}},
				},
			},
			*res,
		)
	})

	t.Run("missing scope", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{
				"self":                 []string{"kokoko"},
				"required_user_roles":  []string{"/role/everything/"},
				"required_user_scopes": []string{"kek"},
			},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "NO_SCOPES",
					Error:         "missing scope 'kek'",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
					topLevelError: "no scopes for user",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": []map[string]string{{"foo": "bar"}}},
				},
			},
			*res,
		)
	})

	t.Run("valid scope", func(t *testing.T) {
		res, err := checkUserTicket(
			url.Values{
				"self":                 []string{"kokoko"},
				"required_user_roles":  []string{"/role/everything/"},
				"required_user_scopes": []string{"some:scope"},
			},
			userTicket,
			cfg,
			newTestCheckState(),
		)
		require.NoError(t, err)
		require.NotNil(t, res)
		require.EqualValues(t,
			checkResponseUser{
				checkResponseCommon: checkResponseCommon{
					Status:        "OK",
					DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=some:scope;default_uid=100500;uid=100500;env=ProdYateam;",
					LoggingString: "3:user:CAwQ__________9_Gh4KBAiUkQYQlJEGGgpzb21lOnNjb3BlINKF2MwEKAI:",
				},
				DefaultUID: "100500",
				UIDs:       []string{"100500"},
				Scopes:     []string{"some:scope"},
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": []map[string]string{{"foo": "bar"}}},
				},
			},
			*res,
		)
	})
}

func TestMergeCheckResponse(t *testing.T) {
	serviceErr := "service error"
	userErr := "user error"
	service := checkResponseService{checkResponseCommon: checkResponseCommon{
		Status:        "OK",
		topLevelError: serviceErr,
	}}
	user := checkResponseUser{checkResponseCommon: checkResponseCommon{
		Status:        "OK",
		topLevelError: userErr,
	}}

	t.Run("both failed", func(t *testing.T) {
		srv := service
		srv.Status = "srv status"
		usr := user
		usr.Status = "usr status"

		require.EqualValues(t,
			checkResponseV2{
				Status:  "CHECK_FAILED",
				Error:   "service error. user error",
				Service: &srv,
				User:    &usr,
			},
			*mergeCheckResponse(&srv, &usr),
		)
	})

	t.Run("service failed", func(t *testing.T) {
		srv := service
		srv.Status = "srv status"

		require.EqualValues(t,
			checkResponseV2{
				Status:  "CHECK_FAILED",
				Error:   "service error",
				Service: &srv,
				User:    &user,
			},
			*mergeCheckResponse(&srv, &user),
		)
	})

	t.Run("user failed", func(t *testing.T) {
		usr := user
		usr.Status = "usr status"

		require.EqualValues(t,
			checkResponseV2{
				Status:  "CHECK_FAILED",
				Error:   "user error",
				Service: &service,
				User:    &usr,
			},
			*mergeCheckResponse(&service, &usr),
		)
	})

	t.Run("ok", func(t *testing.T) {
		require.EqualValues(t,
			checkResponseV2{
				Status:  "OK",
				Service: &service,
				User:    &user,
			},
			*mergeCheckResponse(&service, &user),
		)
	})
}

func TestCheckServiceRoles(t *testing.T) {
	roles, err := tvm.NewRoles([]byte(ValidRolesWithUser))
	require.NoError(t, err)
	serviceTicket := tvmcontext.CheckedServiceTicket{SrcID: 11}

	t.Run("missing exact roles, do not show roles", func(t *testing.T) {
		for _, rol := range []*tvm.Roles{roles, nil} {
			resultIn := &checkResponseService{}
			err := checkServiceRoles(
				"foo,bar",
				false,
				rol,
				&serviceTicket,
				resultIn,
			)

			require.EqualError(t, err, "missing role 'foo'")
			require.EqualValues(t, checkResponseService{}, *resultIn)
		}
	})

	t.Run("missing exact roles, show roles", func(t *testing.T) {
		resultIn := &checkResponseService{}
		err := checkServiceRoles(
			"foo,bar",
			true,
			roles,
			&serviceTicket,
			resultIn,
		)

		require.EqualError(t, err, "missing role 'foo'")
		require.EqualValues(t,
			checkResponseService{
				Roles: checkResponseRoles{"/role/factors_by_number/": {}},
			},
			*resultIn,
		)

		require.EqualError(t, err, "missing role 'foo'")
		require.EqualValues(t,
			checkResponseService{
				Roles: checkResponseRoles{"/role/factors_by_number/": {}},
			},
			*resultIn,
		)
	})

	t.Run("missing any role, do not show roles", func(t *testing.T) {
		ticket := serviceTicket
		ticket.SrcID = 42

		resultIn := &checkResponseService{}
		err := checkServiceRoles(
			"any",
			false,
			roles,
			&ticket,
			resultIn,
		)

		require.EqualError(t, err, "missing any role")
	})

	t.Run("has some roles, do not show roles", func(t *testing.T) {
		resultIn := &checkResponseService{}
		err := checkServiceRoles(
			"any",
			false,
			roles,
			&serviceTicket,
			resultIn,
		)

		require.NoError(t, err)
	})
}

func TestCheckUserRoles(t *testing.T) {
	roles, err := tvm.NewRoles([]byte(ValidRolesWithUser))
	require.NoError(t, err)
	userTicket := tvmcontext.CheckedUserTicket{
		DefaultUID: 100500,
		Uids:       []tvm.UID{100500, 100501, 100502},
		Env:        tvm.BlackboxProdYateam,
	}

	t.Run("missing exact roles: uid=100500, do not show roles", func(t *testing.T) {
		ticket := userTicket
		ticket.DefaultUID = 100500

		for _, rol := range []*tvm.Roles{roles, nil} {
			resultIn := &checkResponseUser{}
			err := checkUserRoles(
				"foo,bar",
				false,
				rol,
				&ticket,
				resultIn,
			)

			require.EqualError(t, err, "missing role 'foo'")
			require.EqualValues(t, checkResponseUser{}, *resultIn)
		}
	})
	t.Run("missing exact roles: uid=100502, do not show roles", func(t *testing.T) {
		ticket := userTicket
		ticket.DefaultUID = 100502

		for _, rol := range []*tvm.Roles{roles, nil} {
			resultIn := &checkResponseUser{}
			err := checkUserRoles(
				"foo,bar",
				false,
				rol,
				&ticket,
				resultIn,
			)

			require.EqualError(t, err, "missing role 'foo'")
		}
	})

	t.Run("missing exact roles, show roles", func(t *testing.T) {
		ticket := userTicket
		ticket.DefaultUID = 100500

		resultIn := &checkResponseUser{}
		err := checkUserRoles(
			"foo,bar",
			true,
			roles,
			&ticket,
			resultIn,
		)

		require.EqualError(t, err, "missing role 'foo'")
		require.EqualValues(t,
			checkResponseUser{
				Roles: map[string]checkResponseRoles{
					"100500": {"/role/everything/": {{"foo": "bar"}}},
					"100501": {"/role/something/": {}},
					"100502": {},
				},
			},
			*resultIn,
		)
	})

	t.Run("do not check roles, do not show roles", func(t *testing.T) {
		ticket := userTicket
		ticket.DefaultUID = 100502

		resultIn := &checkResponseUser{}
		err := checkUserRoles(
			"none",
			false,
			roles,
			&ticket,
			resultIn,
		)

		require.NoError(t, err)
	})

	t.Run("has some roles, do not show roles", func(t *testing.T) {
		resultIn := &checkResponseUser{}
		err := checkUserRoles(
			"any",
			false,
			roles,
			&userTicket,
			resultIn,
		)

		require.NoError(t, err)
	})

	t.Run("has exact role", func(t *testing.T) {
		resultIn := &checkResponseUser{}
		err := checkUserRoles(
			"/role/everything/",
			false,
			roles,
			&userTicket,
			resultIn,
		)

		require.NoError(t, err)
	})

	t.Run("check only default uid roles", func(t *testing.T) {
		resultIn := &checkResponseUser{}
		err := checkUserRoles(
			"/role/something/",
			false,
			roles,
			&userTicket,
			resultIn,
		)

		require.EqualError(t, err, "missing role '/role/something/'")
	})
}

func TestCheckRoles(t *testing.T) {
	require.NoError(t,
		checkRoles("none", getConsumerRoles(), xerrors.New("kek")),
	)

	require.EqualError(t,
		checkRoles("any", &tvm.ConsumerRoles{}, xerrors.New("kek")),
		"kek",
	)
	require.NoError(t,
		checkRoles("any", getConsumerRoles(), nil),
	)

	require.EqualError(t,
		checkRoles("foo", &tvm.ConsumerRoles{}, xerrors.New("kek")),
		"kek",
	)
	require.EqualError(t,
		checkRoles("foo", &tvm.ConsumerRoles{}, nil),
		"missing role 'foo'",
	)
	require.NoError(t,
		checkRoles("/role/everything/", getConsumerRoles(), nil),
	)
	require.EqualError(t,
		checkRoles("/role/everything/,foo", getConsumerRoles(), nil),
		"missing role 'foo'",
	)
}

func TestSetInvalidTicketError(t *testing.T) {
	t.Run("cut", func(t *testing.T) {
		resp := checkResponseCommon{}
		setInvalidTicketError(xerrors.New("kek"), "lol", &resp)
		require.EqualValues(t,
			checkResponseCommon{
				Status:        "INVALID_TICKET",
				Error:         "kek",
				topLevelError: "lol",
			},
			resp,
		)
	})

	t.Run("common", func(t *testing.T) {
		err := &errs.Forbidden{
			Message:       "foo",
			DebugString:   "some_debug",
			LoggingString: "some_logable",
		}
		resp := checkResponseCommon{}
		setInvalidTicketError(err, "lol", &resp)
		require.EqualValues(t,
			checkResponseCommon{
				Status:        "INVALID_TICKET",
				Error:         "foo",
				topLevelError: "lol",
				DebugString:   "some_debug",
				LoggingString: "some_logable",
			},
			resp,
		)
	})
}

func TestSetNoRolesError(t *testing.T) {
	resp := checkResponseCommon{}
	setNoRolesError(xerrors.New("kek"), "lol", &resp)
	require.EqualValues(t,
		checkResponseCommon{
			Status:        "NO_ROLES",
			Error:         "kek",
			topLevelError: "lol",
		},
		resp,
	)
}

func TestShowRoles(t *testing.T) {
	require.True(t, showRoles(url.Values{"lol": []string{}}))
	require.True(t, showRoles(url.Values{"show_roles": []string{}}))
	require.True(t, showRoles(url.Values{"show_roles": []string{"yes"}}))
	require.True(t, showRoles(url.Values{"show_roles": []string{"false"}}))
	require.False(t, showRoles(url.Values{"show_roles": []string{"no"}}))
}

func TestConvertRoles(t *testing.T) {
	require.EqualValues(t,
		checkResponseRoles{
			"/role/everything/": []tvm.Entity{{"foo": "bar"}},
		},
		convertRoles(getConsumerRoles()),
	)
}

func TestConvertUserRoles(t *testing.T) {
	roles, err := tvm.NewRoles([]byte(ValidRolesWithUser))
	require.NoError(t, err)

	ticket := &tvm.CheckedUserTicket{
		UIDs: []tvm.UID{100500, 100501, 100502},
		Env:  tvm.BlackboxProdYateam,
	}
	require.EqualValues(t,
		map[string]checkResponseRoles{
			"100500": {
				"/role/everything/": []tvm.Entity{{"foo": "bar"}},
			},
			"100501": {
				"/role/something/": []tvm.Entity{},
			},
			"100502": {},
		},
		convertUserRoles(ticket, roles),
	)
}

func TestConvertUIDs(t *testing.T) {
	require.EqualValues(t,
		[]string{"42", "10005000"},
		convertUIDs([]tvm.UID{42, 10005000}),
	)
}

func TestGetRequiredArgsForCheck(t *testing.T) {
	cfg := createComplexConfig()

	type Case struct {
		name          string
		query         url.Values
		clientID      tvm.ClientID
		requiredRoles string
		err           string
	}
	cases := []Case{
		{
			name:  "no self",
			query: url.Values{"lol": []string{}},
			err:   "missing parameter 'self'",
		},
		{
			name:  "unknown self",
			query: url.Values{"self": []string{"bar"}},
			err:   "couldn't find client in config by alias: 'bar'",
		},
		{
			name:     "no roles on client",
			query:    url.Values{"self": []string{"kekeke"}},
			clientID: 112,
		},
		{
			name:  "client with roles, missing arg",
			query: url.Values{"self": []string{"kokoko"}},
			err:   "missing parameter 'foo'",
		},
		{
			name:          "client with roles, missing arg",
			query:         url.Values{"self": []string{"kokoko"}, "foo": []string{"bar"}},
			clientID:      111,
			requiredRoles: "bar",
		},
	}

	for _, c := range cases {
		client, requiredRoles, err := getRequiredArgsForCheck(c.query, cfg, "foo")
		if c.err == "" {
			require.NoError(t, err, c.name)
			require.EqualValues(t, c.clientID, client.SelfTvmID, c.name)
			require.EqualValues(t, c.requiredRoles, requiredRoles, c.name)
		} else {
			require.EqualError(t, err, c.err, c.name)
		}
	}
}

func getConsumerRoles() *tvm.ConsumerRoles {
	roles, err := tvm.NewRoles([]byte(ValidRolesWithUser))
	if err != nil {
		panic(err)
	}

	consumerRoles, err := roles.GetRolesForUser(&tvm.CheckedUserTicket{
		DefaultUID: 100500,
		Env:        tvm.BlackboxProdYateam,
	}, nil)
	if err != nil {
		panic(err)
	}

	return consumerRoles
}

type testCheckState struct {
	srv   *tvmcontext.ServiceContext
	usr   *tvmcontext.UserContext
	roles map[string]*tvm.Roles
	err   error
}

func newTestCheckState() *testCheckState {
	sc, err := tvmcontext.NewServiceContext(getTestKeys(getKeys()))
	if err != nil {
		panic(err)
	}
	uc, err := tvmcontext.NewUserContext(getTestKeys(getKeys()), tvm.BlackboxProdYateam)
	if err != nil {
		panic(err)
	}
	ongoingRoles, err := tvm.NewRoles([]byte(ValidRolesWithUser))
	if err != nil {
		panic(err)
	}

	return &testCheckState{
		srv:   sc,
		usr:   uc,
		roles: map[string]*tvm.Roles{"some_slug": ongoingRoles},
	}
}

func (t *testCheckState) GetServiceContext() (*tvmcontext.ServiceContext, error) {
	return t.srv, t.err
}

func (t *testCheckState) GetUserContext() (*tvmcontext.UserContext, error) {
	return t.usr, t.err
}

func (t *testCheckState) GetRoles(slug string) (*tvm.Roles, error) {
	return t.roles[slug], t.err
}
