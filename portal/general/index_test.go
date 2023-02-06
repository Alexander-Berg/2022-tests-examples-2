package storage

import (
	"reflect"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	gb "a.yandex-team.ru/library/go/yandex/geobase"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2/internal/requestcontext"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2/madmtypes"
	"a.yandex-team.ru/portal/avocado/libs/utils/madmcontent"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/contexts"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

var (
	_ Index = &indexData{}
	_ Index = &indexByField{}
)

func TestIndexData_Add(t *testing.T) {
	data := indexData{}
	err := data.Add(Item{}, []indexField{{}})
	require.Error(t, err)
	err = data.Add(Item{}, nil)
	require.NoError(t, err)
	require.Len(t, data.all, 1)
}

func TestIndexData_Select(t *testing.T) {
	data := indexData{all: []Item{{textKeyValue: ptr.String("1")}, {textKeyValue: ptr.String("2")}}}
	items, err := data.Select(requestcontext.Context{}, madm.ArgsConfig{})
	require.NoError(t, err)
	require.Len(t, items, 2)
	require.Equal(t, "1", *items[0].textKeyValue)
	require.Equal(t, "2", *items[1].textKeyValue)
}

func TestIndexByFieldFactory_NewIndexByField(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}

	var testCases = []struct {
		Name          string
		Specifics     indexFieldSpecifics
		ErrorExpected bool
	}{
		{
			Name:      ContentField,
			Specifics: indexFieldSpecifics{VariantsResolver: factory.contentVariants},
		},
		{
			Name:      DomainField,
			Specifics: indexFieldSpecifics{VariantsResolver: factory.domainVariants},
		},
		{
			Name:      LangField,
			Specifics: indexFieldSpecifics{VariantsResolver: factory.langVariants},
		},
		{
			Name:      LocaleField,
			Specifics: indexFieldSpecifics{VariantsResolver: factory.localeVariants},
		},
		{
			Name: GeoField,
			Specifics: indexFieldSpecifics{
				VariantsResolver: factory.geoVariants,
				ItemsFilter:      filterGeosMinus,
			},
		},
		{
			Name:      TextKeyField,
			Specifics: indexFieldSpecifics{VariantsResolver: factory.textKeyVariants},
		},
		{
			Name:          "foo",
			ErrorExpected: true,
		},
	}

	for _, tc := range testCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			index, err := factory.NewIndexByField(tc.Name)
			if tc.ErrorExpected {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			require.Equal(t, reflect.ValueOf(tc.Specifics.VariantsResolver).Pointer(),
				reflect.ValueOf(index.specifics.VariantsResolver).Pointer())
			if tc.Specifics.ItemsFilter == nil {
				require.Nil(t, index.specifics.ItemsFilter)
			} else {
				require.Equal(t, reflect.ValueOf(tc.Specifics.ItemsFilter).Pointer(),
					reflect.ValueOf(index.specifics.ItemsFilter).Pointer())
			}
		})
	}
}

const (
	manualContent    = "content_manual"
	resolvedContent1 = "content_resolved_1"
	resolvedContent2 = "content_resolved_2"
)

type variantsResolverTestCase struct {
	Name          string
	Args          []madm.Arg
	VariantsType  interface{}
	Variants      []interface{}
	ErrorExpected bool
}

func TestIndexByFieldFactory_contentVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "content_from_args",
			Args:         []madm.Arg{madm.Content(manualContent)},
			VariantsType: "",
			Variants:     []interface{}{manualContent, madmcontent.All},
		},
		{
			Name:         "content_from_context",
			VariantsType: "",
			Variants:     []interface{}{resolvedContent1, resolvedContent2, madmcontent.All},
		},
	}
	testVariantsResolver(t, factory.contentVariants, testCases)
}

func TestIndexByFieldFactory_domainVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "domain_from_args_ru",
			Args:         []madm.Arg{madm.Domain(madmtypes.RU)},
			VariantsType: madmtypes.DomainSet(0),
			Variants:     []interface{}{madmtypes.RU, madmtypes.KUB, madmtypes.AllMinusComTr, madmtypes.KubrMinusUA, madmtypes.Kubru, madmtypes.AllDomains},
		},
		{
			Name:         "domain_from_args_com_tr",
			Args:         []madm.Arg{madm.Domain(madmtypes.ComTr)},
			VariantsType: madmtypes.DomainSet(0),
			Variants:     []interface{}{madmtypes.ComTr, madmtypes.AllDomains},
		},
		{
			Name:         "domain_from_context_ua",
			VariantsType: madmtypes.DomainSet(0),
			Variants:     []interface{}{madmtypes.UA, madmtypes.KUB, madmtypes.AllMinusComTr, madmtypes.Kubru, madmtypes.AllDomains},
		},
	}
	testVariantsResolver(t, factory.domainVariants, testCases)
}

