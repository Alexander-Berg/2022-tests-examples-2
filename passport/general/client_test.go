package tirole

import (
	"encoding/base64"
	"fmt"
	"net/http"
	"net/url"
	"testing"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmversion"
)

var ValidRoles = `{"revision":"GYYTKYZRMVSDC","born_date":1633427153,"tvm":{"11":{"/role/factors_by_number/":[{}]}}}`
var ValidRolesBlob = mustDecodeBase64URL(`G2EAAMSAeaV-eXIF1Zf4hA04cA_GhQahAQMPWXyoDOv6xYwGGuy2Lfy2y8IqN3QQCMksa6GxEs8LnMyKPIHz3qF9wbJA9xH6j2_HvL1nl0ND67__8f__Aw`)
var ValidRolesCodec = `1:brotli:98:2B0236B8E83B41F1ABD9042406A42D7E6728644904550ED914380FEA95F2F529`

func mustDecodeBase64URL(in string) []byte {
	out, err := base64.RawURLEncoding.DecodeString(in)
	if err != nil {
		panic(err)
	}
	return out
}

func TestTiroleCommon(t *testing.T) {
	httpClient := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodGet && req.URL.Path == "/v1/get_actual_roles" {
					if req.Header.Get("If-None-Match") == `"GYYTKYZRMVSDC"` {
						return nil, http.StatusNotModified, nil
					}
					return ValidRolesBlob, http.StatusOK, nil
				}

				return nil, http.StatusNotFound, nil
			},
			Headers: http.Header{
				"X-Tirole-Compression": []string{ValidRolesCodec},
			},
		},
	}

	tiroleClient := NewTirole(&url.URL{Scheme: "http", Host: "localhost:1"}, httpClient)
	roles, err := tiroleClient.GetRoles(
		"passportparmadev",
		"some_ticket",
		"",
	)
	require.NoError(t, err)
	require.NotNil(t, roles)
	require.EqualValues(t, ValidRoles, string(roles.GetRaw()))
	require.EqualValues(t, "GYYTKYZRMVSDC", roles.GetMeta().Revision)

	roles, err = tiroleClient.GetRoles(
		"passportparmadev",
		"some_ticket",
		"GYYTKYZRMVSDC",
	)
	require.NoError(t, err)
	require.Nil(t, roles)
}

func TestBuildRequest(t *testing.T) {
	tiroleClient := NewTirole(&url.URL{Scheme: "http", Host: "localhost:1"}, &http.Client{})

	req := tiroleClient.buildRequest("some&_slug", "some_&ticket", "")
	require.EqualValues(t,
		fmt.Sprintf("lib_version=%s&system_slug=some%%26_slug", tvmversion.GetVersion()),
		req.QueryParam.Encode(),
	)
	require.EqualValues(t,
		http.Header{
			"X-Ya-Service-Ticket": []string{"some_&ticket"},
		},
		req.Header,
	)

	req = tiroleClient.buildRequest("some&_slug", "some_&ticket", "some_revision")
	require.EqualValues(t,
		fmt.Sprintf("lib_version=%s&system_slug=some%%26_slug", tvmversion.GetVersion()),
		req.QueryParam.Encode(),
	)
	require.EqualValues(t,
		http.Header{
			"X-Ya-Service-Ticket": []string{"some_&ticket"},
			"If-None-Match":       []string{`"some_revision"`},
		},
		req.Header,
	)
}

func TestProcResponse(t *testing.T) {
	resp := &resty.Response{
		RawResponse: &http.Response{
			StatusCode: http.StatusNotModified,
			Header: http.Header{
				"X-Tirole-Compression": []string{"kek"},
			},
		},
	}
	blob, err := procResponse(resp, "")
	require.NoError(t, err)
	require.Nil(t, blob)

	resp.RawResponse.StatusCode = http.StatusNotFound
	_, err = procResponse(resp, "")
	require.EqualError(t, err, "HTTP code 404: ")

	resp.RawResponse.StatusCode = http.StatusOK
	_, err = procResponse(resp, "")
	require.EqualError(t, err, "failed to parse codec info from tirole: 'kek'. unknown codec format version; known: 1")

	delete(resp.RawResponse.Header, "X-Tirole-Compression")

	blob, err = procResponse(resp, "")
	require.NoError(t, err)
	require.Nil(t, blob)
}
