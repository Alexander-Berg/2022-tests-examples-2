package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/golang/protobuf/proto"
	"github.com/stretchr/testify/require"

	protobigb "a.yandex-team.ru/ads/bsyeti/eagle/collect/proto"
)

func Test_bigBURLComparator_compare(t *testing.T) {
	tests := []struct {
		name string

		expected *protobigb.TQueryParams
		got      *protobigb.TQueryParams

		wantErr bool
	}{
		{
			name:     "both are nil",
			expected: nil,
			got:      nil,
			wantErr:  true,
		},
		{
			name: "got are nil",
			expected: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(123),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			got:     nil,
			wantErr: true,
		},
		{
			name:     "expected are nil",
			expected: nil,
			got: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(123),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			wantErr: true,
		},
		{
			name: "equal",
			expected: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(123),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			got: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(123),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			wantErr: false,
		},
		{
			name: "not equal",
			expected: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(124),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			got: &protobigb.TQueryParams{
				BigbUid: proto.Uint64(123),
				Uuid:    proto.String("a1a1a1"),
				Puid:    proto.Uint64(456),
			},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expected := NewMockComparableContextExpected(ctrl)
			expected.EXPECT().GetBigBURL().Return(tt.expected).AnyTimes()
			got := NewMockComparableContextGot(ctrl)
			got.EXPECT().GetBigBURL().Return(tt.got).AnyTimes()

			c := &bigBURLComparator{}
			err := c.compare(expected, got)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