func TestIndexByFieldFactory_langVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "lang_from_arg",
			Args:         []madm.Arg{madm.Lang("ru")},
			VariantsType: "",
			Variants:     []interface{}{"ru", LocaleAll},
		},
		{
			Name:         "lang_from_context",
			VariantsType: "",
			Variants:     []interface{}{"ua", LocaleAll},
		},
	}
	testVariantsResolver(t, factory.langVariants, testCases)
}

func TestIndexByFieldFactory_localeVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "lang_from_arg",
			Args:         []madm.Arg{madm.Locale("ru")},
			VariantsType: "",
			Variants:     []interface{}{"ru", LocaleAll},
		},
		{
			Name:         "lang_from_context",
			VariantsType: "",
			Variants:     []interface{}{"ua", LocaleAll},
		},
	}
	testVariantsResolver(t, factory.localeVariants, testCases)
}

func TestIndexByFieldFactory_textKeyVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "text_key_from_arg",
			Args:         []madm.Arg{madm.TextKey("foo")},
			VariantsType: "",
			Variants:     []interface{}{"foo"},
		},
		{
			Name:          "no_text_key_from_arg",
			ErrorExpected: true,
		},
	}
	testVariantsResolver(t, factory.textKeyVariants, testCases)
}

func TestIndexByFieldFactory_geoVariants(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	var testCases = []variantsResolverTestCase{
		{
			Name:         "geo_from_args_exact",
			Args:         []madm.Arg{madm.ExactGeo(moscow, moscowAndRegion)},
			VariantsType: uint32(0),
			Variants:     []interface{}{uint32(moscow), uint32(moscowAndRegion)},
		},
		{
			Name:         "geo_from_args_started",
			Args:         []madm.Arg{madm.StartedGeo(moscow)},
			VariantsType: uint32(0),
			Variants:     []interface{}{uint32(moscow), uint32(moscowAndRegion), uint32(russia), uint32(earth)},
		},
		{
			Name:         "geo_from_args_extra",
			Args:         []madm.Arg{madm.ExtraGeos(moscow, piter)},
			VariantsType: uint32(0),
			Variants: []interface{}{uint32(moscow), uint32(moscowAndRegion), uint32(russia), uint32(earth),
				uint32(piter)},
		},
		{
			Name:         "geo_from_context",
			VariantsType: uint32(0),
			Variants:     []interface{}{uint32(moscow), uint32(moscowAndRegion), uint32(russia), uint32(earth)},
		},
	}
	testVariantsResolver(t, factory.geoVariants, testCases)
}

func TestIndexByField_Add(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	index, err := factory.NewIndexByField(ContentField)
	require.NoError(t, err)

	err = index.Add(Item{textKeyValue: ptr.String("1")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{"1"},
		},
		{
			Name:   DomainField,
			Values: []interface{}{madmtypes.RU},
		},
	})
	require.NoError(t, err)
	require.Equal(t, 1, len(index.kv))
	require.Contains(t, index.kv, "1")
	require.IsType(t, &indexByField{}, index.kv["1"])
	require.Equal(t, DomainField, index.kv["1"].(*indexByField).fieldName)
	require.Len(t, index.kv["1"].(*indexByField).kv, 1)
	require.Contains(t, index.kv["1"].(*indexByField).kv, madmtypes.RU)
	require.IsType(t, &indexData{}, index.kv["1"].(*indexByField).kv[madmtypes.RU])
	require.Len(t, index.kv["1"].(*indexByField).kv[madmtypes.RU].(*indexData).all, 1)

	err = index.Add(Item{textKeyValue: ptr.String("2")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{"1"},
		},
		{
			Name:   DomainField,
			Values: []interface{}{madmtypes.UA},
		},
	})
	require.NoError(t, err)
	require.Equal(t, 1, len(index.kv))
	require.Len(t, index.kv["1"].(*indexByField).kv, 2)
	require.Contains(t, index.kv["1"].(*indexByField).kv, madmtypes.UA)
	require.IsType(t, &indexData{}, index.kv["1"].(*indexByField).kv[madmtypes.UA])
	require.Len(t, index.kv["1"].(*indexByField).kv[madmtypes.UA].(*indexData).all, 1)

	err = index.Add(Item{textKeyValue: ptr.String("2")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{"1"},
		},
		{
			Name:   TextKeyField,
			Values: []interface{}{"foo"},
		},
	})
	require.Error(t, err)
}

