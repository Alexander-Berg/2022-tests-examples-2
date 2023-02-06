package main

import (
	"bytes"
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha1"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"os/exec"
	"path"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
	"github.com/stripe/krl"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/library/go/yandex/tvm/tvmauth"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mockskotty"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mockssh"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mocktvmcert"
)

const (
	RobotUID   = "1120000000021014"
	RobotLogin = " robot-passport-test \n"
	Data       = "some useful data"
	TvmID      = tvm.ClientID(172)
)

var (
	Principals     = []string{strings.TrimSpace(RobotLogin)}
	AgentRsaPrefix = []byte{0x00, 0x00, 0x00, 0x07, 's', 's', 'h', '-', 'r', 's', 'a'}
)

type IDType int

const (
	IDTypeUID IDType = iota
	IDTypeLogin
	IDTypeBoth
	IDTypeNone
)

func FormatResponse(response *resty.Response) string {
	return fmt.Sprintf("[%d] %s", response.StatusCode(), response.Body())
}

func GenVerifySSH(sign []byte, idType IDType) map[string]string {
	params := map[string]string{}
	switch idType {
	case IDTypeUID:
		params["uid"] = RobotUID
	case IDTypeLogin:
		params["login"] = RobotLogin
	case IDTypeBoth:
		params["uid"] = RobotUID
		params["login"] = RobotLogin
	case IDTypeNone:
	}
	params["to_sign"] = Data
	params["ssh_sign"] = base64.RawURLEncoding.EncodeToString(sign)

	return params
}

func GenVerifySSHKey(t *testing.T, toSign string, signer ssh.Signer, idType IDType) map[string]string {
	sign, err := signer.Sign(rand.Reader, []byte(toSign))
	require.NoError(t, err)

	return GenVerifySSH(sign.Blob, idType)
}

func GenVerifySSHCert(t *testing.T, toSign string, cert *ssh.Certificate, signer ssh.Signer, idType IDType) map[string]string {
	post := GenVerifySSHKey(t, toSign, signer, idType)
	post["public_cert"] = base64.RawURLEncoding.EncodeToString(cert.Marshal())
	return post
}

func GenGetTicketKey(t *testing.T, src string, dst string, signer ssh.Signer) map[string]string {
	ts := strconv.FormatInt(time.Now().Unix(), 10)
	toSSHSign := fmt.Sprintf("%s|%s|%s", ts, src, dst)
	sign, err := signer.Sign(rand.Reader, []byte(toSSHSign))
	require.NoError(t, err)

	return map[string]string{
		"grant_type": "sshkey",
		"src":        src,
		"dst":        dst,
		"ts":         ts,
		"login":      RobotLogin,
		"ssh_sign":   base64.RawURLEncoding.EncodeToString(sign.Blob),
	}
}

func GenGetTicketCert(t *testing.T, src string, dst string, cert *ssh.Certificate, signer ssh.Signer) map[string]string {
	params := GenGetTicketKey(t, src, dst, signer)
	params["public_cert"] = base64.RawURLEncoding.EncodeToString(cert.Marshal())
	return params
}

func GetPortFromFile(t *testing.T, filename string) int {
	data, err := ioutil.ReadFile(filename)
	require.NoError(t, err)
	tvmPort, err := strconv.ParseInt(string(data), 10, 64)
	require.NoError(t, err)
	return int(tvmPort)
}

func SourcePath(dir string) string {
	return yatest.SourcePath(path.Join("passport/infra/daemons/tvmapi/ut_py/data", dir))
}

type ManualTestSuite struct {
	suite.Suite
	CAKey    mockssh.ECDSAKeyPair
	BadCAKey mockssh.ECDSAKeyPair
	RSAKey   mockssh.RSAKeyPair
	ECDSAKey mockssh.ECDSAKeyPair

	Headers      map[string]string
	Client       *resty.Client
	TVMClientAPI tvm.Client
	TVMClient29  tvm.Client

	Skotty  *httptest.Server
	Tvmcert *exec.Cmd
}

