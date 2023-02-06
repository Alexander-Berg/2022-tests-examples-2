package madmoptions

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
)

func Test_keeper_GetMadmOptions(t *testing.T) {
	type fields struct {
		options exports.Options
		request models.Request
	}

	tests := []struct {
		name   string
		fields fields
		want   exports.Options
	}{
		{
			name: "Empty list of madm options get params",
			fields: fields{
				options: exports.Options{
					Topnews: exports.TopnewsOptions{
						NewsDegradationTitle: "Degradation Title",
					},
					MordaZoneOptions: exports.MordaZoneOptions{
						DisableSpokDomainMordaZoneAllow: false,
					},
					ZenSetup: exports.ZenOptions{
						ShortFormatIOSVersionMin: 2,
					},
				},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: false,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
		{
			name: "GetMadmOptions params: is_internal=true",
			fields: fields{
				options: exports.Options{
					Topnews: exports.TopnewsOptions{
						NewsDegradationTitle: "Degradation Title",
					},
					MordaZoneOptions: exports.MordaZoneOptions{
						DisableSpokDomainMordaZoneAllow: false,
					},
					ZenSetup: exports.ZenOptions{
						ShortFormatIOSVersionMin: 2,
					},
				},
				request: models.Request{
					CGI: map[string][]string{
						"madm_options": {"disable_spok_domain_mordazone_allow=true"},
					},
					IsInternal: true,
				},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: false,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
		{
			name: "GetMadmOptions params: is_internal=false",
			fields: fields{
				options: exports.Options{
					Topnews: exports.TopnewsOptions{
						NewsDegradationTitle: "Degradation Title",
					},
					MordaZoneOptions: exports.MordaZoneOptions{
						DisableSpokDomainMordaZoneAllow: false,
					},
					ZenSetup: exports.ZenOptions{
						ShortFormatIOSVersionMin: 2,
					},
				},
				request: models.Request{
					CGI: map[string][]string{
						"madm_options": {"news_degradation_title=title"},
					},
					IsInternal: false,
				},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: false,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.fields.request).MaxTimes(2)

			rewriterMock := NewMockoptionsRewriter(ctrl)
			rewriterMock.EXPECT().RewriteOptions(gomock.Any()).Return(nil).MaxTimes(1)
			rewriterMock.EXPECT().WithOptions(gomock.Any()).Return().MaxTimes(1)

			k := &keeper{
				logger:          log3.NewLoggerStub(),
				requestGetter:   requestGetterMock,
				optionsRewriter: rewriterMock,
				madmOptions:     tt.fields.options,
			}

			actual := k.GetMadmOptions()

			assert.Equal(t, tt.want, actual)
		})
	}
}
