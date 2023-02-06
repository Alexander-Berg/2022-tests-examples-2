package mordazone

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/country"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
)

func Test_parser_extractGeoInfo(t *testing.T) {
	testCases := []struct {
		name     string
		geos     []uint32
		isCrimea bool
	}{
		{
			name: "empty geo",
		},
		{
			name: "without crimea",
			geos: []uint32{1, 2, 3},
		},
		{
			name:     "with crimea",
			geos:     []uint32{1, 2, 3, 977},
			isCrimea: true,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			appSearchShortChecker := NewMockappSearchShortChecker(ctl)
			geoKeeper := NewMockgeoKeeper(ctl)
			appInfoGetter := NewMockappInfoGetter(ctl)
			domainGetter := NewMockdomainGetter(ctl)
			spokDomainsGetter := NewMockspokSettings(ctl)
			spokDomainsGetter.EXPECT().GetSpokDomains().Return([]string{}).AnyTimes()
			deviceSetterMock := NewMockdeviceSetter(ctl)

			madmOptions := exports.Options{}

			expectedGeo := models.Geo{
				Parents: testCase.geos,
			}
			geoKeeper.EXPECT().GetGeo().Return(expectedGeo)

			p := NewParser(log3.NewLoggerStub(), requestGetter, geoKeeper, appInfoGetter, appSearchShortChecker,
				madmOptions, spokDomainsGetter, domainGetter, deviceSetterMock, NewMockmordaZoneMetrics(ctl))
			geoInfo := p.extractGeoInfo()
			geosSlice := make([]uint32, 0, len(geoInfo.geosSet))
			for id := range geoInfo.geosSet {
				geosSlice = append(geosSlice, uint32(id))
			}
			geosSlice2 := make([]uint32, 0, len(geoInfo.geos))
			for _, id := range geoInfo.geos {
				geosSlice2 = append(geosSlice2, uint32(id))
			}
			assert.ElementsMatch(t, testCase.geos, geosSlice)
			assert.ElementsMatch(t, testCase.geos, geosSlice2)
			assert.Equal(t, testCase.isCrimea, geoInfo.isCrimea())
		})
	}
}

func Test_parser_getValidZones(t *testing.T) {
	testCases := []struct {
		name                   string
		isAPIAndroidWidgetOld  bool
		apiInfo                models.APIInfo
		country                country.Country
		additionalZonesMapping map[uint32]string
		ppUzOption             bool
		expectedOutput         readonlyStringSet
	}{
		{
			name:           "plain",
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone),
		},
		{
			name: "with comTr for old android widget without country",
			apiInfo: models.APIInfo{
				Name: "old_android_widget",
			},
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone, comTrZone),
		},
		{
			name: "without comTr for old android widget with country",
			apiInfo: models.APIInfo{
				Name: "old_android_widget",
			},
			country:        country.RU,
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone),
		},
		{
			name: "with additional zones from mapping",
			additionalZonesMapping: map[uint32]string{
				1: ruZone,
				2: ruZone,
				3: coZone,
			},
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone, coZone),
		},
		{
			name:           "with uz from options",
			ppUzOption:     true,
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone, uzZone),
		},
		{
			name: "with everything at once",
			apiInfo: models.APIInfo{
				Name: "old_android_widget",
			},
			ppUzOption: true,
			additionalZonesMapping: map[uint32]string{
				1: ruZone,
				2: ruZone,
				3: coZone,
			},
			expectedOutput: common.NewStringSet(ruZone, uaZone, kzZone, byZone, comTrZone, coZone, uzZone),
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			appSearchShortChecker := NewMockappSearchShortChecker(ctl)
			geoKeeper := NewMockgeoKeeper(ctl)
			appInfoGetter := NewMockappInfoGetter(ctl)
			domainGetter := NewMockdomainGetter(ctl)
			spokDomainsGetter := NewMockspokSettings(ctl)
			spokDomainsGetter.EXPECT().GetSpokDomains().Return([]string{}).AnyTimes()
			deviceSetterMock := NewMockdeviceSetter(ctl)

			madmOptions := exports.Options{
				MordaZoneOptions: exports.MordaZoneOptions{
					PPUz: testCase.ppUzOption,
				},
			}

			p := NewParser(log3.NewLoggerStub(), requestGetter, geoKeeper, appInfoGetter, appSearchShortChecker,
				madmOptions, spokDomainsGetter, domainGetter, deviceSetterMock, NewMockmordaZoneMetrics(ctl))
			got := p.getValidZones(testCase.apiInfo, testCase.country, testCase.additionalZonesMapping)

			assert.Equal(t, testCase.expectedOutput, got)
		})
	}
}

