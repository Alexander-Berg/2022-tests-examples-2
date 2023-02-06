package locales

import (
	"errors"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var langdetectDataPath = yatest.SourcePath("portal/avocado/libs/utils/langdetect/data/lang_detect_data.txt")

func Test_keeper_GetLocaleOrErr(t *testing.T) {
	type testCase struct {
		name              string
		initMocks         func(p *MocklocaleParser)
		cached            *models.Locale
		cacheUpdated      bool
		want              models.Locale
		wantCachedUpdated bool
		wantErr           bool
	}

	cases := []testCase{
		{
			name: "non-empty cache",
			cached: &models.Locale{
				Value: "uk",
			},
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "be"}, nil).Times(0)
			},
			cacheUpdated: false,
			want: models.Locale{
				Value: "uk",
			},
			wantErr:           false,
			wantCachedUpdated: false,
		},
		{
			name:         "empty cache, parser ok",
			cached:       nil,
			cacheUpdated: false,
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "uk"}, nil).Times(1)
			},
			want: models.Locale{
				Value: "uk",
			},
			wantErr:           false,
			wantCachedUpdated: true,
		},
		{
			name:         "empty cache, parser fails",
			cached:       nil,
			cacheUpdated: false,
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "uk"}, errors.New("some parsing error")).Times(1)
			},
			want: models.Locale{
				Value: "uk",
			},
			wantErr:           true,
			wantCachedUpdated: true,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			localeParserMock := NewMocklocaleParser(ctrl)
			tt.initMocks(localeParserMock)

			k := &keeper{
				logger: log3.NewLoggerStub(),
				parser: localeParserMock,
				cached: tt.cached,
			}
			actual, err := k.GetLocaleOrErr()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, actual)
			}
			assert.Equal(t, tt.wantCachedUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetLocale(t *testing.T) {
	type testCase struct {
		name      string
		initMocks func(p *MocklocaleParser)
		cached    *models.Locale
		want      models.Locale
	}

	cases := []testCase{
		{
			name: "non-empty cache",
			cached: &models.Locale{
				Value: "uk",
			},
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "be"}, nil).Times(0)
			},
			want: models.Locale{
				Value: "uk",
			},
		},
		{
			name:   "empty cache, parser ok",
			cached: nil,
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "uk"}, nil).Times(1)
			},
			want: models.Locale{
				Value: "uk",
			},
		},
		{
			name:   "empty cache, parser fails",
			cached: nil,
			initMocks: func(p *MocklocaleParser) {
				p.EXPECT().Parse().Return(models.Locale{Value: "uk"}, errors.New("some parsing error")).Times(1)
			},
			want: models.Locale{
				Value: "uk",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			localeParserMock := NewMocklocaleParser(ctrl)
			tt.initMocks(localeParserMock)

			k := &keeper{
				logger: log3.NewLoggerStub(),
				parser: localeParserMock,
				cached: tt.cached,
			}
			actual := k.GetLocale()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_keeper_GetLocaleIfUpdated(t *testing.T) {
	type testCase struct {
		name         string
		cached       *models.Locale
		cacheUpdated bool
		want         *morda_data.Lang
	}

	cases := []testCase{
		{
			name:         "cache is updated, but nil",
			cached:       nil,
			cacheUpdated: true,
			want:         nil,
		},
		{
			name: "cache is updated, empty value",
			cached: &models.Locale{
				Value: "",
			},
			cacheUpdated: true,
			want:         &morda_data.Lang{Locale: make([]byte, 0)},
		},
		{
			name: "cache is updated, regular value",
			cached: &models.Locale{
				Value: "uk",
			},
			cacheUpdated: true,
			want: &morda_data.Lang{
				Locale: []byte("uk"),
			},
		},
		{
			name: "cache is not updated",
			cached: &models.Locale{
				Value: "uk",
			},
			cacheUpdated: false,
			want:         nil,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				parser:       nil,
				cached:       tt.cached,
				cacheUpdated: tt.cacheUpdated,
			}
			actual := k.GetLocaleIfUpdated()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_keeper_ForceLocale(t *testing.T) {
	type fields struct {
		cached       *models.Locale
		cacheUpdated bool
	}
	type args struct {
		locale models.Locale
	}
	tests := []struct {
		name        string
		fields      fields
		args        args
		wantCache   *models.Locale
		wantUpdated bool
	}{
		{
			name: "update cache",
			fields: fields{
				cached: &models.Locale{
					Value: "ru",
				},
				cacheUpdated: false,
			},
			args: args{
				locale: models.Locale{
					Value: "en",
				},
			},
			wantCache: &models.Locale{
				Value: "en",
			},
			wantUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			k.ForceLocale(tt.args.locale)
			assert.Equal(t, tt.wantCache, k.cached)
			assert.Equal(t, tt.wantUpdated, k.cacheUpdated)
		})
	}
}