func (s *ManualTestSuite) SetupSuite() {
	tvmHost := "http://localhost"
	tvmPort := GetPortFromFile(s.T(), "tvmapi.port")
	s.Client = resty.New().SetBaseURL(fmt.Sprintf("%s:%d", tvmHost, tvmPort))
	secret, err := ioutil.ReadFile(SourcePath("secret"))
	require.NoError(s.T(), err)
	secret = bytes.TrimSpace(secret)

	s.TVMClientAPI, err = tvmauth.NewAPIClient(tvmauth.TvmAPISettings{
		SelfID:               tvm.ClientID(27),
		ServiceTicketOptions: tvmauth.NewIDsOptions(string(secret), []tvm.ClientID{TvmID}),
		TVMHost:              tvmHost,
		TVMPort:              tvmPort,
	}, &nop.Logger{})
	require.NoError(s.T(), err)

	st, err := s.TVMClientAPI.GetServiceTicketForID(context.Background(), TvmID)
	require.NoError(s.T(), err)

	s.Headers = map[string]string{
		"X-Ya-Service-Ticket": st,
	}

	s.CAKey = mockssh.GetECDSAKeyFromFile(s.T(), SourcePath("ca_ecdsa"))
	s.ECDSAKey = mockssh.GetECDSAKeyFromFile(s.T(), SourcePath("id_ecdsa"))
	s.BadCAKey = mockssh.GetECDSAKeyFromFile(s.T(), SourcePath("bad_ecdsa"))
	s.RSAKey = mockssh.GetRSAKeyFromFile(s.T(), SourcePath("test_key"))

	s.TVMClient29, err = tvmauth.NewAPIClient(tvmauth.TvmAPISettings{
		SelfID:                      tvm.ClientID(29),
		EnableServiceTicketChecking: true,
		TVMHost:                     tvmHost,
		TVMPort:                     tvmPort,
	}, &nop.Logger{})
	require.NoError(s.T(), err)

	var skottyURL string
	s.Skotty, skottyURL = mockskotty.New(
		s.T(),
		[]mockssh.ECDSAKeyPair{
			s.CAKey,
		},
		&krl.KRL{},
	)

	config := mocktvmcert.MakeConfig(s.T(), skottyURL)
	config.HTTPCommon.Port = GetPortFromFile(s.T(), "tvmcert.port")

	s.Tvmcert, _ = mocktvmcert.New(s.T(), config)

	time.Sleep(time.Second * 5)
}

func (s *ManualTestSuite) TearDownSuite() {
	s.Skotty.Close()
	s.T().Logf("trying to shutdown daemon gracefully (%s)...", s.Tvmcert.Process.Signal(syscall.SIGINT))
	time.AfterFunc(5*time.Second, func() {
		s.T().Logf("killing daemon (%s)...", s.Tvmcert.Process.Kill())
	})
	s.T().Logf("daemon shutdown (%s)", s.Tvmcert.Wait())
}