func Test_parser_getMordaZonesForSearchShort(t *testing.T) {
	type result int
	const (
		empty result = iota
		nonEmpty
		eu
		nonEU
	)
	testCases := []struct {
		name                                   string
		isAPISearchShort                       bool
		optionsDisableSpokDomainMordaZoneAllow bool
		optionsEnablePPEuHome64280             bool
		expectedResult                         result
	}{
		{
			name: "plain",
		},
		{
			name:                                   "empty when disabled",
			optionsDisableSpokDomainMordaZoneAllow: true,
		},
		{
			name:             "nonempty when not disabled and api is search short",
			isAPISearchShort: true,
			expectedResult:   nonEmpty,
		},
		{
			name:                       "eu when eu is enabled when not disabled and api is search short",
			isAPISearchShort:           true,
			optionsEnablePPEuHome64280: true,
			expectedResult:             eu,
		},
		{
			name:             "noneu when eu is not enabled when not disabled and api is search short",
			isAPISearchShort: true,
			expectedResult:   nonEU,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			geoKeeper := NewMockgeoKeeper(ctl)
			appInfoGetter := NewMockappInfoGetter(ctl)
			domainGetter := NewMockdomainGetter(ctl)
			spokDomainsGetter := NewMockspokSettings(ctl)
			spokDomainsGetter.EXPECT().GetSpokDomains().Return([]string{}).AnyTimes()
			deviceSetterMock := NewMockdeviceSetter(ctl)

			madmOptions := exports.Options{
				MordaZoneOptions: exports.MordaZoneOptions{
					DisableSpokDomainMordaZoneAllow: testCase.optionsDisableSpokDomainMordaZoneAllow,
					EnablePPEuHome64280:             testCase.optionsEnablePPEuHome64280,
				},
			}

			appSearchShortChecker := NewMockappSearchShortChecker(ctl)
			appSearchShortChecker.EXPECT().IsAppSearchShort(gomock.Any(), gomock.Any(), gomock.Any()).
				Return(testCase.isAPISearchShort).AnyTimes()

			p := NewParser(log3.NewLoggerStub(), requestGetter, geoKeeper, appInfoGetter, appSearchShortChecker,
				madmOptions, spokDomainsGetter, domainGetter, deviceSetterMock, NewMockmordaZoneMetrics(ctl))
			got := p.getMordaZonesForSearchShort(models.AppInfo{}, models.APIInfo{}, []uint32{})

			switch testCase.expectedResult {
			case empty:
				assert.Empty(t, got)
			case nonEmpty:
				assert.NotEmpty(t, got)
			case eu:
				assert.Equal(t, mordaZonesForSearchShortEU, got)
			case nonEU:
				assert.Equal(t, mordaZonesForSearchShortNonEU, got)
			}
		})
	}
}

func Test_parser_selectNewZone(t *testing.T) {
	geoInfoCrimea := geoInfo{
		geosSet: map[uint32]struct{}{
			977: struct{}{},
		},
	}
	testCases := []struct {
		name                     string
		geoInfo                  geoInfo
		parsedCountry            country.Country
		mordaZonesForSearchShort map[uint32]string

		expectedZone string
	}{
		{
			name: "plain",
			geoInfo: geoInfo{
				geosSet: map[uint32]struct{}{},
			},
		},
		{
			name:          "return nothing for crimea if parsed country is not ru or ua",
			geoInfo:       geoInfoCrimea,
			parsedCountry: country.UZ,
		},
		{
			name:    "return nothing for crimea if parsed country is empty",
			geoInfo: geoInfoCrimea,
		},
		{
			name:          "return ru for crimea if parsed country is ru",
			geoInfo:       geoInfoCrimea,
			parsedCountry: country.RU,
			expectedZone:  country.RU.ISOCode(),
		},
		{
			name:          "return ua for crimea if parsed country is ua",
			geoInfo:       geoInfoCrimea,
			parsedCountry: country.UA,
			expectedZone:  country.UA.ISOCode(),
		},
		{
			name: "return zone from static mapping first for non-crimea",
			geoInfo: geoInfo{
				geosSet: map[uint32]struct{}{999: struct{}{}, 149: struct{}{}},
			},
			mordaZonesForSearchShort: map[uint32]string{999: "somezone"},
			expectedZone:             countryIDToMordaZoneMapping[149],
		},
		{
			name: "return zone from provided mapping for non-crimea if there's no match in first mapping",
			geoInfo: geoInfo{
				geosSet: map[uint32]struct{}{999: struct{}{}, 150: struct{}{}},
			},
			mordaZonesForSearchShort: map[uint32]string{999: "somezone"},
			expectedZone:             "somezone",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			appSearchShortChecker := NewMockappSearchShortChecker(ctl)
			geoKeeper := NewMockgeoKeeper(ctl)
			appInfoGetter := NewMockappInfoGetter(ctl)
			domainGetter := NewMockdomainGetter(ctl)
			spokDomainsGetter := NewMockspokSettings(ctl)
			spokDomainsGetter.EXPECT().GetSpokDomains().Return([]string{}).AnyTimes()
			deviceSetterMock := NewMockdeviceSetter(ctl)

			madmOptions := exports.Options{}

			p := NewParser(log3.NewLoggerStub(), requestGetter, geoKeeper, appInfoGetter, appSearchShortChecker,
				madmOptions, spokDomainsGetter, domainGetter, deviceSetterMock, NewMockmordaZoneMetrics(ctl))

			got := p.selectNewZone(testCase.geoInfo, testCase.parsedCountry, testCase.mordaZonesForSearchShort)

			assert.Equal(t, testCase.expectedZone, got)
		})
	}
}

