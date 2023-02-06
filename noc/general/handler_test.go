package tacacs_test

import (
	"context"
	"fmt"
	"net"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/contrib/go/patched/tacplus"
	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/nocauth/pkg/tacacs"
	"a.yandex-team.ru/noc/nocauth/pkg/types"
)

type MockLdapChecker struct {
	Valid bool
}

func (c *MockLdapChecker) Validate(_, _ string) error {
	if c.Valid {
		return nil
	}
	return fmt.Errorf("mock ldap check failed")
}

type MockRoleStorage struct {
	checkRole types.AccessType
	device    types.DeviceIPs
}

func (s *MockRoleStorage) CheckRole(_, _ string, _ bool) types.AccessType {
	return s.checkRole
}

func (s *MockRoleStorage) GetDeviceByIP(ip string) (res types.DeviceIPs, found bool) {
	if s.device.Name == "" {
		return res, false
	}
	return s.device, true
}

func mockRequestHandler(ldap *MockLdapChecker, rs *MockRoleStorage) (*tacacs.RequestHandler, error) {
	labChecker, err := tacacs.NewLabNetChecker()
	if err != nil {
		return nil, fmt.Errorf("new lab net checker: %w", err)
	}
	logger, err := zap.New(zap.ConsoleConfig(log.DebugLevel))
	if err != nil {
		return nil, fmt.Errorf("create logger: %w", err)
	}
	frozenTime, err := time.Parse("2006-01-02", "2017-01-01")
	if err != nil {
		return nil, err
	}
	otPasswordManager := tacacs.NewOTPasswordManagerWithNow([]byte("secret"), func() time.Time {
		return frozenTime
	})
	return &tacacs.RequestHandler{
		RoleStorage:   rs,
		Logger:        logger,
		LabNetChecker: labChecker,
		Verificator:   tacacs.NewNOCVerificator(otPasswordManager, ldap),
	}, nil
}

func TestHandler_HandleAuthenRequest(t *testing.T) {
	testCases := []struct {
		name        string
		request     *tacplus.AuthenStart
		roleStorage *MockRoleStorage
		session     tacacs.ServerSession
		ldapChecker *MockLdapChecker
		expected    *tacplus.AuthenReply
	}{
		{
			name: "test_pap_success",
			request: &tacplus.AuthenStart{
				Action:        tacplus.AuthenActionLogin,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypePAP,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "some_port",
				RemAddr:       "127.0.0.1",
				Data:          []byte("password"),
			},
			roleStorage: &MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", "password"),
			ldapChecker: &MockLdapChecker{Valid: true},
			expected: &tacplus.AuthenReply{
				Status:    tacplus.AuthenStatusPass,
				NoEcho:    false,
				ServerMsg: "",
				Data:      nil,
			},
		},
		{
			name: "test_no_role",
			request: &tacplus.AuthenStart{
				Action:        tacplus.AuthenActionLogin,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypePAP,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "some_port",
				RemAddr:       "127.0.0.1",
				Data:          []byte("password"),
			},
			roleStorage: &MockRoleStorage{checkRole: types.NoAccess, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", "password"),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected:    nil,
		},
		{
			name: "test_pap_success_with_ot_password",
			request: &tacplus.AuthenStart{
				Action:        tacplus.AuthenActionLogin,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypePAP,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "some_port",
				RemAddr:       "127.0.0.1",
				Data:          []byte("SEi7HUKW0|1Cntza"),
			},
			roleStorage: &MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", "SEi7HUKW0|1Cntza"),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected: &tacplus.AuthenReply{
				Status:    tacplus.AuthenStatusPass,
				NoEcho:    false,
				ServerMsg: "",
				Data:      nil,
			},
		},
		{
			name: "test_pap_success_with_ot_invalid_password",
			request: &tacplus.AuthenStart{
				Action:        tacplus.AuthenActionLogin,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypePAP,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "some_port",
				RemAddr:       "127.0.0.1",
				Data:          []byte("SEi7HUKW01|1Cntza"),
			},
			roleStorage: &MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", "SEi7HUKW01|1Cntza"),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected:    nil,
		},
		{
			name: "test_pap_success_with_empty_password",
			request: &tacplus.AuthenStart{
				Action:        tacplus.AuthenActionLogin,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypePAP,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "some_port",
				RemAddr:       "127.0.0.1",
				Data:          []byte{},
			},
			roleStorage: &MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected:    nil,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			requestHandler, err := mockRequestHandler(testCase.ldapChecker, testCase.roleStorage)
			require.NoError(t, err)

			reply := requestHandler.HandleAuthenStart(
				context.TODO(),
				testCase.request,
				testCase.session,
			)
			require.Equal(t, testCase.expected, reply)
		})
	}
}