func (s *ManualTestSuite) TestOkRegular() {
	post := GenVerifySSHKey(s.T(), Data, s.RSAKey.Signer, IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusOK, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"status":"OK","fingerprint":"8b:ca:b6:37:49:0f:53:2a:4d:3a:7a:39:30:12:26:05"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestOkCert() {
	cert, signer := mockssh.MakeECDSACert(s.T(), s.ECDSAKey.Signer, s.CAKey.Signer, 10, Principals)
	post := GenVerifySSHCert(s.T(), Data, cert, signer, IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusOK, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(), `{"status":"OK","fingerprint":""}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadCert() {
	cert, signer := mockssh.MakeECDSACert(s.T(), s.ECDSAKey.Signer, s.BadCAKey.Signer, 10, Principals)
	post := GenVerifySSHCert(s.T(), Data, cert, signer, IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"SSH_BROKEN","desc":"Ssh sign is broken: INVALID_CA"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestOkPss() {
	h := sha1.New()
	h.Write([]byte(Data))
	sign, err := rsa.SignPSS(rand.Reader, s.RSAKey.PrivateKey, crypto.SHA1, h.Sum(nil), nil)
	require.NoError(s.T(), err)

	post := GenVerifySSH(sign, IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equalf(s.T(), http.StatusOK, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"status":"OK","fingerprint":"8b:ca:b6:37:49:0f:53:2a:4d:3a:7a:39:30:12:26:05"}`,
		string(response.Body()),
	)
}

func AddAgentMeta(str []byte) []byte {
	LenSize := 4

	l := len(str)
	prefix := make([]byte, len(AgentRsaPrefix)+LenSize)
	copy(prefix, AgentRsaPrefix)
	str = append(prefix, str...)

	for i := 0; i < LenSize; i++ {
		str[len(AgentRsaPrefix)+LenSize-1-i] = byte((l >> (8 * i)) & 0xFF)
	}

	return str
}

func (s *ManualTestSuite) TestOkAgent() {
	sign, err := s.RSAKey.Signer.Sign(rand.Reader, []byte(Data))
	require.NoError(s.T(), err)

	post := GenVerifySSH(AddAgentMeta(sign.Blob), IDTypeUID)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equalf(s.T(), http.StatusOK, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"status":"OK","fingerprint":"8b:ca:b6:37:49:0f:53:2a:4d:3a:7a:39:30:12:26:05"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestWrongPssAgent() {
	h := sha1.New()
	h.Write([]byte(Data))
	sign, err := rsa.SignPSS(rand.Reader, s.RSAKey.PrivateKey, crypto.SHA1, h.Sum(nil), nil)
	require.NoError(s.T(), err)

	post := GenVerifySSH(AddAgentMeta(sign), IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equalf(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"SSH_BROKEN","desc":"Ssh sign is broken: None of the 1 sshkeys fit with 'sshagent' checker. fingerprints: '8b:ca:b6:37:49:0f:53:2a:4d:3a:7a:39:30:12:26:05'"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestWrongUID() {
	sign, err := s.RSAKey.Signer.Sign(rand.Reader, []byte(Data))
	require.NoError(s.T(), err)

	response, err := s.Client.R().
		SetFormData(map[string]string{
			"uid":      "123",
			"to_sign":  Data,
			"ssh_sign": base64.RawURLEncoding.EncodeToString(sign.Blob),
		}).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"SSH_BROKEN","desc":"Ssh sign is broken: No one ssh key found for uid 123"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestWrongLogin() {
	sign, err := s.RSAKey.Signer.Sign(rand.Reader, []byte(Data))
	require.NoError(s.T(), err)

	response, err := s.Client.R().
		SetFormData(map[string]string{
			"login":    "123",
			"to_sign":  Data,
			"ssh_sign": base64.RawURLEncoding.EncodeToString(sign.Blob),
		}).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"NO_SSH_KEY","desc":"Login not found"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadSign() {
	sign, err := s.RSAKey.Signer.Sign(rand.Reader, []byte(Data))
	require.NoError(s.T(), err)

	post := GenVerifySSH(sign.Blob[4:], IDTypeLogin)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"SSH_BROKEN","desc":"Ssh sign is broken: None of the 1 sshkeys fit with 'as-is' checker. fingerprints: '8b:ca:b6:37:49:0f:53:2a:4d:3a:7a:39:30:12:26:05'"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadID() {
	post := GenVerifySSHKey(s.T(), Data, s.RSAKey.Signer, IDTypeNone)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), http.StatusBadRequest, response.StatusCode(), FormatResponse(response))
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_REQUEST","error":"MISSING","desc":"Required 'login' OR 'uid'"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadID2() {
	post := GenVerifySSHKey(s.T(), Data, s.RSAKey.Signer, IDTypeBoth)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/verify_ssh")
	require.NoError(s.T(), err)

	require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_REQUEST","error":"MISSING","desc":"Required 'login' OR 'uid'"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestOkGrantTypeSSHKey() {
	post := GenGetTicketKey(s.T(), "27", "29", s.RSAKey.Signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)
	require.Equal(s.T(), response.StatusCode(), http.StatusOK)

	var data map[string]map[string]string
	require.NoError(s.T(), json.Unmarshal(response.Body(), &data))

	st := data["29"]["ticket"]

	checked, err := s.TVMClient29.CheckServiceTicket(context.Background(), st)
	require.NoError(s.T(), err)
	require.Equal(s.T(), tvm.UID(1120000000021014), checked.IssuerUID)
}

func (s *ManualTestSuite) TestOkGrantTypeSSHCert() {
	cert, signer := mockssh.MakeECDSACert(s.T(), s.ECDSAKey.Signer, s.CAKey.Signer, 10, Principals)
	post := GenGetTicketCert(s.T(), "27", "29", cert, signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)
	require.Equal(s.T(), response.StatusCode(), http.StatusOK)

	var data map[string]map[string]string
	require.NoError(s.T(), json.Unmarshal(response.Body(), &data))

	st := data["29"]["ticket"]

	checked, err := s.TVMClient29.CheckServiceTicket(context.Background(), st)
	require.NoError(s.T(), err)
	require.Equal(s.T(), tvm.UID(1120000000021014), checked.IssuerUID)
}

func (s *ManualTestSuite) TestBadSSHKeyNoRole() {
	post := GenGetTicketKey(s.T(), "29", "100500", s.RSAKey.Signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)

	require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"UID_NOT_ALLOWED","desc":"User 1120000000021014 does not have role 'TVM ssh user' for tvm_id=29: nobody can get it because tvm_id is not linked with any ABC service. You can link it with email to tvm-dev@yandex-team.ru"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadSSHCertNoRole() {
	cert, signer := mockssh.MakeECDSACert(s.T(), s.ECDSAKey.Signer, s.CAKey.Signer, 10, Principals)
	post := GenGetTicketCert(s.T(), "29", "100500", cert, signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)

	require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
	require.Equal(s.T(),
		`{"request_id":"","status":"ERR_CREDENTIALS","error":"UID_NOT_ALLOWED","desc":"User 1120000000021014 does not have role 'TVM ssh user' for tvm_id=29: nobody can get it because tvm_id is not linked with any ABC service. You can link it with email to tvm-dev@yandex-team.ru"}`,
		string(response.Body()),
	)
}

func (s *ManualTestSuite) TestBadSSHKeyNoSrc() {
	post := GenGetTicketKey(s.T(), "0", "100500", s.RSAKey.Signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)

	require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
}

func (s *ManualTestSuite) TestBadSSHCertNoSrc() {
	cert, signer := mockssh.MakeECDSACert(s.T(), s.ECDSAKey.Signer, s.CAKey.Signer, 10, Principals)
	post := GenGetTicketCert(s.T(), "0", "100500", cert, signer)
	response, err := s.Client.R().
		SetFormData(post).
		SetHeaders(s.Headers).
		Post("/2/ticket")
	require.NoError(s.T(), err)

	require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
}

func (s *ManualTestSuite) TestBadIntParams() {
	type reqestsData struct {
		param    string
		postData map[string]string
		message  string
	}

	postTS := GenGetTicketKey(s.T(), "27", "29", s.RSAKey.Signer)
	postTS["ts"] = "9999999999999999999" // rewrite ts with invalid value

	var requestsDataArr []reqestsData
	requestsDataArr = append(requestsDataArr, reqestsData{param: "ts", postData: postTS, message: "number"})
	requestsDataArr = append(requestsDataArr, reqestsData{param: "src", postData: GenGetTicketKey(s.T(), "9999999999999999999", "29", s.RSAKey.Signer), message: "number"})
	requestsDataArr = append(requestsDataArr, reqestsData{param: "src", postData: GenGetTicketKey(s.T(), "9999999999999999999", "29", s.RSAKey.Signer), message: "number"})
	requestsDataArr = append(requestsDataArr, reqestsData{param: "dst", postData: GenGetTicketKey(s.T(), "27", "9999999999999999999,123", s.RSAKey.Signer), message: "comma-separated array of numbers"})

	for _, data := range requestsDataArr {
		response, err := s.Client.R().
			SetFormData(data.postData).
			SetHeaders(s.Headers).
			Post("/2/ticket")
		require.NoError(s.T(), err)
		require.Equal(s.T(), response.StatusCode(), http.StatusBadRequest)
		expected := fmt.Sprintf(`{"request_id":"","status":"ERR_REQUEST","error":"INCORRECT.%s","desc":"Arg must be a %s: %s"}`, data.param, data.message, data.param)
		require.Equal(s.T(),
			expected,
			string(response.Body()),
		)
	}
}

func TestManualSuite(t *testing.T) {
	suite.Run(t, &ManualTestSuite{})
}
