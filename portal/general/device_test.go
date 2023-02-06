package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/library/go/yandex/uatraits"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewBrowserDesc(t *testing.T) {
	type args struct {
		dto *mordadata.BrowserDesc
	}

	tests := []struct {
		name string
		args args
		want *BrowserDesc
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "nil traits",
			args: args{
				dto: &mordadata.BrowserDesc{
					Traits:        nil,
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     []byte("user-agent"),
					Dpi:           1.5,
					Screen:        &mordadata.Screen{X: 2, Y: 1},
				},
			},
			want: &BrowserDesc{
				Traits:        nil,
				IsGramps:      true,
				IsTouchGramps: true,
				UserAgent:     "user-agent",
				DPI:           1.5,
				Screen:        Screen{X: 2, Y: 1},
			},
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.BrowserDesc{
					Traits: map[string]string{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: false,
					UserAgent:     []byte("user-agent"),
					Dpi:           1.5,
					Screen:        &mordadata.Screen{X: 2, Y: 1},
				},
			},
			want: &BrowserDesc{
				Traits: uatraits.Traits{
					"IsMobile": "true",
				},
				IsGramps:      true,
				IsTouchGramps: false,
				UserAgent:     "user-agent",
				DPI:           1.5,
				Screen:        Screen{X: 2, Y: 1},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewBrowserDesc(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestBrowserDesc_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *BrowserDesc
		want  *mordadata.BrowserDesc
	}{
		{
			name:  "nil browser desc",
			model: nil,
			want:  nil,
		},
		{
			name: "nil traits",
			model: &BrowserDesc{
				Traits:        nil,
				IsGramps:      true,
				IsTouchGramps: true,
				UserAgent:     "user-agent",
				DPI:           1.5,
				Screen:        Screen{X: 2, Y: 1},
			},
			want: &mordadata.BrowserDesc{
				Traits:        nil,
				IsGramps:      true,
				IsTouchGramps: true,
				UserAgent:     []byte("user-agent"),
				Dpi:           1.5,
				Screen:        &mordadata.Screen{X: 2, Y: 1},
			},
		},
		{
			name: "success",
			model: &BrowserDesc{
				Traits: uatraits.Traits{
					"IsMobile": "true",
				},
				IsGramps:      true,
				IsTouchGramps: false,
				UserAgent:     "user-agent",
				DPI:           1.5,
				Screen:        Screen{X: 2, Y: 1},
			},
			want: &mordadata.BrowserDesc{
				Traits: map[string]string{
					"IsMobile": "true",
				},
				IsGramps:      true,
				IsTouchGramps: false,
				UserAgent:     []byte("user-agent"),
				Dpi:           1.5,
				Screen:        &mordadata.Screen{X: 2, Y: 1},
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

func TestNewDevice(t *testing.T) {
	type args struct {
		dto *mordadata.Device
	}

	tests := []struct {
		name string
		args args
		want *Device
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
				dto: &mordadata.Device{
					BrowserDesc: &mordadata.BrowserDesc{
						Traits: map[string]string{
							"IsMobile": "true",
						},
						IsGramps:      true,
						IsTouchGramps: true,
						UserAgent:     []byte("user-agent"),
						Dpi:           1.5,
						Screen:        &mordadata.Screen{X: 2, Y: 1},
					},
				},
			},
			want: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     "user-agent",
					DPI:           1.5,
					Screen:        Screen{X: 2, Y: 1},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewDevice(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  *mordadata.Device
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     "user-agent",
					DPI:           1.5,
					Screen:        Screen{X: 2, Y: 1},
				},
			},
			want: &mordadata.Device{
				BrowserDesc: &mordadata.BrowserDesc{
					Traits: map[string]string{
						"IsMobile": "true",
					},
					IsGramps:      true,
					IsTouchGramps: true,
					UserAgent:     []byte("user-agent"),
					Dpi:           1.5,
					Screen:        &mordadata.Screen{X: 2, Y: 1},
				},
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

func TestDevice_GetTraits(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  uatraits.Traits
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: nil,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"IsMobile": "true",
					},
				},
			},
			want: uatraits.Traits{
				"IsMobile": "true",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetTraits()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_IsGramps(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  bool
	}{
		{
			name:  "nil model",
			model: nil,
			want:  false,
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: false,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					IsGramps: true,
				},
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.IsGramps()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_IsTouchGramps(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  bool
	}{
		{
			name:  "nil model",
			model: nil,
			want:  false,
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: false,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					IsTouchGramps: true,
				},
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.IsTouchGramps()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_GetUserAgent(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  string
	}{
		{
			name:  "nil model",
			model: nil,
			want:  "",
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: "",
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					UserAgent: "user-agent",
				},
			},
			want: "user-agent",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetUserAgent()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_GetDpi(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  float32
	}{
		{
			name:  "nil model",
			model: nil,
			want:  0,
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: 0,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					DPI: 1.5,
				},
			},
			want: 1.5,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetDPI()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_GetScaleFactor(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  float32
	}{
		{
			name:  "nil model",
			model: nil,
			want:  0,
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: 1,
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					DPI: 1.5,
				},
			},
			want: 1.5,
		},
		{
			name: "default",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					DPI: 0,
				},
			},
			want: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetScaleFactor()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_GetScreen(t *testing.T) {
	tests := []struct {
		name  string
		model *Device
		want  Screen
	}{
		{
			name:  "nil model",
			model: nil,
			want:  Screen{},
		},
		{
			name: "nil browser desc",
			model: &Device{
				BrowserDesc: nil,
			},
			want: Screen{},
		},
		{
			name: "success",
			model: &Device{
				BrowserDesc: &BrowserDesc{
					Screen: Screen{X: 2, Y: 5},
				},
			},
			want: Screen{X: 2, Y: 5},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetScreen()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_NewScreen(t *testing.T) {
	type args struct {
		dto *mordadata.Screen
	}

	tests := []struct {
		name string
		args args
		want Screen
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: Screen{},
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.Screen{
					X: 2,
					Y: 1,
				},
			},
			want: Screen{X: 2, Y: 1},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewScreen(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_IsAndroid(t *testing.T) {
	tests := []struct {
		name     string
		device   *Device
		wantFunc assert.BoolAssertionFunc
	}{
		{
			name:     "nil device",
			device:   nil,
			wantFunc: assert.False,
		},
		{
			name: "empty browser desc",
			device: &Device{
				BrowserDesc: nil,
			},
			wantFunc: assert.False,
		},
		{
			name: "empty traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: nil,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "no os in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "non-Android in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"OSFamily": "Windows",
					},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "Android in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"OSFamily": "Android",
					},
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.wantFunc(t, tt.device.IsAndroid())
		})
	}
}

func TestDevice_GetDTOScreen(t *testing.T) {
	tests := []struct {
		name  string
		model *BrowserDesc
		want  *mordadata.Screen
	}{
		{
			name:  "nil browser desc",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &BrowserDesc{
				Screen: Screen{
					X: 2,
					Y: 1,
				},
			},
			want: &mordadata.Screen{X: 2, Y: 1},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.GetDTOScreen()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDevice_IsIPhone(t *testing.T) {
	tests := []struct {
		name     string
		device   *Device
		wantFunc assert.BoolAssertionFunc
	}{
		{
			name:     "nil device",
			device:   nil,
			wantFunc: assert.False,
		},
		{
			name: "empty browser desc",
			device: &Device{
				BrowserDesc: nil,
			},
			wantFunc: assert.False,
		},
		{
			name: "empty traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: nil,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "no os in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "non-iOS in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"OSFamily": "Windows",
					},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "iPad in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"OSFamily": "iOS",
						"isTablet": "true",
					},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "iPhone in traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: uatraits.Traits{
						"OSFamily": "iOS",
						"isTablet": "false",
					},
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.wantFunc(t, tt.device.IsIPhone())
		})
	}
}

func TestDevice_IsIOS(t *testing.T) {
	type testCase struct {
		name     string
		device   *Device
		wantFunc assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name:     "nil device",
			device:   nil,
			wantFunc: assert.False,
		},
		{
			name: "nil traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: nil,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "not ios",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: map[string]string{
						"OSFamily": "Android",
					},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "ios",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: map[string]string{
						"OSFamily": "iOS",
					},
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			tt.wantFunc(t, tt.device.IsIOS())
		})
	}
}

func TestDevice_IsChromeMobile(t *testing.T) {
	type testCase struct {
		name     string
		device   *Device
		wantFunc assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name:     "nil device",
			device:   nil,
			wantFunc: assert.False,
		},
		{
			name: "nil traits",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: nil,
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "not chrome mobile",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: map[string]string{
						"BrowserName": "MobileFirefox",
					},
				},
			},
			wantFunc: assert.False,
		},
		{
			name: "chrome mobile",
			device: &Device{
				BrowserDesc: &BrowserDesc{
					Traits: map[string]string{
						"BrowserName": "ChromeMobile",
					},
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			tt.wantFunc(t, tt.device.IsChromeMobile())
		})
	}
}
