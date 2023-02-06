package compare

import (
	"fmt"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/lang"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/unistat"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
)

type errorTemplated interface {
	GetTemplated() (string, map[string][]interface{})
}

func Test_NewComparator(t *testing.T) {
	langProvider := lang.GetResourceLocalizer()

	type args struct {
		options []Option
	}
	tests := []struct {
		name         string
		args         args
		want         common.StringSet
		wantIsSecond bool
	}{
		{
			name: "no options",
			args: args{
				options: nil,
			},
			want: common.NewStringSet(),
		},
		{
			name: "all comparators",
			args: args{
				options: []Option{
					WithAll(),
				},
			},
			want: common.NewStringSet(
				abFlagsKey,
				authKey,
				bigBKey,
				bigBURLKey,
				clidKey,
				deviceKey,
				exportsKey,
				geoKey,
				localeKey,
				madmContentKey,
				mordaContentKey,
				sliceNamesKey,
				timeKey,
				yabsKey,
				yabsURLKey,
				yandexUIDKey,
				zoneKey,
			),
		},
		{
			name: "all comparators without several",
			args: args{
				options: []Option{
					WithAll(),
					WithoutMordaContent(),
					WithoutMadmContent(),
					WithoutDevice(),
				},
			},
			want: common.NewStringSet(
				abFlagsKey,
				authKey,
				bigBKey,
				bigBURLKey,
				clidKey,
				exportsKey,
				geoKey,
				localeKey,
				sliceNamesKey,
				timeKey,
				yabsKey,
				yabsURLKey,
				yandexUIDKey,
				zoneKey,
			),
		},
		{
			name: "with several",
			args: args{
				options: []Option{
					WithABFlags(),
					WithSliceNames(),
				},
			},
			want: common.NewStringSet(
				abFlagsKey,
				sliceNamesKey,
			),
		},
		{
			name: "without non-presented keys",
			args: args{
				options: []Option{
					WithZone(),
					WithMordaContent(),
					WithoutABFlags(),
					WithoutSliceNames(),
				},
			},
			want: common.NewStringSet(
				zoneKey,
				mordaContentKey,
			),
		},
		{
			name: "with second",
			args: args{
				options: []Option{
					WithABFlags(),
					WithSliceNames(),
					WithSecond(),
				},
			},
			want: common.NewStringSet(
				abFlagsKey,
				sliceNamesKey,
			),
			wantIsSecond: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			mockedITSComparatorOptionsGetter := NewMockitsComparatorOptionsGetter(ctrl)
			mockedITSComparatorOptionsGetter.EXPECT().GetComparatorOptions().Return(its.ComparatorOptions{}).AnyTimes()

			got := NewComparator(mockedITSComparatorOptionsGetter, unistat.NewRegistry("test"), nil,
				langProvider, tt.args.options...)
			gotSet := common.NewStringSet()
			for key := range got.comparators {
				gotSet.Add(key)
			}

			assert.Equal(t, tt.want, gotSet)
			assert.Equal(t, tt.wantIsSecond, got.isSecond)
		})
	}
}

