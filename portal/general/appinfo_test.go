package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewAppInfo(t *testing.T) {
	type args struct {
		dto *mordadata.AppInfo
	}

	tests := []struct {
		name string
		args args
		want *AppInfo
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.AppInfo{
					Id:         []byte("ru.yandex.searchplugin"),
					Version:    []byte("78000000"),
					Platform:   []byte("android"),
					Uuid:       []byte("123456789"),
					Did:        []byte("987654321"),
					UuidHashed: 4054712127949633829,
					DidHashed:  16797091784880995950,
					OsVersion:  []byte("15.3"),
					Country:    []byte("ru"),
					Lang:       []byte("en"),
				},
			},
			want: &AppInfo{
				ID:         "ru.yandex.searchplugin",
				Version:    "78000000",
				Platform:   "android",
				UUID:       "123456789",
				DID:        "987654321",
				UUIDHashed: 4054712127949633829,
				DIDHashed:  16797091784880995950,
				OSVersion:  "15.3",
				Country:    "ru",
				Lang:       "en",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewAppInfo(tt.args.dto))
		})
	}
}

func TestAppInfo_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *AppInfo
		want  *mordadata.AppInfo
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &AppInfo{
				ID:         "ru.yandex.searchplugin",
				Version:    "78000000",
				Platform:   "android",
				UUID:       "123456789",
				DID:        "987654321",
				UUIDHashed: 4054712127949633829,
				DIDHashed:  16797091784880995950,
				OSVersion:  "15.3",
				Country:    "ru",
				Lang:       "en",
			},
			want: &mordadata.AppInfo{
				Id:         []byte("ru.yandex.searchplugin"),
				Version:    []byte("78000000"),
				Platform:   []byte("android"),
				Uuid:       []byte("123456789"),
				Did:        []byte("987654321"),
				UuidHashed: 4054712127949633829,
				DidHashed:  16797091784880995950,
				OsVersion:  []byte("15.3"),
				Country:    []byte("ru"),
				Lang:       []byte("en"),
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestAppInfo_IsAndroid(t *testing.T) {
	type fields struct {
		Platform string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "platform android",
			fields: fields{
				Platform: "android",
			},
			want: true,
		},
		{
			name: "platform apad",
			fields: fields{
				Platform: "apad",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Platform: "iphone",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &AppInfo{
				Platform: tt.fields.Platform,
			}

			assert.Equal(t, tt.want, a.IsAndroid())
		})
	}
}

func TestAppInfo_IsIOS(t *testing.T) {
	type fields struct {
		Platform string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "platform android",
			fields: fields{
				Platform: "iphone",
			},
			want: true,
		},
		{
			name: "platform apad",
			fields: fields{
				Platform: "ipad",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Platform: "android",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &AppInfo{
				Platform: tt.fields.Platform,
			}

			assert.Equal(t, tt.want, a.IsIOS())
		})
	}
}

func TestAppInfo_IsApad(t *testing.T) {
	type fields struct {
		Platform string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Platform: "apad",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Platform: "iphone",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &AppInfo{
				Platform: tt.fields.Platform,
			}

			assert.Equal(t, tt.want, a.IsApad())
		})
	}
}

func TestAppInfo_IsIpad(t *testing.T) {
	type fields struct {
		Platform string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Platform: "ipad",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Platform: "android",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &AppInfo{
				Platform: tt.fields.Platform,
			}

			assert.Equal(t, tt.want, a.IsIpad())
		})
	}
}

func TestAppInfo_IsWinPhone(t *testing.T) {
	type fields struct {
		Platform string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "platform wp",
			fields: fields{
				Platform: "wp",
			},
			want: true,
		},
		{
			name: "platform win_phone",
			fields: fields{
				Platform: "win_phone",
			},
			want: true,
		},

		{
			name: "failed",
			fields: fields{
				Platform: "iphone",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &AppInfo{
				Platform: tt.fields.Platform,
			}

			assert.Equal(t, tt.want, a.IsWinPhone())
		})
	}
}
