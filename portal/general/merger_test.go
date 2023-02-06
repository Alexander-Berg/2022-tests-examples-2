package searchapp

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/morda-go/pkg/dto"
	"a.yandex-team.ru/portal/morda-go/tests/helpers"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func Test_merge(t *testing.T) {
	tests := []struct {
		name     string
		testCase mergeTestCase
		want     *protoanswers.THttpResponse
		wantErr  bool
	}{
		{
			name: "Skipped blocks = 0; got raw geohelper response",
			testCase: mergeTestCase{
				skippedBlocks: []string{},
				rawGeohelperResponse: &protoanswers.THttpResponse{
					StatusCode: http.StatusOK,
					Content:    []byte(`{"test": "test"}`),
				},
			},
			want: &protoanswers.THttpResponse{
				StatusCode: http.StatusOK,
				Content:    []byte(`{"test": "test"}`),
			},
			wantErr: false,
		},
		{
			name: "One block from div renderer; failed = 0",
			testCase: mergeTestCase{
				geohelperResponse: &dto.GeohelperResponse{
					DivTemplates: map[string]json.RawMessage{"top_news": []byte(`{}`), "auto": []byte(`{}`), "test": []byte(`{}`)},
					Layout:       []dto.GeohelperResponseLayoutItem{{}, {}, {}},
					Blocks:       []dto.GeohelperResponseBlock{{}, {}},
				},
				skippedBlocks: []string{"auto"},
				failedBlocks:  []string{},
				divRendererResponse: &dto.GeohelperResponse{
					DivTemplates: map[string]json.RawMessage{"auto": []byte(`{"value": "auto"}`)},
					Layout:       []dto.GeohelperResponseLayoutItem{},
					Blocks:       []dto.GeohelperResponseBlock{{}},
				},
			},
			want: &protoanswers.THttpResponse{
				StatusCode: http.StatusOK,
				Headers:    []*protoanswers.THeader{{Name: "Content-Type", Value: "application/json; charset=utf-8"}},
				//TODO: migrate to golden files
				Content: []byte(`{"div_templates":{"auto":{"value":"auto"},"test":{},"top_news":{}},"ttl":0,"ttv":0,"country":"","api_version":"","utime":0,"geo_country":0,"layout":[{"id":"","type":"","heavy":0},{"id":"","type":"","heavy":0},{"id":"","type":"","heavy":0}],"msid":"","api_name":"","geo":0,"block":[{"id":"","data":null,"ttl":0,"ttv":0,"utime":0,"type":"","topic":"","heavy":0},{"id":"","data":null,"ttl":0,"ttv":0,"utime":0,"type":"","topic":"","heavy":0},{"id":"","data":null,"ttl":0,"ttv":0,"utime":0,"type":"","topic":"","heavy":0}],"lang":""}`),
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctxMock := &mocks.GeohelperContext{}
			initMockByMergeCase(ctxMock, tt.testCase, tt.want)

			err := merge(ctxMock)

			ctxMock.AssertExpectations(t)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

type mergeTestCase struct {
	geohelperResponse    *dto.GeohelperResponse
	divRendererResponse  *dto.GeohelperResponse
	skippedBlocks        []string
	failedBlocks         []string
	rawGeohelperResponse *protoanswers.THttpResponse
}

func initMockByMergeCase(ctxMock *mocks.GeohelperContext, c mergeTestCase, want *protoanswers.THttpResponse) {
	if c.geohelperResponse != nil {
		ctxMock.On("GetGeohelperResponse").Return(c.geohelperResponse, nil).Once()
	}

	if c.skippedBlocks != nil {
		ctxMock.On("GetSkippedBlocks").Return(c.skippedBlocks, nil).Once()
	}

	if c.rawGeohelperResponse != nil {
		ctxMock.On("GetGeohelperRawResponse").Return(c.rawGeohelperResponse, nil).Once()
	}

	if c.failedBlocks != nil {
		ctxMock.On("GetFailedBlocks").Return(c.failedBlocks, nil).Once()
	}

	if c.divRendererResponse != nil {
		ctxMock.On("GetDivRendererResponse").Return(c.divRendererResponse, nil).Once()
	}

	if want != nil {
		ctxMock.On("AddPB", httpResponse, mock.MatchedBy(func(obj *protoanswers.THttpResponse) bool {
			return helpers.THttpResponseCompare(obj, want)
		})).Return(nil).Once()
	}
}
