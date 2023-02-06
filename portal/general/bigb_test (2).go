package storage

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func Test_havePromoGroupsAnd(t *testing.T) {
	var testCases = []struct {
		Name        string
		PromoGroups common.StringSet
		BKTag       string
		Expected    bool
	}{
		{
			Name:        "no value",
			PromoGroups: common.NewStringSet("1:1", "2:2"),
			BKTag:       "",
			Expected:    false,
		},
		{
			Name:        "one value match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "2:2",
			Expected:    true,
		},
		{
			Name:        "one value doesn't match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "4:4",
			Expected:    false,
		},
		{
			Name:        "groups or match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "1:1,4:4",
			Expected:    true,
		},
		{
			Name:        "groups or match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "1:1 4:4",
			Expected:    true,
		},
		{
			Name:        "groups or match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "4:4; 1:1",
			Expected:    true,
		},
		{
			Name:        "groups or doesn't match",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "4:4; 5:5",
			Expected:    false,
		},
		{
			Name:        "groups or match with &",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "4:4; 1:1&2:2",
			Expected:    true,
		},
		{
			Name:        "groups or doesn't match with &",
			PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
			BKTag:       "4:4; 1:1&5:5",
			Expected:    false,
		},
	}

	for _, tc := range testCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			require.Equal(t, tc.Expected, havePromoGroupsAnd(tc.PromoGroups, tc.BKTag))
		})
	}
}
