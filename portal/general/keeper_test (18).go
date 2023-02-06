package origin

import (
	"errors"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/cookies"
	"a.yandex-team.ru/portal/avocado/libs/utils/log2"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
	"a.yandex-team.ru/portal/avocado/proto/api"
)

func Test_keeper_GetOriginRequest(t *testing.T) {
	protoRequest := &protoanswers.THttpRequest{
		Method:  protoanswers.THttpRequest_Get,
		Scheme:  protoanswers.THttpRequest_Https,
		Path:    "/test",
		Headers: []*protoanswers.THeader{{Name: "Test", Value: "ooo"}, {Name: "Cookie", Value: "some=cookie;"}},
		Content: []byte(`smth that can not affect tests`),
	}
	apiRequest := &api.THttpRequest{
		Method:  api.THttpRequest_Get,
		Scheme:  api.THttpRequest_Https,
		Path:    []byte("/test"),
		Headers: []*api.THeader{{Name: []byte("Test"), Value: []byte("ooo")}, {Name: []byte("Cookie"), Value: []byte("some=cookie;")}},
		Content: []byte(`smth that can not affect tests`),
	}
	requestModel := &models.OriginRequest{
		Method: protoanswers.THttpRequest_Get,
		Scheme: protoanswers.THttpRequest_Https,
		Path:   "/test",
		Headers: map[string][]string{
			"Test":   {"ooo"},
			"Cookie": {"some=cookie;"},
		},
		Content: []byte(`smth that can not affect tests`),
	}
	type fields struct {
		cached       *models.OriginRequest
		cacheUpdated bool
	}
	tests := []struct {
		name      string
		fields    fields
		initMocks func(*Mockclient)
		want      *models.OriginRequest
		wantErr   bool
	}{
		{
			name: "Warm cache",
			fields: fields{
				cached:       models.NewOriginRequest(protoRequest),
				cacheUpdated: true,
			},
			initMocks: func(*Mockclient) {},
			want:      requestModel,
		},
		{
			name:   "Got data from apphost",
			fields: fields{},
			initMocks: func(client *Mockclient) {
				client.EXPECT().get().Return(protoRequest, nil).Times(1)
			},
			want: requestModel,
		},
		{
			name:   "Got data from apphost (getInBytes)",
			fields: fields{},
			initMocks: func(client *Mockclient) {
				client.EXPECT().get().Return(nil, errors.New("smth went wrong")).Times(1)
				client.EXPECT().getInBytes().Return(apiRequest, nil).Times(1)
			},
			want:    requestModel,
			wantErr: false,
		},
		{
			name:   "Got error from apphost",
			fields: fields{},
			initMocks: func(client *Mockclient) {
				client.EXPECT().get().Return(nil, errors.New("smth went wrong")).Times(1)
				client.EXPECT().getInBytes().Return(nil, errors.New("smth went wrong")).Times(1)
			},
			want:    nil,
			wantErr: true,
		},
		{
			name:   "Got empty http request from apphost",
			fields: fields{},
			initMocks: func(client *Mockclient) {
				client.EXPECT().get().Return(nil, nil).Times(1)
			},
			want:    nil,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			require.NoError(t, log2.Init(log2.WithStdout()))
			mockClient := NewMockclient(gomock.NewController(t))
			tt.initMocks(mockClient)

			k := &keeper{
				client:       mockClient,
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
				requestFixer: NewFixer(its.Options{}, cookies.NewParser()),
			}

			got, err := k.GetOriginRequest()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}
