package tiroleinternal

import (
	"bytes"
	"encoding/base64"
	"io"
	"io/ioutil"
	"net/http"
	"strings"
	"testing"

	"github.com/andybalholm/brotli"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/internal/reqs"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/internal/ytc"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/keys"
)

type badBody struct {
}

func (t *badBody) Read(p []byte) (n int, err error) {
	return 0, xerrors.Errorf("kek")
}

func (t *badBody) Close() error {
	return xerrors.Errorf("kek")
}

func TestParseUploadRolesRequest(t *testing.T) {
	CTJson := http.Header{
		echo.HeaderContentType: []string{echo.MIMEApplicationJSONCharsetUTF8},
	}

	cases := []struct {
		Headers http.Header
		Body    string
		Err     string
		Req     reqs.UploadRoles
	}{
		{
			Err: "Only JSON allowed as request, got Content-Type: ''",
		},
		{
			Headers: CTJson,
			Body:    `[`,
			Err:     "Failed to unmarshal request body as JSON",
		},
		{
			Headers: CTJson,
			Body:    `{"some_field":123}`,
			Err:     "Failed to validate request body",
		},
		{
			Headers: CTJson,
			Body:    `{"system_slug":"foo","roles":{"revision": 1612791975,"born_date": 1612791975}}`,
			Req: reqs.UploadRoles{
				SystemSlug: "foo",
				Roles: reqs.Roles{
					Revision: 1612791975,
					BornDate: 1612791975,
				},
			},
		},
		{
			Headers: CTJson,
			Body:    `{"system_slug":"foo","roles":{"revision": 161,"born_date": 164,"tvm":{"1":{"kek":[]}}}}`,
			Req: reqs.UploadRoles{
				SystemSlug: "foo",
				Roles: reqs.Roles{
					Revision: 161,
					BornDate: 164,
					Tvm: &reqs.Consumers{
						"1": {"kek": {}},
					},
				},
			},
		},
	}

	for idx, c := range cases {
		e := echo.New()
		req := &http.Request{
			Header:        c.Headers,
			Body:          ioutil.NopCloser(strings.NewReader(c.Body)),
			ContentLength: int64(len(c.Body)),
		}
		wr := &testRespWriter{}
		ctx := e.NewContext(req, wr)

		r, err := ParseUploadRolesRequest(ctx)
		if c.Err == "" {
			require.NoError(t, err, idx)
			require.NotNil(t, r, idx)
			require.Equal(t, *r, c.Req)
		} else {
			require.Error(t, err, idx)
			require.Contains(t, err.Error(), c.Err, idx)
			_, ok := err.(*errs.InvalidRequestError)
			require.True(t, ok)
			require.Nil(t, r, idx)
		}
	}
}

func TestParseUploadRolesRequest_BadBody(t *testing.T) {
	e := echo.New()
	req := &http.Request{
		Header: http.Header{
			echo.HeaderContentType: []string{echo.MIMEApplicationJSONCharsetUTF8},
		},
		Body:          &badBody{},
		ContentLength: 100,
	}
	wr := &testRespWriter{}
	ctx := e.NewContext(req, wr)
	_, err := ParseUploadRolesRequest(ctx)

	require.Error(t, err)
	require.Contains(t, err.Error(), "Failed to fetch request body")
}

func TestPrepareYtReq(t *testing.T) {
	req := &reqs.UploadRoles{
		SystemSlug: "foo",
		Roles: reqs.Roles{
			Revision: 789,
			BornDate: 456,
			Tvm: &reqs.Consumers{
				"42": reqs.ConsumerRoles{
					"bar": []reqs.Entry{
						{"kek": "lol"},
						{"scope": "/"},
					},
				},
			},
		},
	}

	keyMap, err := keys.CreateKeyMap("Q", "aabbccddeeff")
	require.NoError(t, err)

	res, err := PrepareYtReq(req, keyMap)
	require.NoError(t, err)

	// _, _ = fmt.Fprintf(os.Stderr, "%s", base64.RawURLEncoding.EncodeToString(res.Blob))
	encoded, err := base64.RawURLEncoding.DecodeString(
		"G1YAAAS-n1vqL38YyDRcKAaxWUTEZNrEIpbPgUMOHG7NA4RjGmyMTccVql2TGQ0xr_u2EITLpZuojlPw_Q9K6gBXkkNH0u6G6G_HkTQmiIJP2w",
	)
	require.NoError(t, err)

	expectedJSON := `{"revision":"GMYTK","born_date":456,"tvm":{"42":{"bar":[{"kek":"lol"},{"scope":"/"}]}}}`

	decoded := make([]byte, len(expectedJSON))
	r := brotli.NewReader(bytes.NewBuffer(res.Blob))
	_, err = io.ReadFull(r, decoded)
	require.NoError(t, err)
	require.Equal(t, expectedJSON, string(decoded))

	expected := &ytc.UploadRolesReq{
		Slug:     "foo",
		Revision: 9223372036854775018,
		Meta: ytc.UploadRolesMetaReq{
			Unixtime:      456,
			Codec:         "brotli",
			DecodedSize:   87,
			DecodedSha256: "7CA5FFA795665D09962BC6C1E42D6561D21D0A45358363FAA3CA35F3D34012DA",
			EncodedHmac:   "Q:8898738442151be4a0a3634f7cb1cf303e97de53ef29ac81b4a19bb529bb7a9b",
			RevisionExt:   "GMYTK",
			Revision:      789,
			Borndate:      "1970-01-01 03:07:36 +0300 MSK",
		},
		Blob: encoded,
	}

	require.Equal(t, *expected, *res)
}

func TestReverseRevision(t *testing.T) {
	require.Equal(t, uint64(9223372036854775807), reverseRevision(0))
	require.Equal(t, uint64(9223372036854675307), reverseRevision(100500))
	require.Equal(t, uint64(9223372035240261985), reverseRevision(1614513822))
}

func TestMakeRevisionExternal(t *testing.T) {
	require.Equal(t, "GA", makeRevisionExternal(0))
	require.Equal(t, "MZTA", makeRevisionExternal(255))
	require.Equal(t, "GE4DQOJU", makeRevisionExternal(100500))
	require.Equal(t, "GYYDGYRYGY4WK", makeRevisionExternal(1614513822))
	require.Equal(t, "GYYDGYRYGZQTC", makeRevisionExternal(1614513825))
	require.Equal(t, "GYYTQYRWGRSWC", makeRevisionExternal(1636525290))
}
