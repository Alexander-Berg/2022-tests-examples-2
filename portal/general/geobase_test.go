package geobase

import (
	"testing"

	"github.com/stretchr/testify/require"

	gb "a.yandex-team.ru/library/go/yandex/geobase"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
)

func Test_handleError(t *testing.T) {
	type args struct {
		id  gb.ID
		err error
	}
	tests := []struct {
		name            string
		args            args
		expectTemplated bool
		unknownID       gb.ID
		wantErr         error
	}{
		{
			name: "common case",
			args: args{
				id:  218752,
				err: errors.Error("Impl::RegIdxById(218752) - unknown id (out-of-range)"),
			},
			expectTemplated: true,
			wantErr:         errors.Error("Impl::RegIdxById([GeobaseUnknownID]) - unknown id (out-of-range)"),
			unknownID:       218752,
		},
		{
			name: "without out of range",
			args: args{
				id:  218752,
				err: errors.Error("Impl::RegIdxById(218752) - unknown id"),
			},
			expectTemplated: true,
			wantErr:         errors.Error("Impl::RegIdxById([GeobaseUnknownID]) - unknown id"),
			unknownID:       218752,
		},
		{
			name: "simple error",
			args: args{
				id:  0,
				err: errors.Error("error"),
			},
			expectTemplated: false,
			wantErr:         errors.Error("error"),
		},
		{
			name: "nil error",
			args: args{
				id:  0,
				err: nil,
			},
			expectTemplated: false,
			wantErr:         nil,
		},
		{
			name: "error with percent symbols",
			args: args{
				id:  123,
				err: errors.Error("unknown id - %s%s%%ss%%%s (123)"),
			},
			expectTemplated: true,
			wantErr:         errors.Error("unknown id - %s%s%%ss%%%s ([GeobaseUnknownID])"),
			unknownID:       123,
		},
		{
			name: "error without id",
			args: args{
				id:  123,
				err: errors.Error("Impl::RegIdxById - unknown id"),
			},
			expectTemplated: true,
			wantErr:         errors.Error("Impl::RegIdxById - unknown id ([GeobaseUnknownID])"),
			unknownID:       123,
		},
		{
			name: "error with multiple ids",
			args: args{
				id:  123,
				err: errors.Error("Impl::RegIdxById(123) - unknown id (123), id (123) is not found"),
			},
			expectTemplated: true,
			wantErr:         errors.Error("Impl::RegIdxById([GeobaseUnknownID]) - unknown id ([GeobaseUnknownID]), id ([GeobaseUnknownID]) is not found"),
			unknownID:       123,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := handleError(tt.args.id, tt.args.err)

			if tt.expectTemplated {
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)

				template, data := errTemplated.GetTemplated()
				values, ok := data["GeobaseUnknownID"]
				if !ok || len(values) != 1 {
					require.Fail(t, "wrong GeobaseUnknownID data")
				}

				id, ok := values[0].(gb.ID)
				require.True(t, ok)

				require.Equal(t, tt.unknownID, id)
				require.Equal(t, tt.wantErr.Error(), template)
			} else if tt.wantErr == nil {
				require.Equal(t, tt.wantErr, err)
			} else {
				require.Equal(t, tt.wantErr.Error(), err.Error())
			}
		})
	}
}
