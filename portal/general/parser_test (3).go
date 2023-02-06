package appinfo

import (
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parser_parseFromCGI(t *testing.T) {
	type args struct {
		cgi url.Values
	}

	tests := []struct {
		name string
		args args
		want models.AppInfo
	}{
		{
			name: "success",
			args: args{
				cgi: map[string][]string{
					"app_id":       {"ru.yandex.searchplugin"},
					"app_version":  {"78000000"},
					"app_platform": {"android"},
					"uuid":         {"123456789"},
					"did":          {"987654321"},
					"os_version":   {"15.3"},
				},
			},
			want: models.AppInfo{
				ID:        "ru.yandex.searchplugin",
				Version:   "78000000",
				Platform:  "android",
				UUID:      "123456789",
				DID:       "987654321",
				OSVersion: "15.3",
			},
		},
		{
			name: "did from deviceid",
			args: args{
				cgi: map[string][]string{
					"app_id":       {"ru.yandex.searchplugin"},
					"app_version":  {"78000000"},
					"app_platform": {"android"},
					"uuid":         {"123456789"},
					"deviceid":     {"987654321"},
					"os_version":   {"15.3"},
				},
			},
			want: models.AppInfo{
				ID:        "ru.yandex.searchplugin",
				Version:   "78000000",
				Platform:  "android",
				UUID:      "123456789",
				DID:       "987654321",
				OSVersion: "15.3",
			},
		},
		{
			name: "default platform",
			args: args{
				cgi: map[string][]string{
					"app_id":      {"ru.yandex.searchplugin"},
					"app_version": {"78000000"},
					"uuid":        {"123456789"},
					"deviceid":    {"987654321"},
					"os_version":  {"15.3"},
				},
			},
			want: models.AppInfo{
				ID:        "ru.yandex.searchplugin",
				Version:   "78000000",
				Platform:  "android",
				UUID:      "123456789",
				DID:       "987654321",
				OSVersion: "15.3",
			},
		},
		{
			name: "country and lang 1st case",
			args: args{
				cgi: map[string][]string{
					"lang": {"aa-bb_cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "aa",
				Country:  "cc",
			},
		},
		{
			name: "country and lang 1st case alt",
			args: args{
				cgi: map[string][]string{
					"lang": {"aA-bB_cC"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "aa",
				Country:  "cc",
			},
		},
		{
			name: "country and lang 2nd case",
			args: args{
				cgi: map[string][]string{
					"lang": {"bb_cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "bb",
				Country:  "cc",
			},
		},
		{
			name: "country and lang 2nd case alt",
			args: args{
				cgi: map[string][]string{
					"lang": {"bB_Cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "bb",
				Country:  "cc",
			},
		},
		{
			name: "lang 3rd case",
			args: args{
				cgi: map[string][]string{
					"lang": {"bB"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "bb",
			},
		},
		{
			name: "country",
			args: args{
				cgi: map[string][]string{
					"country": {"cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Country:  "cc",
			},
		},
		{
			name: "country alt",
			args: args{
				cgi: map[string][]string{
					"country": {"cC"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Country:  "cc",
			},
		},
		{
			name: "separate lang and country",
			args: args{
				cgi: map[string][]string{
					"lang":    {"bB"},
					"country": {"cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "bb",
				Country:  "cc",
			},
		},
		{
			name: "separate lang+country and country",
			args: args{
				cgi: map[string][]string{
					"lang":    {"bB_dd"},
					"country": {"cc"},
				},
			},
			want: models.AppInfo{
				Platform: "android",
				Lang:     "bb",
				Country:  "cc",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			assert.Equal(t, tt.want, p.parseFromCGI(tt.args.cgi))
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		createRequestKeeper   func(t *testing.T) *MockrequestKeeper
		createYaCookiesKeeper func(t *testing.T) *MockyaCookiesKeeper
	}
	tests := []struct {
		name   string
		fields fields
		want   models.AppInfo
	}{
		{
			name: "from cgi",
			fields: fields{
				createRequestKeeper: func(t *testing.T) *MockrequestKeeper {
					keeper := NewMockrequestKeeper(gomock.NewController(t))
					keeper.EXPECT().GetRequest().Return(models.Request{
						CGI: map[string][]string{
							"app_id":       {"ru.yandex.searchplugin"},
							"app_version":  {"78000000"},
							"app_platform": {"android"},
							"uuid":         {"123456789"},
							"did":          {"987654321"},
							"os_version":   {"15.3"},
						},
					})
					return keeper
				},
				createYaCookiesKeeper: func(t *testing.T) *MockyaCookiesKeeper {
					keeper := NewMockyaCookiesKeeper(gomock.NewController(t))
					keeper.EXPECT().GetYaCookies().Return(models.YaCookies{
						Ys: models.YCookie{
							Subcookies: map[string]models.YSubcookie{
								"uuid": {
									Name:  "uuid",
									Value: "111111",
								},
							},
						},
						Yp: models.YCookie{
							Subcookies: map[string]models.YSubcookie{
								"did": {
									Name:  "did",
									Value: "222222",
								},
							},
						},
					})
					return keeper
				},
			},
			want: models.AppInfo{
				ID:         "ru.yandex.searchplugin",
				Version:    "78000000",
				Platform:   "android",
				UUID:       "123456789",
				DID:        "987654321",
				UUIDHashed: 4054712127949633829,
				DIDHashed:  16797091784880995950,
				OSVersion:  "15.3",
			},
		},
		{
			name: "uuid and did from yacookie",
			fields: fields{
				createRequestKeeper: func(t *testing.T) *MockrequestKeeper {
					keeper := NewMockrequestKeeper(gomock.NewController(t))
					keeper.EXPECT().GetRequest().Return(models.Request{
						CGI: map[string][]string{
							"app_id":       {"ru.yandex.searchplugin"},
							"app_version":  {"78000000"},
							"app_platform": {"android"},
							"os_version":   {"15.3"},
						},
					})
					return keeper
				},
				createYaCookiesKeeper: func(t *testing.T) *MockyaCookiesKeeper {
					keeper := NewMockyaCookiesKeeper(gomock.NewController(t))
					keeper.EXPECT().GetYaCookies().Return(models.YaCookies{
						Ys: models.YCookie{
							Subcookies: map[string]models.YSubcookie{
								"uuid": {
									Name:  "uuid",
									Value: "111111",
								},
							},
						},
						Yp: models.YCookie{
							Subcookies: map[string]models.YSubcookie{
								"did": {
									Name:  "did",
									Value: "222222",
								},
							},
						},
					})
					return keeper
				},
			},
			want: models.AppInfo{
				ID:         "ru.yandex.searchplugin",
				Version:    "78000000",
				Platform:   "android",
				UUID:       "111111",
				DID:        "222222",
				UUIDHashed: 3222148057157265302,
				DIDHashed:  15717292333625364195,
				OSVersion:  "15.3",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				requestKeeper:   tt.fields.createRequestKeeper(t),
				yaCookiesKeeper: tt.fields.createYaCookiesKeeper(t),
			}
			got := p.Parse()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_processIDHashed(t *testing.T) {
	type args struct {
		id string
	}

	tests := []struct {
		name string
		args args
		want uint64
	}{
		{
			name: "id - test",
			args: args{
				id: "test",
			},
			want: 8346051122425466633,
		},
		{
			name: "id - 1 only",
			args: args{
				id: "11111111111111",
			},
			want: 13338667015825688039,
		},
		{
			name: "id - rnd",
			args: args{
				id: "128049812831278",
			},
			want: 9711917633825357890,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			assert.Equal(t, tt.want, p.processIDHashed(tt.args.id))
		})
	}
}
