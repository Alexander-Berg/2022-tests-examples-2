package certutil_test

import (
	"crypto/x509/pkix"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/libs/certutil"
)

func TestParseExtraNames(t *testing.T) {
	cases := []struct {
		in  []pkix.AttributeTypeAndValue
		out *certutil.ExtraName
		err bool
	}{
		{
			in: []pkix.AttributeTypeAndValue{
				{
					Type: []int{2, 5, 4, 6},
				},
				{
					Type:  certutil.ExtNameTokenID,
					Value: "token_id",
				},
				{
					Type:  certutil.ExtNameEnrollID,
					Value: "enroll_id",
				},
				{
					Type:  certutil.ExtNameUser,
					Value: "user",
				},
			},
			out: &certutil.ExtraName{
				TokenID:  "token_id",
				EnrollID: "enroll_id",
				User:     "user",
			},
		},
		{
			in: []pkix.AttributeTypeAndValue{
				{
					Type: []int{2, 5, 4, 6},
				},
				{
					Type:  certutil.ExtNameTokenID,
					Value: 1,
				},
				{
					Type:  certutil.ExtNameEnrollID,
					Value: "enroll_id",
				},
				{
					Type:  certutil.ExtNameUser,
					Value: "user",
				},
			},
			err: true,
		},
		{
			in: []pkix.AttributeTypeAndValue{
				{
					Type: []int{2, 5, 4, 6},
				},
				{
					Type:  certutil.ExtNameTokenID,
					Value: "token_id",
				},
				{
					Type:  certutil.ExtNameEnrollID,
					Value: 2,
				},
				{
					Type:  certutil.ExtNameUser,
					Value: "user",
				},
			},
			err: true,
		},
		{
			in: []pkix.AttributeTypeAndValue{
				{
					Type: []int{2, 5, 4, 6},
				},
				{
					Type:  certutil.ExtNameTokenID,
					Value: "token_id",
				},
				{
					Type:  certutil.ExtNameEnrollID,
					Value: "enroll_id",
				},
				{
					Type:  certutil.ExtNameUser,
					Value: 3,
				},
			},
			err: true,
		},
	}

	for i, tc := range cases {
		t.Run(fmt.Sprint(i), func(t *testing.T) {
			actual, err := certutil.ParseExtraNames(tc.in)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.out, actual)
		})
	}
}
