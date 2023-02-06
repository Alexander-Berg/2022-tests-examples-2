package compare

import (
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"go.mongodb.org/mongo-driver/bson/primitive"

	"a.yandex-team.ru/portal/madm/internal/common"
	"a.yandex-team.ru/portal/madm/internal/utils"
)

func TestCompareExportsToUpload(t *testing.T) {
	testCases := []struct {
		caseName        string
		stage           string
		environment     string
		exportsFS       map[string]common.File
		exportsMongo    map[string][]common.MongoFile
		maxExports      int
		maxHistoryBatch int
		initMocks       func(mockcalculatorProvider *MockcalculatorProvider)

		expectedUploadQueue []common.File
		expectedRotateQueue []common.File
	}{
		{
			caseName:    "new one export from FS",
			stage:       "production",
			environment: "production",
			exportsFS: map[string]common.File{
				"ab_flags": {
					ID:    primitive.ObjectID{},
					Name:  "ab_flags",
					Path:  "/opt/www/bases/madm/production/ab_flags",
					MD5:   "",
					Stage: "production",
					MTime: 1560872007,
					ServiceInfo: common.BackendInfo{
						Env:      "",
						Source:   "",
						Instance: "",
						PRNumber: "",
					},
				},
			},
			exportsMongo: map[string][]common.MongoFile{},
			maxExports:   1,

			expectedUploadQueue: []common.File{
				{
					ID:    primitive.ObjectID{},
					Name:  "ab_flags",
					Path:  "/opt/www/bases/madm/production/ab_flags",
					MD5:   "",
					Stage: "production",
					MTime: 1560872007,
					ServiceInfo: common.BackendInfo{
						Env:      "",
						Source:   "",
						Instance: "",
						PRNumber: "",
					},
				},
			},
			expectedRotateQueue: []common.File{},
			initMocks: func(mockcalculatorProvider *MockcalculatorProvider) {

			},
		},
		{
			caseName:    "new one export in different stage from FS",
			stage:       "production",
			environment: "production",
			exportsFS: map[string]common.File{
				"ab_flags": {
					ID:    primitive.ObjectID{},
					Name:  "ab_flags",
					Path:  "/opt/www/bases/madm/production/ab_flags",
					MD5:   "",
					Stage: "testing",
					MTime: 1560872007,
					ServiceInfo: common.BackendInfo{
						Env:      "",
						Source:   "",
						Instance: "",
						PRNumber: "",
					},
				},
			},
			exportsMongo: map[string][]common.MongoFile{},
			maxExports:   1,

			expectedUploadQueue: []common.File{},
			expectedRotateQueue: []common.File{},
		},
	}

	for _, tt := range testCases {
		t.Run(tt.caseName, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			log := utils.InitLogging()
			mockCalculatorProvider := NewMockcalculatorProvider(ctrl)
			mockCalculatorProvider.EXPECT().GetFileMD5(gomock.Any()).Return("", nil).MaxTimes(1)
			comparator := NewComparator(mockCalculatorProvider, log)
			actualUploadQueue, actualRotateQueue, err := comparator.CompareExportsToUpload(
				tt.stage,
				tt.environment,
				tt.exportsFS,
				tt.exportsMongo,
				tt.maxExports,
				tt.maxHistoryBatch,
			)
			assert.NoError(t, err)
			assert.Equal(t, tt.expectedUploadQueue, actualUploadQueue)
			assert.Equal(t, tt.expectedRotateQueue, actualRotateQueue)
		})
	}
}

func TestGetMongoExport(t *testing.T) {
	testCases := []struct {
		caseName    string
		stage       string
		order       exportOrder
		mongoExport []common.MongoFile

		expected *common.File
	}{
		// exportLast cases
		{
			caseName:    "no exports from mongo",
			stage:       "production",
			order:       exportLast,
			mongoExport: []common.MongoFile{},

			expected: nil,
		},
		{
			caseName: "one export from mongo if different stage",
			stage:    "production",
			order:    exportLast,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "testing",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},

			expected: nil,
		},
		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportLast,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{1},
				UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872007,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},
		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportLast,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
				{
					ID:         primitive.ObjectID{2},
					UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872008,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{2},
				UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872008,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},
		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportLast,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{2},
					UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872008,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{2},
				UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872008,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},

		// exportFirst cases
		{
			caseName:    "no exports from mongo",
			stage:       "production",
			order:       exportFirst,
			mongoExport: []common.MongoFile{},

			expected: nil,
		},
		{
			caseName: "one export from mongo if different stage",
			stage:    "production",
			order:    exportFirst,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "testing",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},

			expected: nil,
		},
		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportFirst,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{1},
				UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872007,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},
		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportFirst,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
				{
					ID:         primitive.ObjectID{2},
					UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872008,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{1},
				UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872007,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},

		{
			caseName: "one export from mongo",
			stage:    "production",
			order:    exportFirst,
			mongoExport: []common.MongoFile{
				{
					ID:         primitive.ObjectID{2},
					UploadDate: time.Date(2022, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872008,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
				{
					ID:         primitive.ObjectID{1},
					UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
					Metadata: common.File{
						ID:    primitive.ObjectID{},
						Name:  "ab_flags",
						Path:  "/opt/www/bases/madm/production/ab_flags",
						MD5:   "",
						Stage: "production",
						MTime: 1560872007,
						ServiceInfo: common.BackendInfo{
							Env:      "",
							Source:   "",
							Instance: "",
							PRNumber: "",
						},
					},
				},
			},
			expected: &common.File{
				ID:         primitive.ObjectID{1},
				UploadDate: time.Date(2021, time.January, 1, 0, 0, 0, 100*1e6, time.Local),
				Name:       "ab_flags",
				Path:       "/opt/www/bases/madm/production/ab_flags",
				MD5:        "",
				Stage:      "production",
				MTime:      1560872007,
				ServiceInfo: common.BackendInfo{
					Env:      "",
					Source:   "",
					Instance: "",
					PRNumber: "",
				},
			},
		},
	}
	for _, tt := range testCases {
		t.Run(tt.caseName, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			log := utils.InitLogging()
			mockCalculatorProvider := NewMockcalculatorProvider(ctrl)
			comparator := NewComparator(mockCalculatorProvider, log)
			lastMongoExport := comparator.getMongoExport(tt.stage, tt.mongoExport, tt.order)
			assert.Equal(t, tt.expected, lastMongoExport)
		})
	}
}