func Test_contextComparator_compareContext(t *testing.T) {
	type comparatorAnswer struct {
		compare error
		force   error
	}
	type result struct {
		wantToForce bool
		wantMetric  string
	}

	tests := []struct {
		name              string
		randomizerAnswer  int
		comparatorAnswers map[string]comparatorAnswer
		its               its.ComparatorOptions
		wantComponents    map[string]result
		wantErrs          []error
	}{
		{
			name:              "no comparators",
			randomizerAnswer:  42,
			comparatorAnswers: map[string]comparatorAnswer{},
			its:               its.ComparatorOptions{},
			wantComponents:    map[string]result{},
			wantErrs:          nil,
		},
		{
			name:             "zero default percent, no component settings",
			randomizerAnswer: 42,
			comparatorAnswers: map[string]comparatorAnswer{
				abFlagsKey: {
					compare: errors.WithAddedTags(errors.Error("abflags error"), perlErrTag),
				},
				zoneKey: {
					compare: errors.WithAddedTags(errors.Error("zone error"), goErrTag),
					force:   nil,
				},
				mordaContentKey: {
					compare: errors.WithAddedTags(errors.Error("mordacontent error"), compareErrTag),
					force:   nil,
				},
			},
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 0,
				},
			},
			wantComponents: map[string]result{
				abFlagsKey: {
					wantToForce: false,
					wantMetric:  errorMetric,
				},
				zoneKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
				mordaContentKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
			},
			wantErrs: nil,
		},
		{
			name:             "100 default percent, some comparators return error",
			randomizerAnswer: 42,
			comparatorAnswers: map[string]comparatorAnswer{
				abFlagsKey: {
					compare: nil,
				},
				zoneKey: {
					compare: nil,
				},
				yabsKey: {
					compare: errors.WithAddedTags(errors.Error("yabs error"), perlErrTag),
				},
				bigBKey: {
					compare: errors.WithAddedTags(errors.Error("bigb error"), compareErrTag),
					force:   nil,
				},
			},
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 100,
				},
			},
			wantComponents: map[string]result{
				abFlagsKey: {
					wantToForce: false,
					wantMetric:  fromGoMetric,
				},
				zoneKey: {
					wantToForce: false,
					wantMetric:  fromGoMetric,
				},
				yabsKey: {
					wantToForce: false,
					wantMetric:  errorMetric,
				},
				bigBKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
			},
			wantErrs: []error{
				errors.Errorf("%s not equal: bigb error", bigBKey),
				errors.Errorf("couldn't get %s from Perl: yabs error", yabsKey),
			},
		},
		{
			name:             "some comparators return error, its options are presented",
			randomizerAnswer: 20,
			comparatorAnswers: map[string]comparatorAnswer{
				geoKey: {
					compare: errors.WithAddedTags(errors.Error("geo error"), compareErrTag),
					force:   errors.Error("geo force error"),
				},
				authKey: {
					compare: errors.WithAddedTags(errors.Error("auth error"), goErrTag),
					force:   nil,
				},
				yandexUIDKey: {
					compare: nil,
				},
				localeKey: {
					compare: errors.WithAddedTags(errors.Error("locale error"), compareErrTag),
					force:   nil,
				},
				clidKey: {
					compare: errors.WithAddedTags(errors.Error("clid error"), perlErrTag),
				},
				timeKey: {
					compare: errors.WithAddedTags(errors.Error("time error"), goErrTag),
					force:   nil,
				},
			},
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 10,
					ComponentsPercentage: map[string]int{
						geoKey:       30,
						authKey:      25,
						yandexUIDKey: 50,
						localeKey:    15,
						clidKey:      20,
					},
				},
			},
			wantComponents: map[string]result{
				geoKey: {
					wantToForce: true,
					wantMetric:  errorMetric,
				},
				authKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
				yandexUIDKey: {
					wantToForce: false,
					wantMetric:  fromGoMetric,
				},
				localeKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
				clidKey: {
					wantToForce: false,
					wantMetric:  errorMetric,
				},
				timeKey: {
					wantToForce: true,
					wantMetric:  fromPerlMetric,
				},
			},
			wantErrs: []error{
				errors.WithAddedTags(errors.Errorf("couldn't get %s from Go: auth error", authKey)),
				errors.Errorf("%s not equal: geo error", geoKey),
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			mockedContextExpected := NewMockComparableContextExpected(ctrl)
			mockedContextGot := NewMockForceableContextGot(ctrl)
			mockedContextGot.EXPECT().GetRequest().Return(models.Request{
				Host: "yandex.ru",
			}).AnyTimes()
			mockedContextGot.EXPECT().GetLogger().Return(log3.NewLoggerStub()).AnyTimes()
			mockedContextGot.EXPECT().RefreshTimeLocation().Return().AnyTimes()
			mockedContextGot.EXPECT().RefreshMadmContent().Return().AnyTimes()
			comparators := make(map[string]comparator, len(tt.comparatorAnswers))
			for key, answer := range tt.comparatorAnswers {
				comparator := NewMockcomparator(ctrl)
				comparator.EXPECT().compare(mockedContextExpected, mockedContextGot).Return(answer.compare).Times(1)
				if tt.wantComponents[key].wantToForce {
					comparator.EXPECT().force(mockedContextExpected, mockedContextGot).Return(answer.force).Times(1)
				}
				comparator.EXPECT().incrementMetric(tt.wantComponents[key].wantMetric).Times(1)
				comparators[key] = comparator
			}

			randomizerMock := NewMockrandomizer(ctrl)
			randomizerMock.EXPECT().randomPercent().Return(tt.randomizerAnswer).Times(1)

			c := &contextComparator{
				comparators: comparators,
				randomizer:  randomizerMock,
			}

			gotErrs := c.compareContext(mockedContextExpected, mockedContextGot, tt.its)
			got := errorStr(errors.Collapse(gotErrs))
			want := errorStr(errors.Collapse(tt.wantErrs))

			assert.Equal(t, want, got)
		})
	}
}

