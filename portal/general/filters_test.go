package storage

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2/internal/requestcontext"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2/madmtypes"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	basemocks "a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

func Test_filterEnabled(t *testing.T) {
	var (
		item = Item{
			common: newCommonValues(),
		}
		ctx  requestcontext.Context
		args madm.ArgsConfig
	)
	ok, err := filterEnabled(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.Enabled = false
	ok, err = filterEnabled(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)

	item.common.Enabled = true
	item.common.Disabled = true
	ok, err = filterEnabled(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)
}

func Test_filterTargetingInfo(t *testing.T) {
	item := Item{
		common: newCommonValues(),
	}
	args := madm.ArgsConfig{}
	baseCtx := &basemocks.Base{}
	baseCtx.On("GetBigBOrErr").Return(models.BigB{TargetingInfo: models.TargetingInfo{
		PromoGroups: common.NewStringSet("1:1", "2:2", "3:3"),
	}}, nil)
	ctx := requestcontext.NewContext(nil, baseCtx)

	ok, err := filterTargetingInfo(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.BKTag = ptr.String("1:1")
	ok, err = filterTargetingInfo(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.BKTag = ptr.String("4:4")
	ok, err = filterTargetingInfo(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)

	item.common.BKTag = ptr.String("1:1&4:4,2:2 & 3:3, 5:5")
	ok, err = filterTargetingInfo(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.BKTagExcept = ptr.String("1:1&2:2")
	ok, err = filterTargetingInfo(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)
}

func Test_filterDated(t *testing.T) {
	for _, tc := range filterDatedTestCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			args := madm.ArgsConfig{Dated: tc.Kind}
			baseCtx := &basemocks.Base{}
			baseCtx.On("GetTime").Return(&models.TimeData{
				MoscowTime: tc.MoscowTime,
				UserTime:   tc.UserTime,
			}).Once()
			defer baseCtx.AssertExpectations(t)
			requestCtx := requestcontext.NewContext(nil, baseCtx)
			var timeLocal string
			if tc.ItemTimeLocal {
				timeLocal = "local"
			}
			item := Item{common: commonValues{
				From:      tc.From,
				To:        tc.To,
				TimeLocal: timeLocal,
			}}
			actual, err := filterDated(requestCtx, item, args)
			require.NoError(t, err)
			require.Equal(t, tc.Expected, actual)
		})
	}
}

func Test_filterYandex(t *testing.T) {
	for _, tc := range filterYandexTestCases {
		tc := tc
		t.Run(fmt.Sprintf("yandex=%v, is_internal=%v", tc.Yandex, tc.IsInternal), func(t *testing.T) {
			var args madm.ArgsConfig
			baseCtx := &basemocks.Base{}
			if tc.Yandex {
				baseCtx.On("GetRequest").Return(models.Request{
					IsInternal: tc.IsInternal,
				}).Once()
			}
			defer baseCtx.AssertExpectations(t)
			requestCtx := requestcontext.NewContext(nil, baseCtx)
			item := Item{common: commonValues{Yandex: tc.Yandex}}
			actual, err := filterYandex(requestCtx, item, args)
			require.NoError(t, err)
			require.Equal(t, tc.Expected, actual)
		})
	}
}

func Test_filterFiltered(t *testing.T) {
	var (
		ff   fakeFilter
		item Item
		args madm.ArgsConfig
		ctx  = requestcontext.NewContext(ff, nil)
	)

	ok, err := filterFiltered(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.Filter = ptr.String("42")
	ok, err = filterFiltered(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)

	item.common.Filter = ptr.String(fakeFilterName)
	ok, err = filterFiltered(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)
}

func Test_filterExpExcept(t *testing.T) {
	var (
		args madm.ArgsConfig
		item Item
		ctx  = requestcontext.NewContextFromSources(requestcontext.WithABFlags(fakeABFlagsGetter{
			flags: map[string]string{
				"1":            "0",
				"2":            "0",
				"3":            "0",
				fakeEnabledExp: "1",
			},
		}))
	)

	ok, err := filterExpExcept(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.ExpExcept = []string{"1", "2", "3"}
	ok, err = filterExpExcept(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.ExpExcept = []string{"1", "2", "3", fakeEnabledExp}
	ok, err = filterExpExcept(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)
}

func Test_filterExp(t *testing.T) {
	var (
		args madm.ArgsConfig
		item Item
		ctx  = requestcontext.NewContextFromSources(requestcontext.WithABFlags(fakeABFlagsGetter{
			flags: map[string]string{
				"1":            "0",
				"2":            "0",
				"3":            "0",
				fakeEnabledExp: "1",
			},
		}))
	)

	ok, err := filterExp(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.Exp = ptr.String("1")
	ok, err = filterExp(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)

	item.common.Exp = ptr.String(fakeEnabledExp)
	ok, err = filterExp(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)
}

func Test_filterTimed(t *testing.T) {
	for _, tc := range filterTimedTestCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			var args madm.ArgsConfig
			baseCtx := &basemocks.Base{}
			baseCtx.On("GetTime").Return(&models.TimeData{
				UserTime: tc.UserTime,
			}).Once()
			defer baseCtx.AssertExpectations(t)
			requestCtx := requestcontext.NewContext(nil, baseCtx)
			item := Item{common: commonValues{
				TimeFrom: tc.TimeFrom,
				TimeTill: tc.TimeTill,
			}}
			actual, err := filterTimed(requestCtx, item, args)
			require.NoError(t, err)
			require.Equal(t, tc.Expected, actual)
		})
	}
}

func Test_filterWeekDay(t *testing.T) {
	for _, tc := range filterWeekDayTestCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			var args madm.ArgsConfig
			baseCtx := &basemocks.Base{}
			baseCtx.On("GetTime").Return(&models.TimeData{
				UserTime:    tc.UserTime,
				HolidaysYTT: tc.YTT,
			})
			requestCtx := requestcontext.NewContext(nil, baseCtx)
			item := Item{common: commonValues{
				WeekDay: tc.Settings,
			}}
			actual, err := filterWeekDay(requestCtx, item, args)
			require.NoError(t, err)
			require.Equal(t, tc.Expected, actual)
		})
	}
}