func Test_parser_overrideForAPI(t *testing.T) {
	inputStub := models.MordaZone{
		Value: "a",
	}
	testCases := []struct {
		name    string
		country country.Country

		geoParentIDs []uint32

		apiInfo          models.APIInfo
		isAPISearchShort bool

		prohibitedZonesOption string

		input          models.MordaZone
		expectedOutput models.MordaZone
	}{
		{
			name:         "no override for old android widget if parsed country is uz",
			country:      "uz",
			geoParentIDs: []uint32{},
			apiInfo: models.APIInfo{
				Name: "old_android_widget",
			},
			input:          inputStub,
			expectedOutput: inputStub,
		},
		{
			name:         "no override for old android widget if isCrimea is true",
			geoParentIDs: []uint32{977},
			apiInfo: models.APIInfo{
				Name: "old_android_widget",
			},
			input:          inputStub,
			expectedOutput: inputStub,
		},
		{
			name:         "no override if resulting zone is not valid",
			geoParentIDs: []uint32{983},
			apiInfo: models.APIInfo{
				Name: "search",
			},
			isAPISearchShort: false,
			input:            inputStub,
			expectedOutput:   inputStub,
		},
		{
			name:         "override if resulting zone is valid",
			geoParentIDs: []uint32{149},
			apiInfo: models.APIInfo{
				Name: "search",
			},
			isAPISearchShort: false,

			input: inputStub,
			expectedOutput: models.MordaZone{
				Value: "by",
			},
		},
		{
			name:         "ua overridden to ru by prohibited option",
			geoParentIDs: []uint32{187},
			apiInfo: models.APIInfo{
				Name: "search",
			},
			isAPISearchShort:      false,
			prohibitedZonesOption: "ua",

			input: inputStub,
			expectedOutput: models.MordaZone{
				Value: "ru",
			},
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			geoKeeper := NewMockgeoKeeper(ctl)
			appInfoGetter := NewMockappInfoGetter(ctl)
			domainGetter := NewMockdomainGetter(ctl)
			appInfoGetter.EXPECT().GetAppInfo().Return(models.AppInfo{
				Country: testCase.country,
			}).AnyTimes()
			spokDomainsGetter := NewMockspokSettings(ctl)
			spokDomainsGetter.EXPECT().GetSpokDomains().Return([]string{}).AnyTimes()
			deviceSetterMock := NewMockdeviceSetter(ctl)

			madmOptions := exports.Options{
				MordaZoneOptions: exports.MordaZoneOptions{
					PPForceMordaZoneRu: testCase.prohibitedZonesOption,
				},
			}

			expectedGeo := models.Geo{
				Parents: testCase.geoParentIDs,
			}
			geoKeeper.EXPECT().GetGeo().Return(expectedGeo).AnyTimes()

			appSearchShortChecker := NewMockappSearchShortChecker(ctl)
			appSearchShortChecker.EXPECT().IsAppSearchShort(gomock.Any(), gomock.Any(), gomock.Any()).
				Return(testCase.isAPISearchShort).AnyTimes()

			p := NewParser(log3.NewLoggerStub(), requestGetter, geoKeeper, appInfoGetter, appSearchShortChecker,
				madmOptions, spokDomainsGetter, domainGetter, deviceSetterMock, NewMockmordaZoneMetrics(ctl))

			overriden := p.overrideForAPI(testCase.input, appInfoGetter.GetAppInfo(), testCase.apiInfo)

			assert.Equal(t, testCase.expectedOutput, overriden)
		})
	}
}

func Test_parser_getProhinitedZones(t *testing.T) {
	tests := []struct {
		name   string
		option string
		want   readonlyStringSet
	}{
		{
			name: "empty option",
			want: common.NewStringSet(),
		},
		{
			name:   "one zone",
			option: "ua",
			want:   common.NewStringSet("ua"),
		},
		{
			name:   "several zones",
			option: "ua, kz, com.tr",
			want:   common.NewStringSet("ua", "kz", "com.tr"),
		},
		{
			name:   "separated differently",
			option: "   ua,kz;;,com.tr ; uz net \t",
			want:   common.NewStringSet("ua", "kz", "com.tr", "uz", "net"),
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				madmOptions: exports.Options{
					MordaZoneOptions: exports.MordaZoneOptions{
						PPForceMordaZoneRu: tt.option,
					},
				},
			}
			got := p.getProhibitedZones()
			assert.Equal(t, tt.want, got)
		})
	}
}