func TestIndexByField_Select(t *testing.T) {
	factory := indexByFieldFactory{geoBase: mockedGeoWrapper(t)}
	index, err := factory.NewIndexByField(ContentField)
	require.NoError(t, err)

	err = index.Add(Item{textKeyValue: ptr.String("1")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{"1"},
		},
		{
			Name:   DomainField,
			Values: []interface{}{madmtypes.RU},
		},
	})
	require.NoError(t, err)
	err = index.Add(Item{textKeyValue: ptr.String("2")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{"1"},
		},
		{
			Name:   DomainField,
			Values: []interface{}{madmtypes.UA},
		},
	})
	require.NoError(t, err)
	err = index.Add(Item{textKeyValue: ptr.String("3")}, []indexField{
		{
			Name:   ContentField,
			Values: []interface{}{madmcontent.All},
		},
		{
			Name:   DomainField,
			Values: []interface{}{madmtypes.KUB},
		},
	})
	require.NoError(t, err)

	var testCases = []struct {
		Name  string
		Items []string
		Args  []madm.Arg
	}{
		{
			Name:  "exact_content",
			Items: []string{"1", "3"},
			Args:  []madm.Arg{madm.Content("1"), madm.Domain(madmtypes.RU)},
		},
		{
			Name:  "exact_content_no_mix_field",
			Items: []string{"1"},
			Args:  []madm.Arg{madm.Content("1"), madm.Domain(madmtypes.RU), madm.NoMixField(ContentField)},
		},
		{
			Name:  "not_found_content_no_mix_field",
			Items: []string{"3"},
			Args:  []madm.Arg{madm.Content("3"), madm.Domain(madmtypes.RU), madm.NoMixField(ContentField)},
		},
		{
			Name:  "exact_content_no_mix_all",
			Items: []string{"1"},
			Args:  []madm.Arg{madm.Content("1"), madm.Domain(madmtypes.RU), madm.NoMix()},
		},
	}

	for _, tc := range testCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			var args madm.ArgsConfig
			for _, arg := range tc.Args {
				arg(&args)
			}
			items, err := index.Select(requestcontext.NewContext(nil, mockedBaseContext()), args)
			require.NoError(t, err)
			require.Len(t, items, len(tc.Items))
			for i, expected := range tc.Items {
				require.Equal(t, expected, *items[i].textKeyValue)
			}
		})
	}
}

func testVariantsResolver(t *testing.T, resolver variantsResolver, testCases []variantsResolverTestCase) {
	for _, tc := range testCases {
		tc := tc
		t.Run(tc.Name, func(t *testing.T) {
			var args madm.ArgsConfig
			for _, arg := range tc.Args {
				arg(&args)
			}
			variants, err := resolver(requestcontext.NewContext(nil, mockedBaseContext()), args)
			if tc.ErrorExpected {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			require.Len(t, variants, len(tc.Variants))
			for i, variant := range variants {
				require.IsType(t, tc.VariantsType, variant)
				require.Equal(t, tc.Variants[i], variant)
			}
		})
	}
}

const (
	moscow          = 213
	piter           = 2
	moscowAndRegion = 1
	russia          = 225
	earth           = 10000
)

func mockedBaseContext() contexts.Base {
	m := &mocks.Base{}
	m.On("GetRequest").Return(models.Request{})
	m.On("GetMordaZone").Return(models.MordaZone{
		Value: "ua",
	})
	m.On("GetMordaContent").Return(models.MordaContent{})
	m.On("GetGeo").Return(models.Geo{Parents: []uint32{
		moscow, moscowAndRegion, russia, earth,
	}})
	m.On("GetAppInfo").Return(models.AppInfo{})
	m.On("GetLocale").Return(models.Locale{Value: "ua"}, nil)
	m.On("GetMadmContent").Return(models.MadmContent{
		Values: []string{resolvedContent1, resolvedContent2, madmcontent.All},
	})
	return m
}

func mockedGeoWrapper(t *testing.T) geoBase {
	m := NewMockgeoBase(gomock.NewController(t))
	m.EXPECT().GetParentsIDsDef(gb.ID(moscow)).Return([]gb.ID{moscow, moscowAndRegion, russia, earth}, nil).AnyTimes()
	return m
}