func Test_filterApp(t *testing.T) {
	for _, tc := range filterAppTestCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			args := madm.ArgsConfig{
				AppTablet:    tc.ArgAppTablet,
				AppLikePhone: tc.ArgAppLikePhone,
			}
			baseCtx := &basemocks.Base{}
			baseCtx.On("GetAppInfo").Return(tc.AppInfo).Once()
			isTabletStr := "false"
			if tc.IsTablet {
				isTabletStr = "true"
			}
			baseCtx.On("GetDevice").Return(models.Device{BrowserDesc: &models.BrowserDesc{
				Traits: uatraits.Traits{
					"isTablet": isTabletStr,
				},
			}}).Once()
			baseCtx.On("GetMadmOptions").Return(
				exports.Options{
					BackendSetup: exports.BackendSetupOptions{
						DisableTabletLikePhone: tc.DisableTabletLikePhone,
					},
				})
			requestCtx := requestcontext.NewContext(nil, baseCtx)
			item := Item{common: commonValues{
				AppPlatform:   tc.AppPlatform,
				AppVersionMin: tc.AppVersionMin,
				AppVersionMax: tc.AppVersionMax,
				OSVersionMin:  tc.OSVersionMin,
				OSVersionMax:  tc.OSVersionMax,
				AppIDs:        tc.AppIDs,
			}}
			actual, err := filterApp(requestCtx, item, args)
			require.NoError(t, err)
			require.Equal(t, tc.Expected, actual)
		})
	}
}

