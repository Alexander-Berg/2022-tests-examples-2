package requests

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_GetRequest(t *testing.T) {
	requestModel := models.Request{
		IsInternal:   true,
		IsStaffLogin: true,
		IsPumpkin:    true,
		IP:           "1.1.1.1",
		URL:          "/",
		CGI: map[string][]string{
			"yandex": {"0"},
		},
		SearchAppFeatures: make([]models.SearchAppFeature, 0),
	}

	testCases := []struct {
		name   string
		cache  *mordadata.Request
		parsed models.Request

		want             models.Request
		wantCachedDTO    *mordadata.Request
		wantCachedModel  *models.Request
		wantCacheUpdated bool
	}{
		{
			name:   "nil cache",
			cache:  nil,
			parsed: requestModel,

			want:             requestModel,
			wantCachedDTO:    requestModel.DTO(),
			wantCachedModel:  &requestModel,
			wantCacheUpdated: true,
		},
		{
			name:  "not nil cache",
			cache: requestModel.DTO(),

			want:             requestModel,
			wantCachedDTO:    requestModel.DTO(),
			wantCachedModel:  &requestModel,
			wantCacheUpdated: false,
		},
	}

	for _, tt := range testCases {
		t.Run(tt.name, func(t *testing.T) {
			parserMock := NewMockrequestParser(gomock.NewController(t))
			keeper := NewKeeper(tt.cache, log3.NewLoggerStub(), parserMock)

			if tt.cache == nil {
				parserMock.EXPECT().Parse().Return(tt.parsed, nil).Times(1)
			}

			got := keeper.GetRequest()

			assert.Equal(t, tt.want, got)
			assert.Equal(t, tt.wantCachedDTO, keeper.cached.DTO())
			assert.Equal(t, tt.wantCachedModel, keeper.cached)
			assert.Equal(t, tt.wantCacheUpdated, keeper.cacheUpdated)
		})
	}
}
