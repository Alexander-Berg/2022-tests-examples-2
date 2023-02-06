package compare

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_madmContentComparator_compareContent(t *testing.T) {
	createGetter := func(ctrl *gomock.Controller, ret models.MadmContent) *MockmadmContentGetter {
		madmContentMock := NewMockmadmContentGetter(ctrl)
		madmContentMock.EXPECT().GetMadmContent().Return(ret).Times(1)

		return madmContentMock
	}

	tests := []struct {
		name            string
		expectedContent models.MadmContent
		gotContent      models.MadmContent
		additionals     map[string][]interface{}
		wantErr         string
	}{
		{
			name:            "no diff",
			expectedContent: models.MadmContent{Values: []string{"big"}},
			gotContent:      models.MadmContent{Values: []string{"big"}},
			wantErr:         "",
		},
		{
			name:            "diff",
			expectedContent: models.MadmContent{Values: []string{"all", "big", "api_search_2"}},
			gotContent:      models.MadmContent{Values: []string{"big", "all", "touch_only"}},
			wantErr:         "[ExtraMadmContentValues], [MissedMadmContentValues], [ExpectedMadmContent], [GotMadmContent]",
			additionals: map[string][]interface{}{
				"ExtraMadmContentValues":  {[]string{"touch_only"}},
				"MissedMadmContentValues": {[]string{"api_search_2"}},
				"ExpectedMadmContent":     {[]string{"all", "api_search_2", "big"}},
				"GotMadmContent":          {[]string{"all", "big", "touch_only"}},
			},
		},
		{
			name:            "diff extra",
			expectedContent: models.MadmContent{Values: []string{"all", "big"}},
			gotContent:      models.MadmContent{Values: []string{"big", "all", "touch_only"}},
			wantErr:         "[ExtraMadmContentValues], [ExpectedMadmContent], [GotMadmContent]",
			additionals: map[string][]interface{}{
				"ExtraMadmContentValues": {[]string{"touch_only"}},
				"ExpectedMadmContent":    {[]string{"all", "big"}},
				"GotMadmContent":         {[]string{"all", "big", "touch_only"}},
			},
		},
		{
			name:            "diff missed",
			expectedContent: models.MadmContent{Values: []string{"all", "big", "touch_only"}},
			gotContent:      models.MadmContent{Values: []string{"big", "all"}},
			wantErr:         "[MissedMadmContentValues], [ExpectedMadmContent], [GotMadmContent]",
			additionals: map[string][]interface{}{
				"MissedMadmContentValues": {[]string{"touch_only"}},
				"ExpectedMadmContent":     {[]string{"all", "big", "touch_only"}},
				"GotMadmContent":          {[]string{"all", "big"}},
			},
		},
		{
			name:            "diff empty expected",
			expectedContent: models.MadmContent{Values: []string{}},
			gotContent:      models.MadmContent{Values: []string{"big", "all", "touch_only"}},
			wantErr:         "[ExtraMadmContentValues], [ExpectedMadmContent], [GotMadmContent]",
			additionals: map[string][]interface{}{
				"ExtraMadmContentValues": {[]string{"all", "big", "touch_only"}},
				"ExpectedMadmContent":    {[]string{}},
				"GotMadmContent":         {[]string{"all", "big", "touch_only"}},
			},
		},
		{
			name:            "diff empty got",
			expectedContent: models.MadmContent{Values: []string{"all", "big", "touch_only"}},
			gotContent:      models.MadmContent{Values: []string{}},
			wantErr:         "[MissedMadmContentValues], [ExpectedMadmContent], [GotMadmContent]",
			additionals: map[string][]interface{}{
				"MissedMadmContentValues": {[]string{"all", "big", "touch_only"}},
				"ExpectedMadmContent":     {[]string{"all", "big", "touch_only"}},
				"GotMadmContent":          {[]string{}},
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			expected := createGetter(ctrl, test.expectedContent)
			got := createGetter(ctrl, test.gotContent)

			c := madmContentComparator{}

			err := c.compareContent(expected, got)

			if test.wantErr == "" {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
				additionalErr, ok := err.(errorTemplated)
				require.True(t, ok)

				template, additionals := additionalErr.GetTemplated()
				assert.Equal(t, test.wantErr, template)
				assert.True(t, reflect.DeepEqual(test.additionals, additionals), fmt.Sprintf("expected %+v\ngot %+v", test.additionals, additionals))
			}
		})
	}
}
