package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewYaCookies(t *testing.T) {
	type args struct {
		dto *mordadata.YaCookies
	}
	tests := []struct {
		name string
		args args
		want *YaCookies
	}{
		{
			name: "DTO is nil",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "with DTO",
			args: args{
				dto: &mordadata.YaCookies{
					YandexGid: 123,
					Yp: &mordadata.YCookie{
						RawString: []byte("100.fruit.apple#300.city.moscow"),
						Subcookies: map[string]*mordadata.YSubcookie{
							"fruit": {
								Name:   []byte("fruit"),
								Value:  []byte("apple"),
								Expire: 100,
							},
							"city": {
								Name:   []byte("city"),
								Value:  []byte("moscow"),
								Expire: 300,
							},
						},
					},
					Ys: &mordadata.YCookie{
						RawString: []byte("show_morda.yes#some_flag.1"),
						Subcookies: map[string]*mordadata.YSubcookie{
							"show_morda": {
								Name:  []byte("show_morda"),
								Value: []byte("yes"),
							},
							"some_flag": {
								Name:  []byte("some_flag"),
								Value: []byte("1"),
							},
						},
					},
					YandexUid:            []byte("1234567890123456"),
					YandexUidSalted:      42,
					IsYandexUidGenerated: true,
					SessionId:            []byte("SomeRandomString1"),
					SessionId2:           []byte("SomeRandomString2"),
				},
			},
			want: &YaCookies{
				YandexGID: 123,
				Yp: YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:            "1234567890123456",
				YandexUIDSalted:      42,
				IsYandexUIDGenerated: true,
				SessionID:            "SomeRandomString1",
				SessionID2:           "SomeRandomString2",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewYaCookies(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestYaCookies_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *YaCookies
		want  *mordadata.YaCookies
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "with Model",
			model: &YaCookies{
				YandexGID: 123,
				Yp: YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:            "1234567890123456",
				YandexUIDSalted:      42,
				IsYandexUIDGenerated: true,
				SessionID:            "SomeRandomString1",
				SessionID2:           "SomeRandomString2",
			},
			want: &mordadata.YaCookies{
				YandexGid: 123,
				Yp: &mordadata.YCookie{
					RawString: []byte("100.fruit.apple#300.city.moscow"),
					Subcookies: map[string]*mordadata.YSubcookie{
						"fruit": {
							Name:   []byte("fruit"),
							Value:  []byte("apple"),
							Expire: 100,
						},
						"city": {
							Name:   []byte("city"),
							Value:  []byte("moscow"),
							Expire: 300,
						},
					},
				},
				Ys: &mordadata.YCookie{
					RawString: []byte("show_morda.yes#some_flag.1"),
					Subcookies: map[string]*mordadata.YSubcookie{
						"show_morda": {
							Name:  []byte("show_morda"),
							Value: []byte("yes"),
						},
						"some_flag": {
							Name:  []byte("some_flag"),
							Value: []byte("1"),
						},
					},
				},
				YandexUid:            []byte("1234567890123456"),
				YandexUidSalted:      42,
				IsYandexUidGenerated: true,
				SessionId:            []byte("SomeRandomString1"),
				SessionId2:           []byte("SomeRandomString2"),
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

func TestNewYCookie(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.YCookie
		want YCookie
	}{
		{
			name: "DTO is nil",
			dto:  nil,
			want: YCookie{},
		},
		{
			name: "with DTO YCookie ys",
			dto: &mordadata.YCookie{
				RawString: []byte("show_morda.yes#some_flag.1"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"show_morda": {
						Name:  []byte("show_morda"),
						Value: []byte("yes"),
					},
					"some_flag": {
						Name:  []byte("some_flag"),
						Value: []byte("1"),
					},
				},
			},
			want: YCookie{
				RawString: "show_morda.yes#some_flag.1",
				Subcookies: map[string]YSubcookie{
					"show_morda": {
						Name:  "show_morda",
						Value: "yes",
					},
					"some_flag": {
						Name:  "some_flag",
						Value: "1",
					},
				},
			},
		},
		{
			name: "with DTO YCookie yp",
			dto: &mordadata.YCookie{
				RawString: []byte("100.fruit.apple#300.city.moscow"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"fruit": {
						Name:   []byte("fruit"),
						Value:  []byte("apple"),
						Expire: 100,
					},
					"city": {
						Name:   []byte("city"),
						Value:  []byte("moscow"),
						Expire: 300,
					},
				},
			},
			want: YCookie{
				RawString: "100.fruit.apple#300.city.moscow",
				Subcookies: map[string]YSubcookie{
					"fruit": {
						Name:   "fruit",
						Value:  "apple",
						Expire: 100,
					},
					"city": {
						Name:   "city",
						Value:  "moscow",
						Expire: 300,
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewYCookie(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestYCookie_DTO_Ys(t *testing.T) {
	tests := []struct {
		name  string
		model *YaCookies
		want  *mordadata.YCookie
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "with Model YCookie Ys ver1",
			model: &YaCookies{
				YandexGID: 123,
				Yp: YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:  "1234567890123456",
				SessionID:  "SomeRandomString1",
				SessionID2: "SomeRandomString2",
			},
			want: &mordadata.YCookie{
				RawString: []byte("show_morda.yes#some_flag.1"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"show_morda": {
						Name:  []byte("show_morda"),
						Value: []byte("yes"),
					},
					"some_flag": {
						Name:  []byte("some_flag"),
						Value: []byte("1"),
					},
				},
			},
		},
		{
			name: "with Model YCookie Ys ver2",
			model: &YaCookies{
				YandexGID: 321,
				Yp: YCookie{
					RawString: "200.fruit.peach#400.city.sochi#600.car.volvo",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "peach",
							Expire: 200,
						},
						"city": {
							Name:   "city",
							Value:  "sochi",
							Expire: 400,
						},
						"car": {
							Name:   "car",
							Value:  "volvo",
							Expire: 600,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#another_flag.0",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"another_flag": {
							Name:  "some_flag",
							Value: "0",
						},
					},
				},
				YandexUID:  "6543210987654321",
				SessionID:  "AnotherRandomString1",
				SessionID2: "AnotherRandomString2",
			},
			want: &mordadata.YCookie{
				RawString: []byte("show_morda.yes#another_flag.0"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"show_morda": {
						Name:  []byte("show_morda"),
						Value: []byte("yes"),
					},
					"another_flag": {
						Name:  []byte("some_flag"),
						Value: []byte("0"),
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.getYsDTOYCookie()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestYCookie_DTO_Yp(t *testing.T) {
	tests := []struct {
		name  string
		model *YaCookies
		want  *mordadata.YCookie
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "with Model YCookie Yp ver1",
			model: &YaCookies{
				YandexGID: 123,
				Yp: YCookie{
					RawString: "100.fruit.apple#300.city.moscow",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "apple",
							Expire: 100,
						},
						"city": {
							Name:   "city",
							Value:  "moscow",
							Expire: 300,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#some_flag.1",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"some_flag": {
							Name:  "some_flag",
							Value: "1",
						},
					},
				},
				YandexUID:  "1234567890123456",
				SessionID:  "SomeRandomString1",
				SessionID2: "SomeRandomString2",
			},
			want: &mordadata.YCookie{
				RawString: []byte("100.fruit.apple#300.city.moscow"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"fruit": {
						Name:   []byte("fruit"),
						Value:  []byte("apple"),
						Expire: 100,
					},
					"city": {
						Name:   []byte("city"),
						Value:  []byte("moscow"),
						Expire: 300,
					},
				},
			},
		},
		{
			name: "with Model YCookie Yp ver2",
			model: &YaCookies{
				YandexGID: 321,
				Yp: YCookie{
					RawString: "200.fruit.peach#400.city.sochi#600.car.volvo",
					Subcookies: map[string]YSubcookie{
						"fruit": {
							Name:   "fruit",
							Value:  "peach",
							Expire: 200,
						},
						"city": {
							Name:   "city",
							Value:  "sochi",
							Expire: 400,
						},
						"car": {
							Name:   "car",
							Value:  "volvo",
							Expire: 600,
						},
					},
				},
				Ys: YCookie{
					RawString: "show_morda.yes#another_flag.0",
					Subcookies: map[string]YSubcookie{
						"show_morda": {
							Name:  "show_morda",
							Value: "yes",
						},
						"another_flag": {
							Name:  "some_flag",
							Value: "0",
						},
					},
				},
				YandexUID:  "6543210987654321",
				SessionID:  "AnotherRandomString1",
				SessionID2: "AnotherRandomString2",
			},
			want: &mordadata.YCookie{
				RawString: []byte("200.fruit.peach#400.city.sochi#600.car.volvo"),
				Subcookies: map[string]*mordadata.YSubcookie{
					"fruit": {
						Name:   []byte("fruit"),
						Value:  []byte("peach"),
						Expire: 200,
					},
					"city": {
						Name:   []byte("city"),
						Value:  []byte("sochi"),
						Expire: 400,
					},
					"car": {
						Name:   []byte("car"),
						Value:  []byte("volvo"),
						Expire: 600,
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.getYpDTOYCookie()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestNewYSubcookie(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.YSubcookie
		want YSubcookie
	}{
		{
			name: "DTO is nil",
			dto:  nil,
			want: YSubcookie{},
		},
		{
			name: "with DTO YSubcookie",
			dto: &mordadata.YSubcookie{
				Name:   []byte("fruit"),
				Value:  []byte("apple"),
				Expire: 100,
			},
			want: YSubcookie{
				Name:   "fruit",
				Value:  "apple",
				Expire: 100,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewYSubcookie(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestYSubcookie_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model YSubcookie
		want  *mordadata.YSubcookie
	}{
		{
			name:  "Model is nil",
			model: YSubcookie{},
			want:  &mordadata.YSubcookie{},
		},
		{
			name: "with Model YCookie Yp ver1",
			model: YSubcookie{
				Name:   "fruit",
				Value:  "apple",
				Expire: 100,
			},
			want: &mordadata.YSubcookie{
				Name:   []byte("fruit"),
				Value:  []byte("apple"),
				Expire: 100,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			yaCookies := YaCookies{}
			got := yaCookies.getDTOYSubcookie(tt.model)
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestYaCookies_GetYSubcookie(t *testing.T) {
	type fields struct {
		Yp YCookie
		Ys YCookie
	}

	type args struct {
		name string
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   YSubcookie
		ok     bool
	}{
		{
			name: "ys subcookie",
			fields: fields{
				Ys: YCookie{
					Subcookies: map[string]YSubcookie{
						"test": {
							Name:  "test",
							Value: "value",
						},
					},
				},
			},
			args: args{
				name: "test",
			},
			want: YSubcookie{
				Name:  "test",
				Value: "value",
			},
			ok: true,
		},
		{
			name: "yp subcookie",
			fields: fields{
				Yp: YCookie{
					Subcookies: map[string]YSubcookie{
						"test": {
							Name:  "test",
							Value: "value",
						},
					},
				},
			},
			args: args{
				name: "test",
			},
			want: YSubcookie{
				Name:  "test",
				Value: "value",
			},
			ok: true,
		},
		{
			name: "ys and yp subcookie return ys value",
			fields: fields{
				Ys: YCookie{
					Subcookies: map[string]YSubcookie{
						"test": {
							Name:  "test",
							Value: "value1",
						},
					},
				},
				Yp: YCookie{
					Subcookies: map[string]YSubcookie{
						"test": {
							Name:  "test",
							Value: "value2",
						},
					},
				},
			},
			args: args{
				name: "test",
			},
			want: YSubcookie{
				Name:  "test",
				Value: "value1",
			},
			ok: true,
		},
		{
			name:   "no subcookie",
			fields: fields{},
			args: args{
				name: "test",
			},
			want: YSubcookie{},
			ok:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			y := &YaCookies{
				Yp: tt.fields.Yp,
				Ys: tt.fields.Ys,
			}

			got, ok := y.GetYSubcookie(tt.args.name)
			assert.Equal(t, tt.want, got)
			assert.Equal(t, tt.ok, ok)
		})
	}
}

func Test_yacookies_getYandexUIDAgeInDays(t *testing.T) {
	type testCase struct {
		name   string
		cookie YaCookies
		time   int64
		want   int
	}

	cases := []testCase{
		{
			name: "generated yandexuid",
			cookie: YaCookies{
				IsYandexUIDGenerated: true,
			},
			time: 1777888999,
			want: 0,
		},
		{
			name: "old yandexuid",
			cookie: YaCookies{
				IsYandexUIDGenerated: false,
				YandexUID:            "1234567891009918799",
			},
			time: 1777888999,
			want: 0,
		},
		{
			name: "min possible timestamp",
			cookie: YaCookies{
				IsYandexUIDGenerated: false,
				YandexUID:            "1234567891009918800",
			},
			time: 1777888999,
			want: (1777888999 - 1009918800) / 86400,
		},
		{
			name: "regular case",
			cookie: YaCookies{
				IsYandexUIDGenerated: false,
				YandexUID:            "1234567891777666555",
			},
			time: 1777888999,
			want: (1777888999 - 1777666555) / 86400,
		},
		{
			name: "zero time",
			cookie: YaCookies{
				IsYandexUIDGenerated: false,
				YandexUID:            "1234567891777666555",
			},
			time: 0,
			want: 0,
		},
		{
			name: "time before timestamp",
			cookie: YaCookies{
				IsYandexUIDGenerated: false,
				YandexUID:            "1234567891777666555",
			},
			time: 1555666777,
			want: 0,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := tt.cookie.getYandexUIDAgeInDays(tt.time)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_NewYbSubcookieYaBroswerInfo(t *testing.T) {
	type testCase struct {
		name string
		dto  *mordadata.YbSubcookieYaBrowserInfo
		want common.Optional[YbSubcookieYaBroswerInfo]
	}

	cases := []testCase{
		{
			name: "nil pointer",
			dto:  nil,
			want: common.NewOptionalNil[YbSubcookieYaBroswerInfo](),
		},
		{
			name: "regular case",
			dto: &mordadata.YbSubcookieYaBrowserInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   1312,
				LastVisitAgeInDays: 792,
				MordaVisitCount:    1057,
			},
			want: common.NewOptional(YbSubcookieYaBroswerInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   1312,
				LastVisitAgeInDays: 792,
				MordaVisitCount:    1057,
			}),
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := NewYbSubcookieYaBrowserInfo(tt.dto)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_YbSubcookieYaBroswerInfo_DTO(t *testing.T) {
	type testCase struct {
		name string
		arg  *YbSubcookieYaBroswerInfo
		want *mordadata.YbSubcookieYaBrowserInfo
	}

	cases := []testCase{
		{
			name: "nil pointer",
			arg:  nil,
			want: nil,
		},
		{
			name: "regular case",
			arg: &YbSubcookieYaBroswerInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   1312,
				LastVisitAgeInDays: 792,
				MordaVisitCount:    1057,
			},
			want: &mordadata.YbSubcookieYaBrowserInfo{
				MajorVersion:       "16_9",
				BroswerAgeInDays:   1312,
				LastVisitAgeInDays: 792,
				MordaVisitCount:    1057,
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := tt.arg.DTO()
			assertpb.Equal(t, tt.want, actual)
		})
	}
}
