package domains

import (
	"strings"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
)

func Test_DomainConverter_DomainToGeo(t *testing.T) {
	tests := []struct {
		name          string
		domain        string
		spokCountryID uint32
		want          uint32
		wantFlag      bool
	}{
		{
			name:          "country from spok",
			domain:        "yandex.com.tr",
			spokCountryID: 983,
			want:          983,
			wantFlag:      true,
		},
		{
			name:          "country from local map",
			domain:        "yandex.by",
			spokCountryID: 0,
			want:          149,
			wantFlag:      true,
		},
		{
			name:          "yandex.ru",
			domain:        "yandex.ru",
			spokCountryID: 0,
			want:          0,
			wantFlag:      false,
		},
		{
			name:          "yandex.ua",
			domain:        "yandex.ua",
			spokCountryID: 0,
			want:          0,
			wantFlag:      false,
		},
		{
			name:          "some domain",
			domain:        "yandex.somedomain",
			spokCountryID: 0,
			want:          0,
			wantFlag:      false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			spokSettingsMock := NewMockspokSettings(ctrl)
			spokSettingsMock.EXPECT().CountryIDByDomain(strings.TrimPrefix(test.domain, yandexPrefix)).Return(test.spokCountryID).Times(1)

			d := NewDomainConverter(spokSettingsMock)

			res, flag := d.DomainToGeo(test.domain)

			assert.Equal(t, test.want, res)
			assert.Equal(t, test.wantFlag, flag)
		})
	}
}

func Test_DomainConverter_DomainToCity(t *testing.T) {
	tests := []struct {
		name       string
		domain     string
		spokCityID uint32
		want       uint32
		wantFlag   bool
	}{
		{
			name:       "city from spok",
			domain:     "yandex.com.tr",
			spokCityID: 11508,
			want:       11508,
			wantFlag:   true,
		},
		{
			name:       "city from local map",
			domain:     "yandex.by",
			spokCityID: 0,
			want:       157,
			wantFlag:   true,
		},
		{
			name:       "yandex.ru",
			domain:     "yandex.ru",
			spokCityID: 0,
			want:       0,
			wantFlag:   false,
		},
		{
			name:       "yandex.ua",
			domain:     "yandex.ua",
			spokCityID: 0,
			want:       0,
			wantFlag:   false,
		},
		{
			name:       "some domain",
			domain:     "yandex.somedomain",
			spokCityID: 0,
			want:       0,
			wantFlag:   false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			spokSettingsMock := NewMockspokSettings(ctrl)
			spokSettingsMock.EXPECT().CityIDByDomain(strings.TrimPrefix(test.domain, yandexPrefix)).Return(test.spokCityID).Times(1)

			d := NewDomainConverter(spokSettingsMock)

			res, flag := d.DomainToCity(test.domain)

			assert.Equal(t, test.want, res)
			assert.Equal(t, test.wantFlag, flag)
		})
	}
}