func Test_contextComparator_addTags(t *testing.T) {
	testCases := []struct {
		name         string
		initMocks    func(*MockcomparableContext)
		isSecond     bool
		expectedTags []string
	}{
		{
			name: "not 3rd level domain",
			initMocks: func(ctx *MockcomparableContext) {
				ctx.EXPECT().GetRequest().Return(models.Request{
					Host: "yandex.com.tr",
				})
			},
		},
		{
			name: "3rd level domain",
			initMocks: func(ctx *MockcomparableContext) {
				ctx.EXPECT().GetRequest().Return(models.Request{
					Host: "something.yandex.com.tr",
				})
			},
			expectedTags: []string{
				tagThirdLevelDomain,
				tagComparator,
			},
		},
		{
			name: "3rd level domain",
			initMocks: func(ctx *MockcomparableContext) {
				ctx.EXPECT().GetRequest().Return(models.Request{
					Host: "something.yandex.com",
				})
			},
			expectedTags: []string{
				tagThirdLevelDomain,
				tagComparator,
			},
		},
		{
			name:     "second comparator",
			isSecond: true,
			initMocks: func(ctx *MockcomparableContext) {
				ctx.EXPECT().GetRequest().Return(models.Request{
					Host: "yandex.com",
				})
			},
			expectedTags: []string{
				tagComparatorSecond,
			},
		},
	}

	for _, testCase := range testCases {
		if testCase.expectedTags == nil {
			testCase.expectedTags = make([]string, 0)
		}
		t.Run(testCase.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			context := NewMockcomparableContext(ctrl)
			if testCase.initMocks != nil {
				testCase.initMocks(context)
			}

			c := &contextComparator{
				isSecond: testCase.isSecond,
			}
			err := fmt.Errorf("some error")
			err = c.addTags(err, context, []string{})

			require.Error(t, err)

			errWithTags, ok := err.(interface {
				GetTags() []string
			})
			if len(testCase.expectedTags) > 0 {
				require.True(t, ok)
				assert.ElementsMatch(t, testCase.expectedTags, errWithTags.GetTags())
			}
		})
	}
}

func Test_contextComparator_shouldLogError(t *testing.T) {
	tests := []struct {
		name     string
		its      its.ComparatorOptions
		random   int
		isSecond bool
		want     map[string]bool
	}{
		{
			name: "zero default percent, no component settings",
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 0,
				},
			},
			random: 42,
			want: map[string]bool{
				abFlagsKey:    false,
				sliceNamesKey: false,
			},
		},
		{
			name: "100 default percent",
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 100,
				},
			},
			random: 42,
			want: map[string]bool{
				abFlagsKey:      true,
				sliceNamesKey:   true,
				mordaContentKey: true,
				zoneKey:         true,
			},
		},
		{
			name: "some components with appropriate its option",
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 100,
					ComponentsPercentage: map[string]int{
						sliceNamesKey:   10,
						mordaContentKey: 25,
						zoneKey:         50,
					},
				},
			},
			random: 20,
			want: map[string]bool{
				abFlagsKey:      true,
				sliceNamesKey:   false,
				mordaContentKey: true,
				zoneKey:         true,
			},
		},
		{
			name: "all comparators with too less percent, extra components in its",
			its: its.ComparatorOptions{
				First: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 100,
					ComponentsPercentage: map[string]int{
						abFlagsKey:      10,
						sliceNamesKey:   15,
						mordaContentKey: 25,
						zoneKey:         50,
					},
				},
			},
			random: 20,
			want: map[string]bool{
				abFlagsKey:    false,
				sliceNamesKey: false,
			},
		},
		{
			name: "second comparator, enabled log",
			its: its.ComparatorOptions{
				Second: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 100,
				},
			},
			random:   42,
			isSecond: true,
			want: map[string]bool{
				abFlagsKey:    true,
				sliceNamesKey: true,
			},
		},
		{
			name: "second comparator, disabled log",
			its: its.ComparatorOptions{
				Second: its.ComparatorOptionsBase{
					DefaultComponentPercentage: 0,
				},
			},
			random:   42,
			isSecond: true,
			want: map[string]bool{
				abFlagsKey:    false,
				sliceNamesKey: false,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &contextComparator{
				isSecond: tt.isSecond,
			}

			for key, want := range tt.want {
				got := c.shouldLogError(key, tt.random, tt.its)
				assert.Equal(t, want, got)
			}
		})
	}
}