func Test_filterBK(t *testing.T) {
	item := Item{
		common: newCommonValues(),
	}
	args := madm.ArgsConfig{}
	baseCtx := &basemocks.Base{}
	baseCtx.On("GetYabsOrErr").Return(models.Yabs{BKFlags: map[string]models.BKFlag{
		"1": {},
		"2": {},
	}}, nil)
	ctx := requestcontext.NewContext(nil, baseCtx)

	ok, err := filterBK(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.BK = ptr.String("1")
	ok, err = filterBK(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.BK = ptr.String("0")
	ok, err = filterBK(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)
}

func Test_filterChild(t *testing.T) {
	item := Item{
		common: newCommonValues(),
	}
	args := madm.ArgsConfig{}
	baseCtx := &basemocks.Base{}
	baseCtx.On("GetAuthOrErr").Return(models.Auth{IsChildAccount: false}, nil).Twice()
	baseCtx.On("GetMadmOptions").Return(exports.Options{BackendSetup: exports.BackendSetupOptions{EnableChildAccount: true}})
	ctx := requestcontext.NewContext(nil, baseCtx)

	ok, err := filterChild(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.Child = "child_only"
	ok, err = filterChild(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)

	item.common.Child = "adult_only"
	ok, err = filterChild(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	baseCtx.On("GetAuthOrErr").Return(models.Auth{IsChildAccount: true}, nil).Twice()

	item.common.Child = "child_only"
	ok, err = filterChild(ctx, item, args)
	require.NoError(t, err)
	require.True(t, ok)

	item.common.Child = "adult_only"
	ok, err = filterChild(ctx, item, args)
	require.NoError(t, err)
	require.False(t, ok)
}

var filterDatedTestCases = []struct {
	Name          string
	Kind          *madm.TimeKind
	UserTime      time.Time
	MoscowTime    time.Time
	ItemTimeLocal bool
	From          *time.Time
	To            *time.Time
	Expected      bool
}{
	{
		Name:     "empty from and to",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		Expected: true,
	},
	{
		Name:     "match from",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		From:     ptr.Time(time.Now().Add(-time.Hour)),
		Expected: true,
	},
	{
		Name:     "doesn't match from",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		From:     ptr.Time(time.Now().Add(time.Hour)),
		Expected: false,
	},
	{
		Name:     "match to",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		To:       ptr.Time(time.Now().Add(time.Hour)),
		Expected: true,
	},
	{
		Name:     "doesn't match to",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		To:       ptr.Time(time.Now().Add(-time.Hour)),
		Expected: false,
	},
	{
		Name:     "match both",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		From:     ptr.Time(time.Now().Add(-time.Hour)),
		To:       ptr.Time(time.Now().Add(time.Hour)),
		Expected: true,
	},
	{
		Name:       "match user time",
		Kind:       ptrTimeKind(madm.UserTime),
		UserTime:   time.Now(),
		MoscowTime: time.Now().Add(-3 * time.Hour),
		From:       ptr.Time(time.Now().Add(-time.Hour)),
		To:         ptr.Time(time.Now().Add(time.Hour)),
		Expected:   true,
	},
	{
		Name:       "doesn't match user time",
		Kind:       ptrTimeKind(madm.UserTime),
		MoscowTime: time.Now(),
		UserTime:   time.Now().Add(-3 * time.Hour),
		From:       ptr.Time(time.Now().Add(-time.Hour)),
		To:         ptr.Time(time.Now().Add(time.Hour)),
		Expected:   false,
	},
	{
		Name:       "match moscow time",
		Kind:       ptrTimeKind(madm.MoscowTime),
		MoscowTime: time.Now(),
		UserTime:   time.Now().Add(-3 * time.Hour),
		From:       ptr.Time(time.Now().Add(-time.Hour)),
		To:         ptr.Time(time.Now().Add(time.Hour)),
		Expected:   true,
	},
	{
		Name:          "match user time forced",
		Kind:          ptrTimeKind(madm.MoscowTime),
		UserTime:      time.Now(),
		MoscowTime:    time.Now().Add(-3 * time.Hour),
		From:          ptr.Time(time.Now().Add(-time.Hour)),
		To:            ptr.Time(time.Now().Add(time.Hour)),
		ItemTimeLocal: true,
		Expected:      true,
	},
	{
		Name:     "match reverse interval",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now().Add(-2 * time.Hour),
		To:       ptr.Time(time.Now().Add(-time.Hour)),
		From:     ptr.Time(time.Now().Add(time.Hour)),
		Expected: true,
	},
	{
		Name:     "doesn't match reverse interval",
		Kind:     ptrTimeKind(madm.UserTime),
		UserTime: time.Now(),
		To:       ptr.Time(time.Now().Add(-time.Hour)),
		From:     ptr.Time(time.Now().Add(time.Hour)),
		Expected: false,
	},
}

var filterYandexTestCases = []struct {
	Yandex     bool
	IsInternal bool
	Expected   bool
}{
	{
		Yandex:     false,
		IsInternal: false,
		Expected:   true,
	},
	{
		Yandex:     false,
		IsInternal: true,
		Expected:   true,
	},
	{
		Yandex:     true,
		IsInternal: false,
		Expected:   false,
	},
	{
		Yandex:     true,
		IsInternal: true,
		Expected:   true,
	},
}

var filterTimedTestCases = []struct {
	Name     string
	UserTime time.Time
	TimeFrom *madmtypes.TimeOfDay
	TimeTill *madmtypes.TimeOfDay
	Expected bool
}{
	{
		Name:     "no time restrictions",
		UserTime: fakeNow,
		Expected: true,
	},
	{
		Name:     "match from",
		UserTime: fakeNow,
		TimeFrom: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(-time.Hour))),
		Expected: true,
	},
	{
		Name:     "doesn't match from",
		UserTime: fakeNow,
		TimeFrom: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(time.Hour))),
		Expected: false,
	},
	{
		Name:     "match till",
		UserTime: fakeNow,
		TimeTill: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(time.Hour))),
		Expected: true,
	},
	{
		Name:     "doesn't match till",
		UserTime: fakeNow,
		TimeTill: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(-time.Hour))),
		Expected: false,
	},
	{
		Name:     "match both",
		UserTime: fakeNow,
		TimeFrom: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(-time.Hour))),
		TimeTill: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(time.Hour))),
		Expected: true,
	},
	{
		Name:     "till fix 00:00",
		UserTime: fakeNow,
		TimeFrom: ptrTimeOfDay(madmtypes.NewTimeOfDayFromTime(fakeNow.Add(-time.Hour))),
		TimeTill: ptrTimeOfDay(madmtypes.NewTimeOfDay(0, 0, 0)),
		Expected: true,
	},
}

