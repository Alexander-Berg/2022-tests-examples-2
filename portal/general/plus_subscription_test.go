package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewPlusSubscription(t *testing.T) {
	type testCase struct {
		name string
		dto  *morda_data.PlusSubscription
		want PlusSubscription
	}
	cases := []testCase{
		{
			name: "nil pointer",
			dto:  nil,
			want: PlusSubscription{},
		},
		{
			name: "not activated",
			dto: &morda_data.PlusSubscription{
				Status:              false,
				StatusType:          "",
				NextChargeTimestamp: 0,
				ExpireTimestamp:     0,
			},
			want: PlusSubscription{
				Status:              false,
				NextChargeTimestamp: 0,
				StatusType:          "",
				ExpireTimestamp:     0,
			},
		},
		{
			name: "activated",
			dto: &morda_data.PlusSubscription{
				Status:              true,
				StatusType:          "YA_PREMIUM",
				NextChargeTimestamp: 1656633601,
				ExpireTimestamp:     1668524400,
			},
			want: PlusSubscription{
				Status:              true,
				NextChargeTimestamp: 1656633601,
				StatusType:          "YA_PREMIUM",
				ExpireTimestamp:     1668524400,
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := newPlusSubscription(tt.dto)
			assert.Equal(t, tt.want, actual, "compare models")
		})
	}
}

func TestPlusSubscription_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *PlusSubscription
		want  *morda_data.PlusSubscription
	}

	cases := []testCase{
		{
			name:  "nil pointer",
			model: nil,
			want:  nil,
		},
		{
			name: "not activated",
			model: &PlusSubscription{
				Status:              false,
				NextChargeTimestamp: 0,
				StatusType:          "",
				ExpireTimestamp:     0,
			},
			want: &morda_data.PlusSubscription{
				Status:              false,
				StatusType:          "",
				NextChargeTimestamp: 0,
				ExpireTimestamp:     0,
			},
		},
		{
			name: "activated",
			model: &PlusSubscription{
				Status:              true,
				NextChargeTimestamp: 1656633601,
				StatusType:          "YA_PREMIUM",
				ExpireTimestamp:     1668524400,
			},
			want: &morda_data.PlusSubscription{
				Status:              true,
				StatusType:          "YA_PREMIUM",
				NextChargeTimestamp: 1656633601,
				ExpireTimestamp:     1668524400,
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := tt.model.DTO()
			assertpb.Equal(t, tt.want, actual, "compare dto")
		})
	}
}
