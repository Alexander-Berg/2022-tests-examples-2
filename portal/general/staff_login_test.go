package stafflogin

import (
	"encoding/base64"
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parser_isStaffLogin(t *testing.T) {
	type fields struct {
		headers   http.Header
		authModel models.Auth
		authErr   error
	}

	type args struct {
		cgi        url.Values
		isInternal bool
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "Headers is empty",
			fields: fields{
				headers: map[string][]string{},
			},
			want: false,
		},
		{
			name: "Headers has exp split params, json is empty",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {base64.StdEncoding.EncodeToString([]byte(`{}`))},
				},
			},
			want: false,
		},
		{
			name: "Headers has exp split params, e flag is false",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {base64.StdEncoding.EncodeToString([]byte(`{"e": false}`))},
				},
			},
			want: false,
		},
		{
			name: "Headers has exp split params, e flag is true",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Expsplitparams": {base64.StdEncoding.EncodeToString([]byte(`{"e": true}`))},
				},
			},
			want: true,
		},
		{
			name: "From prod error, got 118 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjoyMTMsInMiOiJtb3JkYSIsImQiOiJkZXNrdG9wIiwibSI6IiIsImIiOiJDaHJvbWUiLCJpIjpmYWxzZSwibiI6InlhbmRleC5ydSIsImYiOiIifQ==`},
				},
			},
			want: false,
		},
		{
			name: "From prod error, got 130 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjoxMDc0NywicyI6Im1vcmRhIiwiZCI6ImRlc2t0b3AiLCJtIjoiIiwiYiI6IllhbmRleEJyb3dzZXIiLCJpIjpmYWxzZSwibiI6InlhbmRleC5ydSIsImYiOiIifQ==`},
				},
			},
			want: false,
		},
		{
			name: "From prod error, got 115 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjoyLCJzIjoibW9yZGEiLCJkIjoiZGVza3RvcCIsIm0iOiIiLCJiIjoiQ2hyb21lIiwiaSI6ZmFsc2UsIm4iOiJ5YW5kZXgucnUiLCJmIjoiIn0=`},
				},
			},
			want: false,
		},
		{
			name: "From prod error, got 126 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjo1MCwicyI6Im1vcmRhIiwiZCI6ImRlc2t0b3AiLCJtIjoiIiwiYiI6IllhbmRleEJyb3dzZXIiLCJpIjpmYWxzZSwibiI6InlhbmRleC5ydSIsImYiOiIifQ==`},
				},
			},
			want: false,
		},
		{
			name: "From prod error, got 131 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjoxMzc1OTYsInMiOiJtb3JkYSIsImQiOiJkZXNrdG9wIiwibSI6IiIsImIiOiJZYW5kZXhCcm93c2VyIiwiaSI6ZmFsc2UsIm4iOiJ5YW5kZXgucnUiLCJmIjoiIn0=`},
				},
			},
			want: false,
		},
		{
			name: "From prod error, got 122 byte error after base64 encoding",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-ExpSplitParams": {`eyJyIjoxMTkxODMsInMiOiJtb3JkYSIsImQiOiJkZXNrdG9wIiwibSI6IiIsImIiOiJTYWZhcmkiLCJpIjpmYWxzZSwibiI6InlhbmRleC5ydSIsImYiOiIifQ==`},
				},
			},
			want: false,
		},
		{
			name: "Header has autotest",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Autotest": {"1"},
				},
			},
			args: args{
				cgi: url.Values{
					"staff_login": {"1"},
				},
			},
			want: true,
		},
		{
			name: "Header has autotest without cgi",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Autotest": {"1"},
				},
			},
			want: false,
		},
		{
			name: "Staff cgi without autotest header",
			args: args{
				cgi: url.Values{
					"staff_login": {"1"},
				},
			},
			want: false,
		},
		{
			name: "Header has autotest not equal 1",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Autotest": {""},
				},
			},
			args: args{
				cgi: url.Values{
					"staff_login": {"1"},
				},
			},
			want: false,
		},
		{
			name: "Header has autotest with cgi not equal 1",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Autotest": {"1"},
				},
			},
			args: args{
				cgi: url.Values{
					"staff_login": {"0"},
				},
			},
			want: false,
		},
		{
			name: "Internal staff request",
			args: args{
				cgi: url.Values{
					"669": {"1"},
				},
				isInternal: true,
			},
			want: true,
		},
		{
			name: "Not internal staff request",
			args: args{
				cgi: url.Values{
					"669": {"1"},
				},
				isInternal: false,
			},
			want: false,
		},
		{
			name: "Internal not staff request",
			args: args{
				cgi: url.Values{
					"669": {""},
				},
				isInternal: true,
			},
			want: false,
		},
		{
			name: "by auth",
			fields: fields{
				authModel: models.Auth{
					UID:  "afadffads",
					Sids: map[string]string{"669": "11111"},
				},
				authErr: nil,
			},
			want: true,
		},
		{
			name: "by auth",
			fields: fields{
				authModel: models.Auth{
					UID:  "afadffads",
					Sids: map[string]string{"669": "11111"},
				},
				authErr: nil,
			},
			want: true,
		},
		{
			name: "by auth empty uid",
			fields: fields{
				authModel: models.Auth{
					UID:  "",
					Sids: map[string]string{"669": "11111"},
				},
				authErr: nil,
			},
			want: false,
		},
		{
			name: "by auth not exist sid669",
			fields: fields{
				authModel: models.Auth{
					UID:  "afadffads",
					Sids: map[string]string{"1": "11111"},
				},
				authErr: nil,
			},
			want: false,
		},
		{
			name: "by auth empty sid",
			fields: fields{
				authModel: models.Auth{
					UID: "afadffads",
				},
				authErr: nil,
			},
			want: false,
		},
		{
			name: "auth error",
			fields: fields{
				authModel: models.Auth{
					UID:  "afadffads",
					Sids: map[string]string{"669": "11111"},
				},
				authErr: assert.AnError,
			},
			want: false,
		},
		{
			name: "auth error with staff header",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Expsplitparams": {base64.StdEncoding.EncodeToString([]byte(`{"e": true}`))},
				},
				authModel: models.Auth{
					UID:  "afadffads",
					Sids: map[string]string{"669": "11111"},
				},
				authErr: assert.AnError,
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			authMock := NewMockauthGetter(ctrl)
			authMock.EXPECT().GetAuthOrErr().Return(tt.fields.authModel, tt.fields.authErr).MaxTimes(1)

			originRequestMock := NewMockoriginRequestGetter(ctrl)
			originRequestMock.EXPECT().GetOriginRequest().Return(
				&models.OriginRequest{
					Headers: tt.fields.headers,
				},
				nil,
			).MaxTimes(1)

			s := New(authMock, originRequestMock)
			got, err := s.IsStaffLogin(tt.args.cgi, tt.args.isInternal)

			require.NoError(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}
