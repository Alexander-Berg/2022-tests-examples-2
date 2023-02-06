package main

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os/exec"
	"syscall"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
	"github.com/stripe/krl"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/tvmcert"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/utils"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mockskotty"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mockssh"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/mock/mocktvmcert"
)

const (
	User1 = "user1"
	User2 = "user2"
	User3 = "user3"
)

var Principals = []string{User1, User2}

type APITestTestSuite struct {
	suite.Suite
	Skotty  *httptest.Server
	Tvmcert *exec.Cmd
	Client  *resty.Client
	Keys    []mockssh.ECDSAKeyPair
}

func (s *APITestTestSuite) BeforeTest(string, string) {}

func (s *APITestTestSuite) AfterTest(string, string) {}

func (s *APITestTestSuite) SetupSuite() {
	s.Keys = mockssh.GenerateKeys(s.T(), 4)
	var skottyURL string

	s.Skotty, skottyURL = mockskotty.New(s.T(), s.Keys, &krl.KRL{
		GeneratedDate: uint64(time.Now().Unix()),
		Version:       1,
		Sections: []krl.KRLSection{
			&krl.KRLCertificateSection{
				CA: s.Keys[0].PublicKey,
				Sections: []krl.KRLCertificateSubsection{
					&krl.KRLCertificateKeyID{"10", "11"},
				},
			},
			&krl.KRLCertificateSection{
				CA: s.Keys[3].PublicKey,
				Sections: []krl.KRLCertificateSubsection{
					&krl.KRLCertificateKeyID{"12", "13"},
				},
			},
		},
	})

	var tvmcertURL string
	s.Tvmcert, tvmcertURL = mocktvmcert.New(
		s.T(), mocktvmcert.MakeConfig(s.T(), skottyURL))
	s.Client = resty.New().SetBaseURL(tvmcertURL)
}

func (s *APITestTestSuite) TearDownSuite() {
	s.Skotty.Close()
	s.T().Logf("trying to shutdown daemon gracefully (%s)...", s.Tvmcert.Process.Signal(syscall.SIGINT))
	time.AfterFunc(5*time.Second, func() {
		s.T().Logf("killing daemon (%s)...", s.Tvmcert.Process.Kill())
	})
	s.T().Logf("daemon shutdown (%s)", s.Tvmcert.Wait())
}

func (s *APITestTestSuite) SetupTest() {}

func (s *APITestTestSuite) TestPing() {
	response, err := s.Client.R().Get("/ping")
	require.NoError(s.T(), err)
	require.Equal(s.T(), http.StatusOK, response.StatusCode())
	require.Equal(s.T(), []byte{}, response.Body())
}

func (s *APITestTestSuite) TestHealthCheck() {
	response, err := s.Client.R().Get("/healthcheck")
	require.NoError(s.T(), err)
	require.Equal(s.T(), http.StatusOK, response.StatusCode())
	require.Equal(s.T(), "0;OK", string(response.Body()))
}

func (s *APITestTestSuite) CheckVerify(
	cert ssh.PublicKey, signer ssh.Signer,
	username string, data string,
	statusCode int, status tvmcert.Status, message string,
) {
	formatResponse := func(response *resty.Response) string {
		return fmt.Sprintf("[%d] %s", response.StatusCode(), response.Body())
	}

	sign, err := signer.Sign(rand.Reader, []byte(data))
	require.NoError(s.T(), err)

	response, err := s.Client.R().SetFormData(map[string]string{
		"username":    username,
		"data":        data,
		"request_id":  "test",
		"certificate": base64.RawURLEncoding.EncodeToString(cert.Marshal()),
		"sign":        base64.RawURLEncoding.EncodeToString(sign.Blob),
	}).Post("/1/verify")

	require.NoError(s.T(), err)
	require.Equalf(s.T(), statusCode, response.StatusCode(), formatResponse(response))
	result := tvmcert.VerificationStatus{}
	require.NoErrorf(s.T(), json.Unmarshal(response.Body(), &result), formatResponse(response))
	require.Equalf(s.T(), status, result.Status, formatResponse(response))
	require.Containsf(s.T(), result.Message, message, formatResponse(response))
}

func (s *APITestTestSuite) Test1Verify1() {
	key := mockssh.GenECDSAKey(s.T())
	cert, signer := mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[2].Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[2].Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User2, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User2, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)
}

func (s *APITestTestSuite) Test1Verify2() {
	key := mockssh.GenECDSAKey(s.T())
	cert, signer := mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User3, "1645024442|123|321",
		400, tvmcert.InvalidCert, "principal \"user3\" not in the set of valid principals",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	cert.CertType = ssh.HostCert
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCertType, "invalid certificate type",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	cert.Key = s.Keys[0].PublicKey
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: certificate signature does not verify",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	cert.ValidAfter = uint64(time.Now().Add(24 * time.Hour).Unix())
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: cert is not yet valid",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	cert.ValidBefore = uint64(-time.Now().Add(24 * time.Hour).Unix())
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: cert has expired",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, key.Signer, 1001, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCA, "not user authority",
	)

	s.CheckVerify(
		key.PublicKey, key.Signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidType, "not a certificate",
	)

	badKey := mockssh.GenECDSAKey(s.T())
	cert, _ = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 1001, Principals)
	s.CheckVerify(
		cert, badKey.Signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidSignature, "ssh: signature did not verify",
	)
}

func (s *APITestTestSuite) Test1Verify3() {
	key := mockssh.GenECDSAKey(s.T())
	cert, signer := mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 10, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: certificate serial 10 revoked",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 11, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: certificate serial 11 revoked",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 12, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[0].Signer, 13, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[3].Signer, 10, Principals)
	s.CheckVerify(
		cert, signer,
		User2, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[3].Signer, 11, Principals)
	s.CheckVerify(
		cert, signer,
		User2, "1645024442|123|321",
		200, tvmcert.Ok, "",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[3].Signer, 12, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: certificate serial 12 revoked",
	)

	cert, signer = mockssh.MakeECDSACert(s.T(), key.Signer, s.Keys[3].Signer, 13, Principals)
	s.CheckVerify(
		cert, signer,
		User1, "1645024442|123|321",
		400, tvmcert.InvalidCert, "ssh: certificate serial 13 revoked",
	)
}

func TestApiSuite(t *testing.T) {
	defer utils.SkipYaTest(t)
	suite.Run(t, &APITestTestSuite{})
}
