package handler

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/internal/compare/req"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
)

func Test_handler_handle(t *testing.T) {
	type fields struct {
		httpResponseCode uint32
		httpResponseErr  error
		parseErr         error
		comparatorErrs   []error
	}
	tests := []struct {
		name    string
		fields  fields
		wantErr bool
	}{
		{
			name: "get perl request error",
			fields: fields{
				httpResponseErr: assert.AnError,
			},
			wantErr: true,
		},
		{
			name: "non-200 response code",
			fields: fields{
				httpResponseCode: 302,
			},
			wantErr: false,
		},
		{
			name: "200 response code",
			fields: fields{
				httpResponseCode: 200,
			},
			wantErr: false,
		},
		{
			name: "parsing error",
			fields: fields{
				httpResponseCode: 200,
				parseErr:         assert.AnError,
			},
			wantErr: true,
		},
		{
			name: "compare error",
			fields: fields{
				httpResponseCode: 200,
				comparatorErrs:   []error{assert.AnError},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			baseCtx := NewMockforceableContextGot(ctrl)
			baseCtx.EXPECT().GetLogger().Return(log3.NewLoggerStub()).AnyTimes()

			ctx := NewMockhandlerContext(ctrl)
			ctx.EXPECT().GetPerlReqForCompare().Return(&protoanswers.THttpResponse{
				StatusCode: tt.fields.httpResponseCode,
			}, tt.fields.httpResponseErr).Times(1)

			parser := req.NewMockParser(ctrl)
			parser.EXPECT().Parse(nil).Return(nil, tt.fields.parseErr).MaxTimes(1)

			comparator := NewMockbaseComparator(ctrl)
			comparator.EXPECT().CompareContext(gomock.Any(), gomock.Any()).Return(tt.fields.comparatorErrs).MaxTimes(1)

			comparatorSecond := NewMockbaseComparator(ctrl)
			comparatorSecond.EXPECT().CompareContext(gomock.Any(), gomock.Any()).Return(nil).MaxTimes(1)

			itsOptionsGetter := NewMockitsComparatorOptionsGetter(ctrl)
			itsOptionsGetter.EXPECT().GetComparatorOptions().Return(its.ComparatorOptions{}).AnyTimes()

			h := &handler{
				comparator:       comparator,
				comparatorSecond: comparatorSecond,
				requestParser:    parser,
				itsOptionsGetter: itsOptionsGetter,
			}

			err := h.ServeCompare(baseCtx, ctx)
			assert.Equal(t, tt.wantErr, err != nil)
		})
	}
}