var filterWeekDayTestCases = []struct {
	Name     string
	Settings []string
	UserTime time.Time
	YTT      models.HolidaysYTT
	Expected bool
}{
	{
		Name:     "no settings",
		Expected: true,
	},
	{
		Name:     "holiday",
		Settings: []string{"holiday"},
		YTT:      models.HolidaysYTT{Today: true},
		Expected: true,
	},
	{
		Name:     "before_holiday",
		Settings: []string{"before_holiday"},
		YTT:      models.HolidaysYTT{Tomorrow: true},
		Expected: true,
	},
	{
		Name:     "workday",
		Settings: []string{"workday"},
		YTT:      models.HolidaysYTT{Today: true},
		UserTime: monday,
		Expected: false,
	},
	{
		Name:     "weekend",
		Settings: []string{"weekend"},
		UserTime: sunday,
		Expected: true,
	},
	{
		Name:     "workday",
		Settings: []string{"workday"},
		UserTime: monday,
		Expected: true,
	},
	{
		Name:     "sunday",
		Settings: []string{"7"},
		UserTime: sunday,
		Expected: true,
	},
	{
		Name:     "match weekday",
		Settings: []string{"1", "3"},
		UserTime: monday,
		Expected: true,
	},
	{
		Name:     "doesn't match weekday",
		Settings: []string{"1", "3"},
		UserTime: friday,
		Expected: false,
	},
}