func Test_contextComparator_compareComponent(t *testing.T) {
	const testKey = "Test"

	type result struct {
		isEqual     bool
		wantToForce bool
		errMessage  string
	}

	tests := []struct {
		name             string
		comparatorAnswer error
		want             result
	}{
		{
			name:             "no comparator error",
			comparatorAnswer: nil,
			want: result{
				isEqual:     true,
				wantToForce: false,
			},
		},
		{
			name:             "comparator returns error from perl",
			comparatorAnswer: errors.WithAddedTags(errors.Error("error"), perlErrTag),
			want: result{
				isEqual:     false,
				wantToForce: false,
				errMessage:  fmt.Sprintf("couldn't get %s from Perl: error", testKey),
			},
		},
		{
			name:             "comparator returns error from Go",
			comparatorAnswer: errors.WithAddedTags(errors.Error("error"), goErrTag),
			want: result{
				isEqual:     false,
				wantToForce: true,
				errMessage:  fmt.Sprintf("couldn't get %s from Go: error", testKey),
			},
		},
		{
			name:             "comparator returns compare error",
			comparatorAnswer: errors.WithAddedTags(errors.Error("error"), compareErrTag),
			want: result{
				isEqual:     false,
				wantToForce: true,
				errMessage:  fmt.Sprintf("%s not equal: error", testKey),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			mockedContextExpected := NewMockComparableContextExpected(ctrl)
			mockedContextGot := NewMockForceableContextGot(ctrl)
			mockedContextGot.EXPECT().GetLogger().Return(log3.NewLoggerStub()).AnyTimes()

			comparatorMock := NewMockcomparator(ctrl)
			comparatorMock.EXPECT().compare(mockedContextExpected, mockedContextGot).Return(tt.comparatorAnswer).Times(1)

			c := &contextComparator{
				comparators: map[string]comparator{testKey: comparatorMock},
			}

			got, err := c.compareComponent(testKey, mockedContextExpected, mockedContextGot)
			errMsg := errorStr(err)

			assert.Equal(t, tt.want.isEqual, got.isEqual)
			assert.Equal(t, tt.want.wantToForce, got.wantToForce)
			assert.Equal(t, tt.want.errMessage, errMsg)
		})
	}
}

func Test_contextComparator_forceComponent(t *testing.T) {
	const testKey = "Test"

	tests := []struct {
		name          string
		compareResult compareResult
		forceError    error
		wantMetric    string
	}{
		{
			name: "equal components",
			compareResult: compareResult{
				isEqual: true,
			},
			wantMetric: fromGoMetric,
		},
		{
			name: "want to force (error from perl)",
			compareResult: compareResult{
				isEqual:     false,
				wantToForce: false,
			},
			wantMetric: errorMetric,
		},
		{
			name: "force ok",
			compareResult: compareResult{
				isEqual:     false,
				wantToForce: true,
			},
			wantMetric: fromPerlMetric,
		},
		{
			name: "failed to force",
			compareResult: compareResult{
				isEqual:     false,
				wantToForce: true,
			},
			forceError: assert.AnError,
			wantMetric: errorMetric,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			mockedContextExpected := NewMockComparableContextExpected(ctrl)
			mockedContextGot := NewMockForceableContextGot(ctrl)
			mockedContextGot.EXPECT().GetLogger().Return(log3.NewLoggerStub()).AnyTimes()

			comparatorMock := NewMockcomparator(ctrl)
			comparatorMock.EXPECT().force(mockedContextExpected, mockedContextGot).Return(tt.forceError).AnyTimes()
			comparatorMock.EXPECT().incrementMetric(tt.wantMetric).Times(1)

			c := &contextComparator{
				comparators: map[string]comparator{testKey: comparatorMock},
			}

			c.forceComponent(testKey, mockedContextExpected, mockedContextGot, tt.compareResult)
		})
	}
}

func errorStr(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}
