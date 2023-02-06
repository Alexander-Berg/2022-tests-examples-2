package csp

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_keeper_GetCSP(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockcspParser
		cached       *models.CSP
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.CSP
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockcspParser {
					parser := NewMockcspParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.CSP{
						Nonce: "test",
					})
					return parser
				},
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.CSP{
				Nonce: "test",
			},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockcspParser {
					return nil
				},
				cached: &models.CSP{
					Nonce: "test",
				},
				cacheUpdated: false,
			},
			want: models.CSP{
				Nonce: "test",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				parser:       tt.fields.createParser(t),
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			assert.Equal(t, tt.want, k.GetCSP())
		})
	}
}
