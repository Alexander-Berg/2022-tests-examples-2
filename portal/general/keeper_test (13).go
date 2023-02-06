package log3

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/apphost/api/service/go/apphost"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func Test_keeper_GetRequestItem(t *testing.T) {
	type mockSet struct {
		deviceGetter
		requestGetter
		geoGetter
		apphostInfoGetter
		yaCookieGetter
		abFlagsGetter
		mordazoneGetter
		mordaContentGetter
		robotGetter
	}
	type testCase struct {
		name     string
		mockFunc func(t *testing.T) *mockSet
		want     *LogItemRequest
		wantErr  bool
	}

	testCases := []testCase{
		{
			name: "all fields",
			mockFunc: func(t *testing.T) *mockSet {
				controller := gomock.NewController(t)
				deviceGetterMock := NewMockdeviceGetter(controller)
				deviceGetterMock.EXPECT().GetDevice().Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						UserAgent: "Some Browser",
					},
				}).AnyTimes()

				geoGetterMock := NewMockgeoGetter(controller)
				geoGetterMock.EXPECT().GetGeo().Return(models.Geo{
					RegionID: 20728,
				}).AnyTimes()

				requestGetterMock := NewMockrequestGetter(controller)
				requestGetterMock.EXPECT().GetRequest().Return(models.Request{
					IsInternal: true,
					URL:        "/portal/api/search/2",
					IP:         "87.250.250.242",
					Host:       "yandex.ru",
				}).AnyTimes()

				apphostInfoGetterMock := NewMockapphostInfoGetter(controller)
				apphostInfoGetterMock.EXPECT().ApphostParams().Return(apphost.ServiceParams{RequestID: "ABC"}, nil).AnyTimes()
				apphostInfoGetterMock.EXPECT().Path().Return("/some/handler").AnyTimes()

				yaCookieGetterMock := NewMockyaCookieGetter(controller)
				yaCookieGetterMock.EXPECT().GetYaCookies().Return(models.YaCookies{
					YandexUID: "151119920015111992",
				}).AnyTimes()

				abFlagsGetterMock := NewMockabFlagsGetter(controller)
				abFlagsGetterMock.EXPECT().GetFlags().Return(models.ABFlags{
					Flags:          map[string]string{"avocado": "yes"},
					TestIDs:        common.NewIntSet(151192),
					TestIDsBuckets: map[int][]int{151192: {-1}},
				})

				mordazoneGetterMock := NewMockmordazoneGetter(controller)
				mordazoneGetterMock.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"}).AnyTimes()

				mordaContentGetterMock := NewMockmordaContentGetter(controller)
				mordaContentGetterMock.EXPECT().GetMordaContent().Return(models.MordaContent{
					Value: "touch",
				})

				robotGetterMock := NewMockrobotGetter(controller)
				robotGetterMock.EXPECT().GetRobot().Return(models.Robot{IsRobot: false})

				return &mockSet{
					deviceGetter:       deviceGetterMock,
					requestGetter:      requestGetterMock,
					geoGetter:          geoGetterMock,
					apphostInfoGetter:  apphostInfoGetterMock,
					yaCookieGetter:     yaCookieGetterMock,
					abFlagsGetter:      abFlagsGetterMock,
					mordazoneGetter:    mordazoneGetterMock,
					mordaContentGetter: mordaContentGetterMock,
					robotGetter:        robotGetterMock,
				}
			},
			want: &LogItemRequest{
				UserAgent:       "Some Browser",
				URL:             "yandex.ru/portal/api/search/2",
				IP:              "87.250.250.242",
				Platform:        "touch",
				RequestID:       "ABC",
				Page:            "/some/handler",
				YandexUID:       "151119920015111992",
				IsInternal:      true,
				IsRobot:         false,
				Region:          20728,
				ExperimentSlots: "151192,0,-1",
				ExperimentFlags: "avocado=yes",
			},
			wantErr: false,
		},
	}

	for _, tt := range testCases {
		t.Run(tt.name, func(t *testing.T) {
			m := tt.mockFunc(t)
			keeper := NewKeeper(m.deviceGetter, m.requestGetter, m.robotGetter, m.geoGetter, m.apphostInfoGetter, m.yaCookieGetter,
				m.abFlagsGetter, m.mordazoneGetter, m.mordaContentGetter)
			actual, err := keeper.GetItemRequest()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			assert.Equal(t, tt.want, actual)
		})
	}
}
