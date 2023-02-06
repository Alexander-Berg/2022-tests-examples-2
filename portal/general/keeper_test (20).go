package robot

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_GetRobot(t *testing.T) {
	type parserAnswer struct {
		answer models.Robot
		err    error
	}
	type fields struct {
		parserAnswer parserAnswer
		logger       log3.LoggerAlterable
		cached       *models.Robot
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   models.Robot
	}{
		{
			name: "nil cache",
			fields: fields{
				parserAnswer: parserAnswer{
					answer: models.Robot{
						IsRobot: true,
					},
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Robot{IsRobot: true},
		},
		{
			name: "parse error",
			fields: fields{
				parserAnswer: parserAnswer{
					answer: models.Robot{
						IsRobot: true,
					},
					err: assert.AnError,
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Robot{IsRobot: true},
		},
		{
			name: "not nil cache",
			fields: fields{
				logger:       log3.NewLoggerStub(),
				cached:       &models.Robot{IsRobot: true},
				cacheUpdated: false,
			},
			want: models.Robot{IsRobot: true},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			parserMock := NewMockrobotParser(ctrl)
			parserMock.EXPECT().Parse().Return(tt.fields.parserAnswer.answer, tt.fields.parserAnswer.err).MaxTimes(1)
			k := &keeper{
				parser:       parserMock,
				logger:       tt.fields.logger,
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			got := k.GetRobot()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_ForceRobot(t *testing.T) {
	type fields struct {
		cached       *models.Robot
		cacheUpdated bool
	}
	type args struct {
		robot models.Robot
	}
	tests := []struct {
		name             string
		fields           fields
		args             args
		wantCache        *models.Robot
		wantCacheUpdated bool
	}{
		{
			name: "cache updated",
			fields: fields{
				cached:       &models.Robot{IsRobot: false},
				cacheUpdated: false,
			},
			args: args{
				robot: models.Robot{IsRobot: true},
			},
			wantCache:        &models.Robot{IsRobot: true},
			wantCacheUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			k.ForceRobot(tt.args.robot)
			assert.Equal(t, tt.wantCache, k.cached)
			assert.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetRobotIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.Robot
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *morda_data.Robot
	}{
		{
			name: "not updated cache",
			fields: fields{
				cached:       &models.Robot{IsRobot: true},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "updated cache",
			fields: fields{
				cached:       &models.Robot{IsRobot: true},
				cacheUpdated: true,
			},
			want: &morda_data.Robot{IsRobot: true},
		},
		{
			name: "updated nil cache",
			fields: fields{
				cached:       nil,
				cacheUpdated: true,
			},
			want: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			assert.Equal(t, tt.want, k.GetRobotIfUpdated())
		})
	}
}
