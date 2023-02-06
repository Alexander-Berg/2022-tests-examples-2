package config

import (
	yavcore "a.yandex-team.ru/library/go/yandex/yav"
	"a.yandex-team.ru/library/go/yandex/yav/httpyav"
	"a.yandex-team.ru/metrika/go/pkg/testlib"
	"a.yandex-team.ru/metrika/go/pkg/yav"
	"encoding/json"
	"encoding/xml"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type TestSecretConfig struct {
	Config
	MyStr    string   `xml:"my-str"`
	YavToken YavToken `xml:"yav-token"`
	MyToken  FromYav  `xml:"my-token"`
	MyInt    int      `xml:"my-int"`
	Creds    Nested   `xml:"creds"`
}

type Nested struct {
	Login    string  `xml:"name"`
	Password FromYav `xml:"password"`
}

func bootstrap() (*httptest.Server, *yav.Client) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		rsp := new(yavcore.GetVersionResponse)
		rsp.Status = yavcore.StatusOK
		rsp.Version = yavcore.Version{
			CreatedAt:    yavcore.Timestamp{Time: time.Now()},
			CreatedBy:    123,
			CreatorLogin: "qwerty",
			SecretName:   "secret",
			SecretUUID:   "sec-asdqwe",
			Values: []yavcore.Value{
				{
					Key:   "Key",
					Value: "Secret",
				},
				{
					Key:   "Pass",
					Value: "qwerty",
				},
			},
			VersionUUID: "ver-123",
		}
		body, _ := json.Marshal(rsp)

		_, _ = w.Write(body)
	}
	srv, _ := testlib.GetRestyBootstrap(handlerFunc)
	client, _ := yav.NewClientWithToken("")
	client.SetYavOptions(httpyav.WithHTTPHost(srv.URL))

	return srv, client
}

func TestParseSecretConfig(t *testing.T) {
	testCases := []struct {
		name      string
		rawConfig []byte
		parser    func([]byte, *TestSecretConfig) error
	}{
		{
			name: "test_xml",
			rawConfig: []byte(`
<yandex>
	<yav-token from-env="YAV_TOKEN" />
	<my-str>asd</my-str>
	<my-token from-yav="sec-asdqwe/Key" />
	<my-int>123</my-int>
	<creds>
		<name>login</name>
		<password from-yav="sec-asdqwe/Pass" />
	</creds>
</yandex>
			`),
			parser: func(rawConfig []byte, config *TestSecretConfig) error {
				return xml.Unmarshal(rawConfig, config)
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			_ = os.Setenv("YAV_TOKEN", "vault_token")
			var parsedConfig TestSecretConfig

			srv, client := bootstrap()
			defer srv.Close()
			SetYavClient(client)

			err := tc.parser(tc.rawConfig, &parsedConfig)
			require.NoError(t, err)

			assert.Equal(t, "asd", parsedConfig.MyStr)
			assert.Equal(t, 123, parsedConfig.MyInt)
			assert.Equal(t, "login", parsedConfig.Creds.Login)
			assert.Equal(t, "vault_token", string(parsedConfig.YavToken))
			assert.Equal(t, "Secret", string(parsedConfig.MyToken))
			assert.Equal(t, "qwerty", string(parsedConfig.Creds.Password))
			SetYavClient(nil)
			_ = os.Unsetenv("YAV_TOKEN")
		})
	}
}

func TestMarshalSecretConfig(t *testing.T) {
	testCases := []struct {
		name           string
		config         *FromEnv
		marshaler      func(*TestSecretConfig) ([]byte, error)
		expectedConfig string
	}{
		{
			name: "marshal_xml",
			marshaler: func(c *TestSecretConfig) ([]byte, error) {
				return xml.Marshal(c)
			},
			expectedConfig: "<yandex><my-str>asd</my-str><yav-token></yav-token><my-token>Secret</my-token><my-int>123</my-int><creds><name>login</name><password>qwerty</password></creds></yandex>",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			c := TestSecretConfig{
				MyStr:   "asd",
				MyToken: FromYav("Secret"),
				MyInt:   123,
				Creds: Nested{
					Login:    "login",
					Password: FromYav("qwerty"),
				},
			}

			result, err := tc.marshaler(&c)
			require.NoError(t, err)
			assert.Equal(t, tc.expectedConfig, string(result))
		})
	}
}