var filterAppTestCases = []struct {
	Name                   string
	ArgAppTablet           bool
	ArgAppLikePhone        bool
	AppInfo                models.AppInfo
	DisableTabletLikePhone bool
	IsTablet               bool
	AppPlatform            *string
	AppVersionMin          *int
	AppVersionMax          *int
	OSVersionMin           *string
	OSVersionMax           *string
	AppIDs                 []string
	Expected               bool
}{
	{
		Name:     "empty",
		Expected: true,
	},
	{
		Name: "match android",
		AppInfo: models.AppInfo{
			Platform: "android",
		},
		IsTablet:    false,
		AppPlatform: ptr.String("android"),
		Expected:    true,
	},
	{
		Name: "match android tablet",
		AppInfo: models.AppInfo{
			Platform: "android",
		},
		IsTablet:    true,
		AppPlatform: ptr.String("android"),
		Expected:    true,
	},
	{
		Name: "doesn't match android tablet",
		AppInfo: models.AppInfo{
			Platform: "android",
		},
		IsTablet:               true,
		DisableTabletLikePhone: true,
		ArgAppTablet:           true,
		AppPlatform:            ptr.String("android"),
		Expected:               false,
	},
	{
		Name: "doesn't match platform",
		AppInfo: models.AppInfo{
			Platform: "ios",
		},
		IsTablet:    true,
		AppPlatform: ptr.String("android"),
		Expected:    false,
	},
	{
		Name: "match app version",
		AppInfo: models.AppInfo{
			Platform: "android",
			Version:  "1",
		},
		AppPlatform:   ptr.String("android"),
		AppVersionMin: ptr.Int(0),
		AppVersionMax: ptr.Int(2),
		Expected:      true,
	},
	{
		Name: "doesn't match app version min",
		AppInfo: models.AppInfo{
			Platform: "android",
			Version:  "1",
		},
		AppPlatform:   ptr.String("android"),
		AppVersionMin: ptr.Int(2),
		AppVersionMax: ptr.Int(3),
		Expected:      false,
	},
	{
		Name: "doesn't match app version max",
		AppInfo: models.AppInfo{
			Platform: "android",
			Version:  "1",
		},
		AppPlatform:   ptr.String("android"),
		AppVersionMin: ptr.Int(0),
		AppVersionMax: ptr.Int(1),
		Expected:      false,
	},
	{
		Name: "match os version",
		AppInfo: models.AppInfo{
			Platform:  "android",
			OSVersion: "1.2.3",
		},
		AppPlatform:  ptr.String("android"),
		OSVersionMin: ptr.String("1.2.2"),
		OSVersionMax: ptr.String("1.3.0"),
		Expected:     true,
	},
	{
		Name: "doesn't match os version min",
		AppInfo: models.AppInfo{
			Platform:  "android",
			OSVersion: "1.2.3",
		},
		AppPlatform:  ptr.String("android"),
		OSVersionMin: ptr.String("1.2.4"),
		OSVersionMax: ptr.String("1.3.0"),
		Expected:     false,
	},
	{
		Name: "doesn't match os version max",
		AppInfo: models.AppInfo{
			Platform:  "android",
			OSVersion: "1.2.3",
		},
		AppPlatform:  ptr.String("android"),
		OSVersionMin: ptr.String("1.2.0"),
		OSVersionMax: ptr.String("1.2.3"),
		Expected:     false,
	},
	{
		Name: "match app id",
		AppInfo: models.AppInfo{
			Platform: "android",
			ID:       "foo",
		},
		AppPlatform: ptr.String("android"),
		AppIDs:      []string{"bar", "foo"},
		Expected:    true,
	},
	{
		Name: "doesn't match app id",
		AppInfo: models.AppInfo{
			Platform: "android",
			ID:       "foo",
		},
		AppPlatform: ptr.String("android"),
		Expected:    false,
		AppIDs:      []string{"bar", "baz"},
	},
}

var (
	monday = time.Date(2022, 03, 21, 0, 0, 0, 0, time.UTC)
	friday = time.Date(2022, 03, 25, 0, 0, 0, 0, time.UTC)
	sunday = time.Date(2022, 03, 27, 0, 0, 0, 0, time.UTC)
)

var fakeNow = time.Date(2022, 03, 21, 11, 22, 33, 0, time.UTC)

func ptrTimeKind(kind madm.TimeKind) *madm.TimeKind {
	return &kind
}

func ptrTimeOfDay(t madmtypes.TimeOfDay) *madmtypes.TimeOfDay {
	return &t
}

const (
	fakeFilterName = "foobar"
)

type fakeFilter struct{}

func (f fakeFilter) Filter(name string) bool {
	return name == fakeFilterName
}

const (
	fakeEnabledExp = "42"
)

type fakeABFlagsGetter struct {
	flags map[string]string
}

func (f fakeABFlagsGetter) GetFlagsOrErr() (models.ABFlags, error) {
	return models.ABFlags{
		Flags: f.flags,
	}, nil
}