func TestHandler_HandleAuthorRequest(t *testing.T) {
	testCases := []struct {
		name        string
		request     *tacplus.AuthorRequest
		roleStorage *MockRoleStorage
		session     tacacs.ServerSession
		ldapChecker *MockLdapChecker
		expected    *tacplus.AuthorResponse
	}{
		{
			name: "test_juniper_sudo_success",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "junos-exec", Separator: tacacs.EqualSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.SudoAccess, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected: &tacplus.AuthorResponse{
				Status: tacplus.AuthorStatusPassAdd,
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "local-user-name", Value: "SU", Separator: tacacs.EqualSeparator},
				}),
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_juniper_ro_success",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "junos-exec", Separator: tacacs.EqualSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected: &tacplus.AuthorResponse{
				Status: tacplus.AuthorStatusPassAdd,
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "local-user-name", Value: "RO", Separator: tacacs.EqualSeparator},
				}),
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_juniper_no_role",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "junos-exec", Separator: tacacs.EqualSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.NoAccess, device: types.NewEmptyDeviceIPs("mx240-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: false},
			expected: &tacplus.AuthorResponse{
				Status:    tacplus.AuthorStatusFail,
				Arg:       nil,
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_shell_success",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "shell", Separator: tacacs.EqualSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.SudoAccess, device: types.NewEmptyDeviceIPs("s5548-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: true},
			expected: &tacplus.AuthorResponse{
				Status: tacplus.AuthorStatusPassAdd,
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "priv-lvl", Value: "15", Separator: tacacs.EqualSeparator},
				}),
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_nexus_shell_success",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "shell", Separator: tacacs.EqualSeparator},
					{Attribute: "shell:roles", Value: "", Separator: tacacs.AsteriskSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.SudoAccess, device: types.NewEmptyDeviceIPs("s5548-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: true},
			expected: &tacplus.AuthorResponse{
				Status: tacplus.AuthorStatusPassAdd,
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "shell:roles", Value: "\"network-admin\"", Separator: tacacs.EqualSeparator},
				}),
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_unrecognized_service",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg: tacacs.EncodeArgs([]*tacacs.Arg{
					{Attribute: "service", Value: "unknown", Separator: tacacs.EqualSeparator},
				}),
			},
			roleStorage: &MockRoleStorage{checkRole: types.SudoAccess, device: types.NewEmptyDeviceIPs("s5548-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: true},
			expected: &tacplus.AuthorResponse{
				Status:    tacplus.AuthorStatusFail,
				Arg:       nil,
				ServerMsg: "",
				Data:      "",
			},
		},
		{
			name: "test_no_service",
			request: &tacplus.AuthorRequest{
				AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
				PrivLvl:       1,
				AuthenType:    tacplus.AuthenTypeASCII,
				AuthenService: tacplus.AuthenServiceLogin,
				User:          "test_user",
				Port:          "123456",
				RemAddr:       "127.0.0.1",
				Arg:           nil,
			},
			roleStorage: &MockRoleStorage{checkRole: types.SudoAccess, device: types.NewEmptyDeviceIPs("s5548-test")},
			session:     newMockSession("test_user", ""),
			ldapChecker: &MockLdapChecker{Valid: true},
			expected: &tacplus.AuthorResponse{
				Status:    tacplus.AuthorStatusFail,
				Arg:       nil,
				ServerMsg: "",
				Data:      "",
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			requestHandler, err := mockRequestHandler(testCase.ldapChecker, testCase.roleStorage)
			require.NoError(t, err)

			reply := requestHandler.HandleAuthorRequest(
				context.TODO(),
				testCase.request,
				testCase.session,
			)
			require.Equal(t, testCase.expected, reply)
		})
	}
}

func TestHandler_HandleAcctRequest(t *testing.T) {
	requestHandler, err := mockRequestHandler(
		&MockLdapChecker{Valid: false},
		&MockRoleStorage{checkRole: types.Access, device: types.NewEmptyDeviceIPs("noc-sas")},
	)
	require.NoError(t, err)

	request := &tacplus.AcctRequest{
		Flags:         0,
		AuthenMethod:  tacplus.AuthenMethodTACACSPlus,
		PrivLvl:       1,
		AuthenType:    tacplus.AuthenTypeASCII,
		AuthenService: tacplus.AuthenServiceLogin,
		User:          "some_user",
		Port:          "some_port",
		RemAddr:       "127.0.0.1",
		Arg:           nil,
	}

	testCases := []struct {
		request  *tacplus.AcctRequest
		session  tacacs.ServerSession
		expected *tacplus.AcctReply
	}{
		{
			request: request,
			session: newMockSession("", ""),
			expected: &tacplus.AcctReply{
				Status:    tacplus.AcctStatusSuccess,
				ServerMsg: "",
				Data:      "",
			},
		},
	}

	for _, testCase := range testCases {
		t.Run("", func(t *testing.T) {
			reply := requestHandler.HandleAcctRequest(
				context.TODO(),
				testCase.request,
				testCase.session,
			)
			require.Equal(t, testCase.expected, reply)
		})
	}
}

type MockSession struct {
	localAddr  net.Addr
	remoteAddr net.Addr
	user       string
	password   string
}

func newMockSession(user string, password string) *MockSession {
	return &MockSession{
		localAddr: &net.TCPAddr{
			IP:   net.IPv4(127, 0, 0, 1),
			Zone: "",
		},
		remoteAddr: &net.TCPAddr{
			IP:   net.IPv4(127, 0, 0, 1),
			Zone: "",
		},
		user:     user,
		password: password,
	}
}

func (s *MockSession) RemoteAddr() net.Addr {
	return s.remoteAddr
}
func (s *MockSession) LocalAddr() net.Addr {
	return s.localAddr
}
func (s *MockSession) GetUser(ctx context.Context, message string) (*tacplus.AuthenContinue, error) {
	return &tacplus.AuthenContinue{
		Abort:   false,
		Message: s.user,
	}, nil
}
func (s *MockSession) GetPass(ctx context.Context, message string) (*tacplus.AuthenContinue, error) {
	return &tacplus.AuthenContinue{
		Abort:   false,
		Message: s.password,
	}, nil
}
