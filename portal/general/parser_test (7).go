package csp

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		createDeviceGetter func(t *testing.T) *MockdeviceGetter
	}

	tests := []struct {
		name      string
		fields    fields
		wantEmpty bool
	}{
		{
			name: "get nil traits",
			fields: fields{
				createDeviceGetter: func(t *testing.T) *MockdeviceGetter {
					getter := NewMockdeviceGetter(gomock.NewController(t))
					getter.EXPECT().GetDevice().Return(models.Device{
						BrowserDesc: &models.BrowserDesc{
							Traits: nil,
						},
					})
					return getter
				},
			},
			wantEmpty: true,
		},
		{
			name: "csp version 1",
			fields: fields{
				createDeviceGetter: func(t *testing.T) *MockdeviceGetter {
					getter := NewMockdeviceGetter(gomock.NewController(t))
					getter.EXPECT().GetDevice().Return(models.Device{
						BrowserDesc: &models.BrowserDesc{
							Traits: map[string]string{
								"CSP1Support": "true",
							},
						},
					})
					return getter
				},
			},
			wantEmpty: true,
		},
		{
			name: "csp version 2",
			fields: fields{
				createDeviceGetter: func(t *testing.T) *MockdeviceGetter {
					getter := NewMockdeviceGetter(gomock.NewController(t))
					getter.EXPECT().GetDevice().Return(models.Device{
						BrowserDesc: &models.BrowserDesc{
							Traits: map[string]string{
								"CSP2Support": "true",
							},
						},
					})
					return getter
				},
			},
			wantEmpty: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				deviceGetter: tt.fields.createDeviceGetter(t),
				logger:       log3.NewLoggerStub(),
			}

			got := p.Parse()
			if tt.wantEmpty {
				assert.Empty(t, got)
			} else {
				assert.NotEmpty(t, got)
			}
		})
	}
}
