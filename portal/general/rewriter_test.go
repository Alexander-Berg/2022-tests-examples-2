package rewriter

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
)

func Test_keeper_GetMadmOptions(t *testing.T) {
	type args struct {
		options exports.Options
	}

	type fields struct {
		options map[string]string
	}

	tests := []struct {
		name   string
		args   args
		fields fields
		want   exports.Options
	}{
		{
			name: "Empty list of madm options get params",
			args: args{
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
			name: "news_degradation_title=title",
			args: args{
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
			fields: fields{
				options: map[string]string{"news_degradation_title": "title"},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "title",
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
			name: "disable_spok_domain_mordazone_allow=true",
			args: args{
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
			fields: fields{
				options: map[string]string{"disable_spok_domain_mordazone_allow": "true"},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: true,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
		{
			name: "disable_spok_domain_mordazone_allow=1",
			args: args{
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
			fields: fields{
				options: map[string]string{"disable_spok_domain_mordazone_allow": "1"},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: true,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
		{
			name: "disable_spok_domain_mordazone_allow",
			args: args{
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
			fields: fields{
				options: map[string]string{"disable_spok_domain_mordazone_allow": ""},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: true,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 2,
				},
			},
		},
		{
			name: "short_format_ios_version=1",
			args: args{
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
			fields: fields{
				options: map[string]string{"short_format_ios_version": "1"},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: false,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 1,
				},
			},
		},
		{
			name: "disable_spok_domain_mordazone_allow:short_format_ios_version=1",
			args: args{
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
			fields: fields{
				options: map[string]string{"disable_spok_domain_mordazone_allow": "", "short_format_ios_version": "1"},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "Degradation Title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: true,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 1,
				},
			},
		},
		{
			name: "disable_spok_domain_mordazone_allow=0:short_format_ios_version=3:news_degradation_title=title",
			args: args{
				options: exports.Options{
					Topnews: exports.TopnewsOptions{
						NewsDegradationTitle: "Degradation Title",
					},
					MordaZoneOptions: exports.MordaZoneOptions{
						DisableSpokDomainMordaZoneAllow: true,
					},
					ZenSetup: exports.ZenOptions{
						ShortFormatIOSVersionMin: 2,
					},
				},
			},
			fields: fields{
				options: map[string]string{
					"disable_spok_domain_mordazone_allow": "0",
					"short_format_ios_version":            "3",
					"news_degradation_title":              "title",
				},
			},
			want: exports.Options{
				Topnews: exports.TopnewsOptions{
					NewsDegradationTitle: "title",
				},
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: false,
				},
				ZenSetup: exports.ZenOptions{
					ShortFormatIOSVersionMin: 3,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := New()
			r.WithOptions(tt.fields.options)

			err := r.RewriteOptions(&tt.args.options)

			require.NoError(t, err)
			assert.Equal(t, tt.want, tt.args.options)
		})
	}
}
