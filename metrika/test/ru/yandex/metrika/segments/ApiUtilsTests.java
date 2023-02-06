package ru.yandex.metrika.segments;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import com.google.common.collect.Lists;
import gnu.trove.set.hash.TLongHashSet;
import org.apache.commons.lang3.StringUtils;
import org.apache.logging.log4j.Level;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.mockito.Mockito;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.locale.LocaleDecoderGeo;
import ru.yandex.metrika.locale.LocaleDecoderSimple;
import ru.yandex.metrika.locale.LocaleGeobase;
import ru.yandex.metrika.locale.NotALocaleDecoder;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.managers.CurrencyInfoProvider;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.segments.clickhouse.parse.PrintQuery;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.doc.DocumentationSourceImpl;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.segments.core.parser.QueryParseException;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.SelectPart;
import ru.yandex.metrika.segments.core.query.SortPart;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterValues;
import ru.yandex.metrika.segments.core.query.filter.pattern.EventCondition;
import ru.yandex.metrika.segments.core.query.filter.pattern.EventPattern;
import ru.yandex.metrika.segments.core.query.filter.pattern.EventSequenceRelation;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.site.RequiredFilterBuilderSite;
import ru.yandex.metrika.segments.site.RowsUniquesProvider;
import ru.yandex.metrika.segments.site.SamplerSite;
import ru.yandex.metrika.segments.site.bundles.CommonBundleFactory;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundleString;
import ru.yandex.metrika.segments.site.decode.DecoderTypeString;
import ru.yandex.metrika.segments.site.decode.Decoders;
import ru.yandex.metrika.segments.site.decode.DecodersStub;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.Wildcard;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.collections.ZebraList;
import ru.yandex.metrika.util.geobase.GeoBase;
import ru.yandex.metrika.util.geobase.RegionType;
import ru.yandex.metrika.util.locale.LocaleDecoder;
import ru.yandex.metrika.util.locale.LocaleDecoderString;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.anyString;

/**
 * тесты нужны:
 * для каждого параметра: отсутствие , наличие
 * для каждого типа значений:
 * подходящее под формат,
 * неподходящее под формат (должна быть ошибка парсинга),
 * противоречащее здравому смыслу(ошибка парсинга или ошибка расшифровки)
 * для каждого измерения, метрики: вхождение в условие фильтрации с правильным sql
 * ? для запросов по смыслу похожих на отчеты: что sql похож на примеры, которые есть в документации
 */
public class ApiUtilsTests {
    public static ApiUtils apiUtils;

    private static Decoders decoders;
    private static Decoders decodersEn;
    private static MySqlJdbcTemplate template;
    //private MySqlJdbcTemplate visorTemplate;

    @Rule
    public ExpectedException exception = ExpectedException.none();
    private GeoBase geoBase;
    private LocaleGeobase localeGeobase;
    public static DecoderBundle decoderBundle;
    public static DecoderBundleString decoderBundleString;
    public static SimpleProvidersBundle providersBundle;

    @BeforeClass
    public static void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        decoders = new DecodersStub();
        decodersEn = new DecodersStub();
        decoderBundle = Mockito.mock(DecoderBundle.class);
        Mockito.when(decoderBundle.getDecodersForLang(Mockito.anyString()))
                .thenReturn(new DecodersStub());
        decoderBundleString = Mockito.mock(DecoderBundleString.class);
        LocaleDecoderString localeDecoderString = Mockito.mock(LocaleDecoderString.class);

        Mockito.when(decoderBundleString.getDecoder(Mockito.any(DecoderTypeString.class)))
                .thenReturn(localeDecoderString);
        GoalIdsDaoImpl goalIdsDao = Mockito.mock(GoalIdsDaoImpl.class);
        Mockito.when(goalIdsDao.getGoals(Mockito.anyInt()))
                .thenReturn(new TLongHashSet(Arrays.asList(12345L, 23456L, 34567L, 45678L)));

        Mockito.when(goalIdsDao.getGoals(Mockito.anyObject()))
                .thenReturn(new TLongHashSet(Arrays.asList(12345L, 23456L, 34567L, 45678L, 169227L)));

        apiUtils = new ApiUtils();
        CurrencyService currencyService = Mockito.mock(CurrencyService.class);
        Mockito.when(currencyService.getCurrency(anyString())).thenReturn(Optional.of(new Currency(42, "ABC", "name")));
        Mockito.when(currencyService.getCurrenciesMap()).thenReturn(Map.of());
        Mockito.when(currencyService.getCurrenciesMap3Int()).thenReturn(Map.of(CurrencyService.YND, 1));
        CurrencyInfoProvider cip = Mockito.mock(CurrencyInfoProvider.class);
        GeoPointDao geoPointDao = new GeoPointDao();
        //currencyService.afterPropertiesSet();
        AttributeParamsImpl attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService, cip);
        apiUtils.setAttributeParams(attributeParams);
        ApiUtilsConfig apiUtilsConfig = new ApiUtilsConfig();
        apiUtils.setConfig(apiUtilsConfig);
        TableSchemaSite tableSchema = new TableSchemaSite();
        apiUtils.setTableSchema(tableSchema);
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();

        apiUtils.setSampler(new SamplerSite(apiUtilsConfig.getSampleSizes(), apiUtilsConfig.getGlobalSampleSizes(), apiUtilsConfig.getTuplesSampleSizes(), new RowsUniquesProvider() {}));

        CountersRbac rbac = mockCountersRbac();
        RequiredFilterBuilderSite requiredFilterBuilder = new RequiredFilterBuilderSite();
        requiredFilterBuilder.setRankProvider(rbac);
        requiredFilterBuilder.setOwnerProvider(rbac);

        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setDecoderBundleString(decoderBundleString);
        visitProvidersBundle.setIdDecoderBundle(decoderBundle);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        visitProvidersBundle.setAttributeParams(attributeParams);
        visitProvidersBundle.setRequiredFilterBuilder(requiredFilterBuilder);
        visitProvidersBundle.afterPropertiesSet();

        apiUtils.setProvidersBundle(visitProvidersBundle);

        GAProvidersBundle gaProvidersBundle = new GAProvidersBundle();
        gaProvidersBundle.setDecoderBundle(decoderBundle);
        gaProvidersBundle.setIdDecoderBundle(decoderBundle);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.setGoalIdsDao(goalIdsDao);
        gaProvidersBundle.setAttributeParams(attributeParams);
        gaProvidersBundle.afterPropertiesSet();
        DocumentationSourceImpl documentationSource = new DocumentationSourceSite();
        apiUtils.setDocumentationSource(documentationSource);
        apiUtils.setBundleFactory(new CommonBundleFactory(tableSchema, documentationSource, visitProvidersBundle, gaProvidersBundle));
        apiUtils.afterPropertiesSet();

        //visorTemplate = GrepLog2.getTemplate("localhost", 3326, "metrica", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_new"), "WV_0");

        //Это реальный конфиг. Он сломает тесты
        /*DecoderBundle decoderBundle = new DecoderBundle();

        template = GrepLog2.getTemplate("localhost", 3308, "root", "qwerty", "conv_main");

        LocaleDictionaries dictionaries = new LocaleDictionaries();
        dictionaries.afterPropertiesSet();

        LocaleDecoder ts = getSimpleDecoder(dictionaries, "trafficSources", "trafficSource");
        LocaleDecoder adv = getSimpleDecoder(dictionaries, "AdvEngines2", "AdvEngine");
        LocaleDecoder se = getSimpleDecoder(dictionaries, "SearchEngines", "SearchEngine");

        LocaleDecoder sn = getNotALocaleDecoder("SocialNetworks", "Name");
        LocaleDecoder ua = getNotALocaleDecoder("UserAgent", "UserAgent");
        LocaleDecoder os = getNotALocaleDecoder("OSTree", "OS");

        geoBase = new GeoBase();
        localeGeobase = new LocaleGeobase();
        localeGeobase.afterPropertiesSet();

        LocaleDecoder geoCountry = getGeoDecoder(RegionType.COUNTRY);
        LocaleDecoder geoCity = getGeoDecoder(RegionType.CITY);
        LocaleDecoder geoRegion = getGeoDecoder(RegionType.REGION);

        Map<DecoderType, LocaleDecoder> decoderMap = new EnumMap<DecoderType, LocaleDecoder>(DecoderType.class);
        decoderMap.put( DecoderType.TRAFFIC_SOURCE,  ts);
        decoderMap.put( DecoderType.SEARCH_ENGINE,   se);
        decoderMap.put( DecoderType.ADV_ENGINE,      adv);
        decoderMap.put( DecoderType.SOCIAL_NETWORK,  sn);
        decoderMap.put( DecoderType.BROWSER,         ua);
        decoderMap.put( DecoderType.GEO_COUNTRY,     geoRegion);
        decoderMap.put( DecoderType.GEO_REGION,      geoCity);
        decoderMap.put( DecoderType.GEO_CITY,        geoCountry);
        decoderMap.put( DecoderType.OS,               os);

        decoderBundle.setDecoderMap(decoderMap);
        decoders = decoderBundle.getDecodersForLang("ru_RU");
        decodersEn = decoderBundle.getDecodersForLang("en_US");*/
    }

    public static CountersRbac mockCountersRbac() {
        CountersRbac countersRbac = Mockito.mock(CountersRbac.class);
        Mockito.when(countersRbac.getUnavailableIds(Mockito.anyInt()))
                .thenReturn(Lists.newArrayList());
        return countersRbac;
    }

    private LocaleDecoder getGeoDecoder(RegionType regionType) throws Exception {
        LocaleDecoderGeo geoDecoder = new LocaleDecoderGeo();
        geoDecoder.setGeoBase(geoBase);
        geoDecoder.setLocaleGeobase(localeGeobase);
        geoDecoder.setRegionType(regionType);
        geoDecoder.afterPropertiesSet();
        return geoDecoder;
    }

    private LocaleDecoder getSimpleDecoder(LocaleDictionaries dictionaries, String table, String column) throws Exception {
        LocaleDecoderSimple ld;
        ld = new LocaleDecoderSimple();
        ld.setTableName(table);
        ld.setDescriptionColumnName(column);
        ld.setTemplate(template);
        ld.setLocaleDictionaries(dictionaries);
        ld.afterPropertiesSet();
        return ld;
    }

    private NotALocaleDecoder getNotALocaleDecoder(String table, String column) throws Exception {
        NotALocaleDecoder ld = new NotALocaleDecoder();
        ld.setTableName(table);
        ld.setDescriptionColumnName(column);
        ld.setTemplate(template);
        ld.afterPropertiesSet();
        return ld;
    }

    // ga:traficSource <- ga:traficSourceID <- ga:traficSource <-
    @Test
    public void smoke() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU).domain(LocaleDomain.getDefaultChDomain()).counterId(4242).startDate("2012-01-11").endDate("2013-01-21")
                .metrics("ga:sessions,ga:users")
                .dimensions("ym:s:advEngine,ga:trafficSource")
                .filters("ga:date>20130405;ga:date<=20130408;ga:pagePath=@ololo")
                .sort("ym:s:advEngine,ga:trafficSource,ga:sessions,ga:users").build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(query);
        System.out.println(sql);
    }

    @Test
    public void testDimsFromMetadata() throws Exception {
        List<String> dims = Lists.newArrayList("ym:s:trafficSource");

        for (String dim : dims) {
            QueryParams arg = QueryParams.create()
                    .lang(LocaleLangs.RU).domain(LocaleDomain.getDefaultChDomain()).counterId(4242).startDate("2012-01-11").endDate("2013-01-21")
                    .dimensions(dim)
                    .metrics(dim2Uniq(dim))
                    .build();
            Query query = apiUtils.parseQuery(arg);
            String sql = apiUtils.toChQuery(query);
            System.out.println(query);
            System.out.println(sql);
        }

    }

    private String dim2Uniq(String input) {
        int index = input.lastIndexOf(':') + 1;
        String namespace = input.substring(0, index);
        String dim = input.substring(index);
        String uniq = "uniq" + StringUtils.capitalize(dim);
        return namespace + uniq;
    }

    @Test
    public void testLocaleDecode() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumVisits")
                .dimensions("ym:s:cookieEnabled,ym:s:advEngine")
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(query);
        System.out.println(sql);
    }

    @Test
    public void testRemarketingd() throws Exception {
        QueryParams arg = QueryParams.create()
                .counterId(30662992)
                .startDate("2016-04-26")
                .endDate("2016-04-28")
                .dimensions("ym:s:visitID,ym:s:userID,ym:s:dateTime")
                .metrics("ym:s:visits")
                .filtersBraces("(((ym:pv:URL=~'/baza/zhk_mayak' or ym:pv:URL=~'/baza/zhk_na_leninskom_prospekte' or ym:pv:URL=~'/baza/zhk_na_leninskom_prospekte' or ym:pv:URL=~'/baza/zhk_na_ul_zelenaya_himki' or ym:pv:URL=~'/baza/zhk_river_strit' or ym:pv:URL=~'/baza/zhk_rodionovo' or ym:pv:URL=~'/baza/zhk_sheremetevo_park' or ym:pv:URL=~'/baza/zhk_shodnya_park' or ym:pv:URL=~'/baza/zhk_solnechnaya_sistema' or ym:pv:URL=~'/kvartiry/novostroyka/10379-about' or ym:pv:URL=~'/kvartiry/novostroyka/11930-about' or ym:pv:URL=~'/kvartiry/novostroyka/4153-about' or ym:pv:URL=~'/kvartiry/novostroyka/4431-about' or ym:pv:URL=~'/kvartiry/novostroyka/5054-about' or ym:pv:URL=~'/kvartiry/novostroyka/jk_aventin' or ym:pv:URL=~'/kvartiry/novostroyka/jk_kvartal_7' or ym:pv:URL=~'/kvartiry/novostroyka/zhk_alfa_tsentavra' or ym:pv:URL=~'/kvartiry/novostroyka/zhk_dve_stolicy' or ym:pv:URL=~'/kvartiry/novostroyka/zhk_gornyy' or ym:pv:URL=~'/kvartiry/novostroyka/zhk_mayak')) AND (ym:s:userIDHashModulo39 == 13))")
                .ignoreLimits(true)
                .secrecy(false)
                .limit(1000000)
                .sort("ym:s:dateTime")
                .userType(UserType.MANAGER)
                .lang("ru")
                .domain("");
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(query);
        System.out.println(sql);
    }

    @Test
    public void testUidCreateAttr() throws Exception {
        QueryParams arg = getDummyParams()
                .userType(UserType.MANAGER)
                .metrics("ym:s:visits,ym:s:revenuePerVisit")
                .dimensions("ym:s:UIDCreateStartOfMonth")
                .filtersBraces("ym:s:UIDCreateDate>'2012-11-12' and ym:s:UIDCreateStartOfMonth>'2014-10-12'")
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(query);
        System.out.println(sql);
    }

    @Test
    public void testChQuery() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2012-01-01")
                .endDate("2013-01-02")
                .metrics("ga:sessions,ym:s:avgBounce")
                .sort("ga:sessions,ga:trafficSource")
                .filters("ga:operatingSystem==2")
                .dimensions("ga:trafficSource")
                .offset(10)
                .limit(102)
                .build();

        Query query = apiUtils.parseQuery(arg);
        System.out.println(apiUtils.toChQuery(query));
        System.out.println(F.map(query.getDimensions(), SelectPart::toApiName));
        System.out.println(F.map(query.getMetrics(), input -> Wildcard.unEscapeString(input.toApiName())));
        System.out.println(F.map(query.getSortParts(), SortPart::toApiName));
    }

    @Test
    public void testUnescape() {
        assertEquals("abc", Wildcard.unEscapeString("abc"));
        assertEquals("a\\b'c", Wildcard.unEscapeString("a\\\\b\\'c"));

        assertEquals("ab\nc", Wildcard.unEscapeString("ab\\nc"));
    }

    @Test
    public void testWithAdditionalQuery() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2012-01-01")
                .endDate("2013-01-02")
                .metrics("ga:sessions,ym:s:avgBounce")
                .dimensions("ym:s:socialNetworkProfile")
                .offset(10)
                .limit(102)
                .build();

        Query query = apiUtils.parseQuery(arg);
        System.out.println(apiUtils.toChQuery(query));
    }

    @Test
    public void testDimMetrSort() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2012-01-01")
                .endDate("2013-01-02")
                .metrics("ga:sessions,ym:s:avgBounce")
                .sort("ga:sessions,-ga:trafficSource")
                .filters("ym:s:avgPageViews>0")
                .dimensions("ga:trafficSource")
                .offset(10)
                .limit(102)
                .build();

        Query query = apiUtils.parseQuery(arg);
        System.out.println(apiUtils.toChQuery(query));
        assertEquals(Lists.newArrayList("ga:sessions", "ym:s:avgBounce"),
                F.map(query.getMetrics(), input -> Wildcard.unEscapeString(input.toApiName())));
        assertEquals(Lists.newArrayList("ga:trafficSource"), F.map(query.getDimensions(), SelectPart::toApiName));
        assertEquals(Lists.newArrayList("+ga:sessions", "-ga:trafficSource"), F.map(query.getSortParts(), SortPart::toApiName));
    }


    @Test
    @Ignore("METRIQA-936")
    public void testParam() throws Exception {
        /*testParam("ym:s:firstTrafficSource"                         , Arrays.asList("TraficSource.ID[1]"));
        testParam("ym:s:lastTrafficSource"                          , Arrays.asList("TraficSourceID"));
        testParam("ym:s:prevTrafficSource"                          , Arrays.asList("(length(TraficSource.ID)<=1,5,TraficSource.ID[-2])"));
        testParam("ym:s:lastSignTrafficSource"                      , Arrays.asList("LastSignificantTraficSourceID"));*/
        testParam("ym:s:datePeriodDay", Arrays.asList("toDate(StartDate)"));
        testParam("ym:s:firstTrafficSource,ym:s:lastTrafficSource", Arrays.asList("`TraficSource.ID`[1]", "TraficSourceID"));
        testParam("ym:s:goal12345IsReached", Arrays.asList("12345"));
        testParam("ym:s:goal12345IsReached,ym:s:goal23456IsReached", Arrays.asList("12345", "23456"));

    }

    public void testParam(String dimensions, List<String> where) throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .globalRequest(true)
                .startDate("2012-01-01")
                .endDate("2013-01-02")
                .metrics("ym:s:avgBounce")
                .dimensions(dimensions)
                .offset(10)
                .limit(102)
                .build();
        Query query = apiUtils.parseQuery(arg);
        String ch = apiUtils.toChQuery(query);
        System.out.println(ch);
        for (String w : where) {
            assertTrue(ch.contains(w));
        }
    }

    // ::::::::::: Transform tests ::::::::::::

    @Test
    public void testHitMetricTransform() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .dimensions("ga:trafficSource")
                .metrics("ga:sessions")
                .filters("ga:pagePath=@/cart")
                .offset(0)
                .limit(100)
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql, sql.contains("arrayExists(x_0 -> x_0 IN (WITH 1.0 AS W SELECT WatchID AS `ym:pv:eventID`"));
        assertTrue(sql, sql.contains("),`Event.ID`)"));
    }

    @Test
    public void testVisitMetricTransform() throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .dimensions("ga:pagePath")
                .metrics("ga:avgPageLoadTime")
                .filters("ga:trafficSource==Прямые заходы") //=@ -> ==, потому что строковые операции для декодируемых операций отменены
                .offset(1)
                .limit(100)
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("WatchID IN (WITH 1.0 AS W SELECT `Ewv.ID` AS `ym:s:eventID` FROM default.visits_layer as `default.visits_layer` ARRAY JOIN `Event.ID` AS `Ewv.ID`"));
    }

    @Test
    public void testIpFilter() {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .dimensions("ga:pagePath")
                .metrics("ga:avgPageLoadTime")
                .userType(UserType.MANAGER)
                .filtersBraces("((ym:s:specialDefaultDate<='2014-09-07') AND " +
                        "(ym:s:ipAddress!~'^100\\\\.43\\\\.(6[4-9]|[78]\\\\d|9[5-9])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^130\\\\.193\\\\.(3[2-9]|[45]\\\\d|6[0-3])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^141\\\\.8\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^178\\\\.154\\\\.(12[89]|1[3-9]\\\\d|2\\\\d\\\\d)\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^185\\\\.32\\\\.18[4-7]\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^199\\\\.21\\\\.9[6-9]\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^199\\\\.36\\\\.24[0-3]\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^213\\\\.180\\\\.(19[2-9]|2[01]\\\\d|22[0-3])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^37\\\\.140\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^37\\\\.9\\\\.(6[4-9]|[7-9]\\\\d|1[01]\\\\d|12[0-7])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^5\\\\.255\\\\.(19[2-9]|2\\\\d\\\\d)\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^5\\\\.45\\\\.(19[2-9]|2\\\\d\\\\d)\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^77\\\\.88\\\\.(\\\\d|[1-5]\\\\d|6[0-3])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^84\\\\.201\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^87\\\\.250\\\\.(22[4-9]|2[3-5]\\\\d)\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^93\\\\.158\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and " +
                        "ym:s:ipAddress!~'^95\\\\.108\\\\.(12[89]|1[3-9]\\\\d|2\\\\d\\\\d)\\\\.xxx$'))")
                .offset(1)
                .limit(100)
                .build();
        String f = "(" +
                "((ym:s:specialDefaultDate<='2014-09-07') AND (ym:s:ipAddress!~'^100\\\\.43\\\\.(6[4-9]|[78]\\\\d|9[5-9])\\\\.xxx$' and ym:s:ipAddress!~'^130\\\\.193\\\\.(3[2-9]|[45]\\\\d|6[0-3])\\\\.xxx$' and ym:s:ipAddress!~'^141\\\\.8\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and ym:s:ipAddress!~'^178\\\\.154\\\\.(12[89]|1[3-9]\\\\d|2\\\\d\\\\d)\\\\.xxx$' and ym:s:ipAddress!~'^185\\\\.32\\\\.18[4-7]\\\\.xxx$' and ym:s:ipAddress!~'^199\\\\.21\\\\.9[6-9]\\\\.xxx$' and ym:s:ipAddress!~'^199\\\\.36\\\\.24[0-3]\\\\.xxx$' and ym:s:ipAddress!~'^213\\\\.180\\\\.(19[2-9]|2[01]\\\\d|22[0-3])\\\\.xxx$' and ym:s:ipAddress!~'^37\\\\.140\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and ym:s:ipAddress!~'^37\\\\.9\\\\.(6[4-9]|[7-9]\\\\d|1[01]\\\\d|12[0-7])\\\\.xxx$' and ym:s:ipAddress!~'^5\\\\.255\\\\.(19[2-9]|2\\\\d\\\\d)\\\\.xxx$' and ym:s:ipAddress!~'^5\\\\.45\\\\.(19[2-9]|2\\\\d\\\\d)\\\\.xxx$' and ym:s:ipAddress!~'^77\\\\.88\\\\.(\\\\d|[1-5]\\\\d|6[0-3])\\\\.xxx$' and ym:s:ipAddress!~'^84\\\\.201\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and ym:s:ipAddress!~'^87\\\\.250\\\\.(22[4-9]|2[3-5]\\\\d)\\\\.xxx$' and ym:s:ipAddress!~'^93\\\\.158\\\\.(12[8-9]|1[3-8]\\\\d|19[01])\\\\.xxx$' and ym:s:ipAddress!~'^95\\\\.108\\\\.(12[89]|1[3-9]\\\\d|2\\\\d\\\\d)\\\\.xxx$'))" +
                ")";
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
    }


    @Test
    public void testStringHits() throws Exception {
        //только для кликхауса
        testStringChHits("ga:pagePath", "path(URL)");
        testStringChHits("ga:pagePathLevel1", "extract(URL,'(?:[^/]+)//(?:[^/]+)/([^/]+).*')");
        testStringChHits("ga:pagePathLevel2", "extract(URL,'(?:[^/]+)//(?:[^/]+)/(?:[^/]+)/([^/]+).*')");
        testStringChHits("ga:pagePathLevel3", "extract(URL,'(?:[^/]+)//(?:[^/]+)/(?:[^/]+)/(?:[^/]+)/([^/]+).*')");
        testStringChHits("ga:pagePathLevel4", "extract(URL,'(?:[^/]+)//(?:[^/]+)/(?:[^/]+)/(?:[^/]+)/(?:[^/]+)/([^/]+).*')");
        testStringChHits("ga:pageTitle", "Title");
        testStringChHits("ga:previousPagePath", "path(Referer)");
    }

    public void testStringChHits(String paramName, String attribute) throws Exception {
        // ==, !=, >, <, >=, <=, =@, !@, =~, !~
        testWhereChHits(paramName + "==/sasha_grey", attribute + ' ' + '=' + " '/sasha_grey'");
        testWhereChHits(paramName + "!=/sasha_grey", attribute + ' ' + "!=" + " '/sasha_grey'");
        testWhereChHits(paramName + ">/sasha_grey", attribute + ' ' + '>' + " '/sasha_grey'");
        testWhereChHits(paramName + "</sasha_grey", attribute + ' ' + '<' + " '/sasha_grey'");
        testWhereChHits(paramName + ">=/sasha_grey", attribute + ' ' + ">=" + " '/sasha_grey'");
        testWhereChHits(paramName + "<=/sasha_grey", attribute + ' ' + "<=" + " '/sasha_grey'");
        testWhereChHits(paramName + "=@/sasha_grey", "positionCaseInsensitive(" + attribute + ",'/sasha_grey') > toInt32(0)");
        testWhereChHits(paramName + "!@/sasha_grey", "positionCaseInsensitive(" + attribute + ",'/sasha_grey') = toInt32(0)");
        testWhereChHits(paramName + "=@/саша_грей", "positionCaseInsensitiveUTF8(" + attribute + ",'/саша_грей') > toInt32(0)");
        testWhereChHits(paramName + "!@/саша_грей", "positionCaseInsensitiveUTF8(" + attribute + ",'/саша_грей') = toInt32(0)");
        testWhereChHits(paramName + "=~/sasha_grey.*", "match(" + attribute + ",'/sasha_grey.*')");
        testWhereChHits(paramName + "!~/sasha_grey.*", "NOT match(" + attribute + ",'/sasha_grey.*')");
    }


    private String getPathSql(String columnName) {
        return "SUBSTRING(" + columnName + " FROM LOCATE('/', " + columnName + ", LOCATE('//', " + columnName + ") + 2))";
    }

    private String getConcatSql(String column1, String column2, String concatSymbol) {
        return "CONCAT(" + column1 + ", '" + concatSymbol + "', " + column2 + ')';
    }

    // ::::::::::: Decode tests :::::::::::::

    //  эти тесты завязаны на текущую базу, см. setUp()

    /*//locale
    @Test
    public void testDecodeTs() throws Exception {
        testDecode("trafficSource==Переходы из поисковых систем", "((trafficSource in (2)))");
        testDecode("trafficSource==Search engine traffic", "((trafficSource in (2)))", decodersEn);
        testDecode("trafficSource=@из поисковых систем", "((trafficSource in (2)))");
    }

    //not-a-locale
    @Test
    public void testDecodeOs() throws Exception {
        testDecode("operatingSystem==Ubuntu 9.04 Jaunty Jackalope", "((OS in (39)))");
        testDecode("operatingSystem==Ubuntu 9.04 Jaunty Jackalope", "((OS in (39)))", decodersEn);
    }

    //geo
    @Test
    public void testDecodeGeo() throws Exception {
        //Москва одна, а Moscow две
        testDecode("city==Москва", "((city in (213)))");
        testDecode("city==Moscow", "((city in (213 , 103325)))", decodersEn);
        testDecode("country==Russia", "((country in (225)))", decodersEn);
    }

    @Test
    public void testDecodeGeoError() throws Exception {
        exception.expect(DecodeException.class);
        testDecode("country==Москва", "((city in (213)))");
    }*/

    private void testWhereChHits(String filter, String whereString) throws Exception {
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU).domain(LocaleDomain.getDefaultChDomain()).counterId(4242).startDate("2012-01-20").endDate("2013-01-01")
                .metrics("ga:avgPageLoadTime")
                .filters(filter).build();
        String chSql = apiUtils.toChQuery(apiUtils.parseQuery(arg));
        System.out.println(chSql);
        System.out.println(whereString);
        assertTrue(chSql.contains(whereString));
    }

    @Test
    public void testNullability() throws Exception {
        String dimName = "ym:s:trafficSource";
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU).domain(LocaleDomain.getDefaultChDomain()).counterId(4242).startDate("2012-01-20").endDate("2013-01-01")
                .metrics("ym:s:visits")
                .filtersBraces(dimName + "==null").build();
        String chSql = apiUtils.toChWhere(apiUtils.parseQuery(arg));
        System.out.println(chSql);
        assertTrue(chSql.contains("`TrafficSource.ID`[indexOf(`TrafficSource.Model`,1)] = toInt8(5)"));

        QueryParams arg2 = QueryParams.create()
                .lang(LocaleLangs.RU).domain(LocaleDomain.getDefaultChDomain()).counterId(4242).startDate("2012-01-20").endDate("2013-01-01")
                .metrics("ym:s:visits")
                .filtersBraces(dimName + "!=null").build();
        String chSql2 = apiUtils.toChWhere(apiUtils.parseQuery(arg2));
        System.out.println(chSql2);
        assertTrue(chSql2.contains("`TrafficSource.ID`[indexOf(`TrafficSource.Model`,1)] != toInt8(5)"));

    }

    @Test
    public void testInterests() throws Exception {
        QueryParams arg = getDummyParams().dimensions("ym:s:interest").build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("ARRAY JOIN bitmaskToArray(Interests) AS interests_alias,"));
    }

    @Test
    public void testURLPathLevel1Hash() throws Exception {
        QueryParams arg = QueryParams.create()
                .counterId(100)
                .directClientIds(new int[]{0})
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .metrics("ym:c:visits")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain()).dimensions("ym:c:URLPathLevel1Hash").build();
        arg.setOtherParams(Collections.singletonMap("attribution", "Last"));
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("Referer"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testClickStorage() throws Exception {
        QueryParams arg = getDummyParams()
                .directClientIds(new int[]{0})
                .dimensions("ym:cs:directBanner")
                .metrics("ym:cs:unitAdCost,ym:cs:YNDAdCost")
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("toString(dictGetUInt32OrDefault('banners','bid',toUInt64(ContextType = 7?ParentBannerID:BannerID),ContextType = 7?ParentBannerID:BannerID))"));
        assertTrue(sql.contains("sum(EventCost / 1000000.0 * Sign) AS `ym:cs:unitAdCost`"));
        assertTrue(sql.contains("sum((CurrencyID = 42?toUInt64(EventCost) / 1000000.0:0.0) * Sign) AS `ym:cs:YNDAdCost`"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testInterests2() throws Exception {
        QueryParams arg = getDummyParams()
                .dimensions("ym:s:interest")
                .filtersBraces("ym:s:interest IN (1,2) AND ym:s:interest==3 AND ym:s:interest!=(4,5,6)")
                .build();
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("x_0 IN (49,50)"));
        assertTrue(sql.contains("x_0 = 51"));
        assertTrue(sql.contains("x_0 != 52 and x_0 != 53 and x_0 != 54,"));
    }

    //=============== webvisor ==============

    @Test
    public void testNoGroup() throws Exception {
        final QueryParams params = QueryParams.create()
                .counterId(100)
                .startDate("2014-07-24")
                .endDate("2014-07-24")
                .enableSampling(false)
                .dimensions("ym:s:webVisorActivity,ym:s:visitID")
                .filters("ym:s:regionCountry==223")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain()).noGroup(true);

        final String sql = apiUtils.toChQuery(apiUtils.parseQuery(params));

        System.out.println(sql);

    }


    //================ array join ============

    // https://wiki.yandex-team.ru/jandexmetrika/doc/api/apikonstruktora/manual/

    /*
     || **Тупл в dim** | **Тупл в metric** | **Тупл в фильтре** | **Есть ARRAY JOIN** | **Всякое** ||
     || - | - | - | - | ||
+1 -> || - | + | - | - | Метрики считаются через агрегатные функции для туплов (sumArray и т.д.) ||
+2 -> || - | - | + | - | Положительные фильтры реализуются через arrayExists(...), отрицательные - через NOT arrayExists(...) (SelectPartFilter -> фигачим через лямбды) ||
+3 -> || - | + | + | - | Заменяем тупл на arrayFilter версию. По такой версии считаем метрики по туплу. ||
+4 -> || + | - | - | + | Метрики считаются с фильтром arrayEnumerateUniq==1 ||
+5 -> || + | + | - | + | Метрики по этому туплу считаются через алиас, прочие - через arrayEnumerateUniq==1 ||
+6 -> || + | - | + | + | Выражение для тупла заменяется на arrayFilter версию, чтобы остались только строки, прошедшие условие. Это же касается тупла внутри arrayEnumerateUniq. Фильтры по туплу считаются по алиасу.  ||
7 -> || + | + | + | + | Сочетание предыдущих двух строчек ||
     */

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder1() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:sumParamsInternal")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,`ParsedParams.ValueDouble`))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder1f() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:mobilePhoneModel=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t -> MobilePhoneModel = 'ololo'," +
                        "`ParsedParams.ValueDouble`)))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder1Url() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:startURL=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t -> StartURL = 'ololo' OR StartURL = 'ololo/'," +
                        "`ParsedParams.ValueDouble`)))"
        ));
    }

    @Test
    public void testArrayJoinBuilder1_1() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:uniqGoalDimension")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "uniqArray(`Goals.ID`)"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder2_1() throws Exception {

        QueryParams queryParams = getDummyParams()
                .filtersBraces("ym:s:paramsFilter=='ololo'")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "arrayExists(x_0 -> x_0 = 'ololo',`ParsedParams.Key1`)"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder2_2() throws Exception {

        QueryParams queryParams = getDummyParams()
                .filtersBraces("ym:s:paramsLevel1=='ololo'")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "arrayExists(x_0 -> x_0 = 'ololo' AND x_0 != '__ym',`ParsedParams.Key1`)"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder3_1() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:paramsFilter=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'ololo'," +
                        "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilder3_2() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:paramsLevel1=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'ololo'," +
                        "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilderTwoTuples_1() throws Exception {

        QueryParams queryParams = getDummyParams()
                .dimensions("ym:s:goalDimension")
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:paramsFilter=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'ololo' AND _uniq_Goals IN (0,1)," +
                        "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testArrayJoinBuilderTwoTuples_2() throws Exception {

        QueryParams queryParams = getDummyParams()
                .dimensions("ym:s:goalDimension")
                .metrics("ym:s:visits,ym:s:sumParamsInternal(ym:s:paramsLevel1=='ololo')")
                .build();

        assertTrue(sqlContainsAll(queryParams,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'ololo' AND _uniq_Goals IN (0,1)," +
                        "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testSupportMiltivalueFilter() throws Exception {
        Set<Relation> relations = F.filter(Relation.values(), r -> r.getFuncM().isPresent() && !r.isInternal());

        QueryParams queryParams = getDummyParams()
                .metrics("ym:pv:pageviews")
                .filtersBraces(relations.stream().map(r -> "ym:pv:title " + r.getMainRepresentation() + " ('1','two',null)").collect(Collectors.joining(" AND ")))
                .build();
        assertTrue(sqlContainsAll(queryParams,
                //"(NOT Title IN ('1','two',''))",
                "Title IN ('1','two')",
                "Title GLOBAL IN ('1','two')"
        ));
    }

    @Test
    public void goalFilteringMFTest() {
        for (AbstractAttribute attribute : apiUtils.getUnionBundle().getAttributes()) {
            if (attribute.getAttrName().equals("GoalDimension")) {
                SelectPartFilter s = SelectPartFilter.singleValue(attribute, Relation.EQ, "42");
                QueryContext qc = QueryContext.defaultFields()
                        .targetTable(TableSchemaSite.VISITS)
                        .lang("ru")
                        .domain("ru")
                        .apiUtils(apiUtils)
                        .useDimensionNotNullFilters(false)
                        .excludeInsignificant(false)
                        //.tableMetadatas(apiUtils.getClickhouseTableMetas())
                        .build();
                String sql = s.buildExpression(qc).asSql();
                int z = 42;
            }
        }
    }

    @Test(expected = QueryParseException.class)
    public void testNotSupportMiltivalueFilter() throws Exception {
        Set<Relation> relations = F.filter(Relation.values(), r -> !r.getFuncM().isPresent());

        QueryParams queryParams = getDummyParams()
                .metrics("ym:pv:pageviews")
                .filtersBraces(relations.stream().map(r -> "ym:pv:title " + r.getMainRepresentation() + " (1,'two',null)").collect(Collectors.joining(" AND ")))
                .build();
        boolean condition = sqlContainsAll(queryParams);
        assertTrue(condition);
    }


    /*@Test
    public void testArrayJoinBuilderzz() throws Exception {

        QueryParams queryParams = getDummyParams()
                .metrics("ym:s:argMaxParamsQuantity")
                .dimensions("ym:s:age")
                .build();

        assertTrue(sqlContainsNone(queryParams,
                "`_uniq_ParsedParams` = 1",
                "uniqIf(PP.Key1, PP.Key1 != '')",
                "FROM visits_layer ARRAY JOIN ParsedParams AS PP",
                "arrayEnumerate(`ParsedParams.Key1`) AS `_uniq_ParsedParams`"));
        assertTrue(sqlContainsAll(queryParams, "(arrayExists(x -> x IN (1211426), bitmaskToArray(Interests))"));
    }*/

/*
    @Test
    public void testArrayJoinBuilder2() throws Exception {

        QueryParams queryParams = getDummyParams()
            .filters("ym:s:interest=='20'")
            .build();

        assertTrue(sqlContainsNone(queryParams,
            "`_uniq_ParsedParams` = 1",
            "uniqIf(PP.Key1, PP.Key1 != '')",
            "FROM visits_layer ARRAY JOIN ParsedParams AS PP",
            "arrayEnumerate(`ParsedParams.Key1`) AS `_uniq_ParsedParams`"));
        assertTrue(sqlContainsAll(queryParams, "(arrayExists(x -> x IN (1211426), bitmaskToArray(Interests))"));
    }

    @Test
    public void testArrayJoinBuilder3() throws Exception {

        QueryParams queryParams = getDummyParams()
            .metrics("ym:s:uniqParamsLevel1")
            .filters("ym:s:interest=='20'")
            .build();

        assertTrue(sqlContainsAll(queryParams, "(arrayExists(x -> x IN (1211426), bitmaskToArray(Interests))","ARRAY JOIN ParsedParams AS PP", "arrayEnumerate(`ParsedParams.Key1`) AS `_uniq_ParsedParams`"));

    }

    @Test
    public void testArrayJoinBuilder4() throws Exception {

        QueryParams queryParams = getDummyParams()
            .dimensions("ym:s:paramsLevel2")
            .build();

        assertTrue(sqlContainsAll(queryParams, "ARRAY JOIN ParsedParams AS PP", "arrayEnumerateUniq(ParsedParams.Key2)", ""));
    }

    @Test
    public void testArrayJoinBuilder5() throws Exception {

        QueryParams queryParams = getDummyParams()
            .metrics("ym:s:uniqParamsLevel1")
            .dimensions("ym:s:paramsLevel2")
            .filters("ym:s:visits==20")
            .build();

        assertTrue(sqlContainsAll(queryParams, "ARRAY JOIN ParsedParams AS PP", "arrayEnumerateUniq(ParsedParams.Key2)", "HAVING (sum(Sign) = 20)"));
    }

    @Test(expected = QueryParseException.class)
    public void testArrayJoinBuilder5Infernal() throws Exception {

        QueryParams queryParams = getDummyParams()
            .metrics("ym:s:uniqParamsLevel1")
            .dimensions("Interests")
            .build();

        compareSql("", queryParams);
    }

    @Test
    public void testArrayJoinBuilder6() throws Exception {

        QueryParams queryParams = getDummyParams()
            .filters("ym:s:interest=='20'")
            .dimensions("ym:s:paramsLevel1")
            .build();

        assertTrue(sqlContainsAll(queryParams, "ARRAY JOIN ParsedParams AS PP", "arrayEnumerateUniq(ParsedParams.Key1)", "arrayExists(x -> x IN (1211426), bitmaskToArray(Interests)"));
    }

    @Test
    public void testArrayJoinBuilder7() throws Exception {

        QueryParams queryParams = getDummyParams()
            .metrics("ym:s:uniqParamsLevel2")
            .filters("ym:s:interest=='20'")
            .dimensions("ym:s:paramsLevel1")
            .build();

        assertTrue(sqlContainsAll(queryParams, "uniqIf(PP.Key2, PP.Key2 != '')", "ARRAY JOIN ParsedParams AS PP", "arrayEnumerateUniq(ParsedParams.Key1", "arrayExists(x -> x IN (1211426), bitmaskToArray(Interests))"));
    }*/

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesAJ_1() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("exists(ym:s:paramsFilter=='ololo')").build();
        assertTrue(sqlContainsAll(arg, "arrayExists(x_0 -> x_0 = 'ololo',`ParsedParams.Key1`)"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesAJ_2() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("exists(ym:s:paramsLevel1=='ololo')").build();
        assertTrue(sqlContainsAll(arg, "arrayExists(x_0 -> x_0 = 'ololo' AND x_0 != '__ym',`ParsedParams.Key1`)"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesKJ() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("none(ym:pv:title=='ololo')").build();
        assertTrue(sqlContainsAll(arg,
                "AND NOT arrayExists(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "AND Title = 'ololo'"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesKJ2() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("all(ym:pv:title=='ololo')").build();
        assertTrue(sqlContainsAll(arg,
                "AND arrayAll(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "AND Title = 'ololo')"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMETRIKASUPP6605() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("ym:pv:title=='ololo' or ym:pv:title=='alala'").build();
        /*
select sum(Sign) AS `ym:s:visits` from default.visits_layer where
StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 AND
arrayExists(x -> x IN (select WatchID AS `ym:pv:eventID` from merge.hits where EventDate >= toDate('2012-01-01') and EventDate <= toDate('2012-01-02') and CounterID = 100 and
                            NOT DontCountHits AND NOT Refresh AND (Title = 'ololo' OR Title = 'alala')),`Event.ID`) with totals  having `ym:s:visits` > 0.0 order by `ym:s:visits` desc limit 0
        * */
        assertTrue(sqlContainsAll(arg,
                "AND arrayExists(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "Title = 'ololo' OR Title = 'alala')"
        ));

        QueryParams arg2 = getDummyParams().filtersBraces("(ym:pv:URL=*'*ru/person*' or ym:pv:URL=*'*s_m_*') and ym:s:datePeriodday!n and ym:s:datePeriodday!n").build();
/*
select sum(Sign) AS `ym:s:visits` from default.visits_layer where
StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 AND
(arrayExists(x -> x IN (select WatchID AS `ym:pv:eventID` from merge.hits where EventDate >= toDate('2012-01-01') and EventDate <= toDate('2012-01-02') and CounterID = 100 and NOT DontCountHits AND NOT Refresh AND URL LIKE '%ru/person%'),`Event.ID`)
OR
arrayExists(x -> x IN (select WatchID AS `ym:pv:eventID` from merge.hits where EventDate >= toDate('2012-01-01') and EventDate <= toDate('2012-01-02') and CounterID = 100 and NOT DontCountHits AND NOT Refresh AND URL LIKE '%s\\_m\\_%'),`Event.ID`)
) with totals  having `ym:s:visits` > 0.0 order by `ym:s:visits` desc limit 0


select sum(Sign) AS `ym:s:visits` from default.visits_layer where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100
AND arrayExists(x -> x IN (select WatchID AS `ym:pv:eventID` from merge.hits where EventDate >= toDate('2012-01-01') and EventDate <= toDate('2012-01-02') and CounterID = 100 and NOT DontCountHits AND NOT Refresh AND (URL LIKE '%ru/person%' OR URL LIKE '%s\\_m\\_%')),`Event.ID`)
with totals  having `ym:s:visits` > 0.0 order by `ym:s:visits` desc limit 0
**/
        assertTrue(sqlContainsAll(arg2,
                "AND arrayExists(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "(URL LIKE '%ru/person%' OR URL LIKE '%s\\\\_m\\\\_%')"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesKJ3() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("all(ym:pv:title!='ololo')").build();
        assertTrue(sqlContainsAll(arg,
                "AND arrayAll(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "AND Title != 'ololo')"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesKJ4() throws Exception {
        QueryParams arg = getDummyParams().filtersBraces("all(ym:pv:URL!='ololo')").build();
        assertTrue(sqlContainsAll(arg,
                "AND arrayAll(x_0 -> x_0 IN (select WatchID AS `ym:pv:eventID`",
                "AND URL != 'ololo')"
        ));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesAJAJ_1() throws Exception {
        QueryParams arg = getDummyParams()
                .dimensions("ym:s:paramsFilter")
                .filtersBraces("all(ym:s:paramsFilter=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "arrayAll(x_0 -> x_0 = 'ololo',`ParsedParams.Key1`)"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesAJAJ_2() throws Exception {
        QueryParams arg = getDummyParams()
                .dimensions("ym:s:paramsLevel1")
                .filtersBraces("all(ym:s:paramsLevel1=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "arrayAll(x_0 -> x_0 = 'ololo' AND x_0 != '__ym',`ParsedParams.Key1`) " +
                "and `PP.Key1` != '__ym' AND `PP.Key1` != ''"));
    }

    @Test
    public void testEntitiesManyToOne() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:pv:pageviews")
                .filtersBraces("ym:s:lastTrafficSource=='organic'")
                .build();
        assertTrue(sqlContainsAll(arg, "WatchID IN (WITH 1.0 AS W SELECT `Ewv.ID` AS `ym:s:eventID` FROM default.visits_layer as `default.visits_layer` ARRAY JOIN `Event.ID` AS `Ewv.ID`"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal")
                .filtersBraces("all(ym:s:paramsLevel1=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,`ParsedParams.ValueDouble`))"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric2_1() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal(ym:s:paramsFilter=='alala')")
                .filtersBraces("exists(ym:s:paramsFilter=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'alala'," +
                "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric2_2() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal(ym:s:paramsLevel1=='alala')")
                .filtersBraces("exists(ym:s:paramsLevel1=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0 -> x_0 = 'alala'," +
                "`ParsedParams.ValueDouble`,`ParsedParams.Key1`)))"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric3_1() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal(ym:s:paramsFilter=='alala')")
                .dimensions("ym:s:advEngine")
                .filtersBraces("exists(ym:s:paramsFilter=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "arrayExists(x_0 -> x_0 = 'ololo',`ParsedParams.Key1`)"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric3_2() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal(ym:s:paramsLevel1=='alala' and ym:s:paramsLevel2=='kkk')")
                .dimensions("ym:s:advEngine")
                .filtersBraces("exists(ym:s:paramsLevel1=='ololo')")
                .build();
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t,x_0,x_1 -> x_0 = 'alala' AND x_1 = 'kkk'," +
                "`ParsedParams.ValueDouble`,`ParsedParams.Key1`,`ParsedParams.Key2`)))"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric4_1() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal")
                .filtersBraces("exists(ym:s:paramsFilter=='alala')")
                .build();
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,`ParsedParams.ValueDouble`))"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric4_2() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal")
                .filtersBraces("exists(ym:s:paramsLevel1=='alala' and ym:s:paramsLevel2=='kkk')")
                .build();
        assertTrue(sqlContainsAll(arg,
                "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,`ParsedParams.ValueDouble`))",
                "x_0 = 'alala' AND x_0 != '__ym' AND x_1 = 'kkk' AND x_0 != '__ym'"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testEntitiesMetric5() throws Exception {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:sumParamsInternal")
                .dimensions("ym:s:gender")
                .build();
        // если
        // группировка по атрибуту без тупла,
        // в parent_id атрибуты с туплом
        // метрика по туплу,
        // то
        // надо фильтровать эти метрики по тупл-условию из parent_id filter. сейчас это не происходит и это баг.
        arg.setParentIdFilter("exists(ym:s:paramsLevel1=='alala' and ym:s:paramsLevel2=='kkk') and ym:s:trafficSourceID==3");
        assertTrue(sqlContainsAll(arg, "sumArray(arrayMap(x -> (isFinite(x)?x:0) * Sign,arrayFilter(t -> arrayExists(x_0,x_1 -> x_0 = 'alala' AND x_0 != '__ym' AND x_1 = 'kkk' AND x_0 != '__ym'," +
                "`ParsedParams.Key1`,`ParsedParams.Key2`),`ParsedParams.ValueDouble`)))"));
    }

    @Test
    public void testExistsAnd() throws Exception {

        QueryParams queryParams = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .metrics("ym:s:users")
                .filtersBraces("exists(ym:s:paramsLevel1=='_1_' and ym:s:paramsLevel2=='_a_') and exists(ym:s:paramsLevel1=='_2_' and ym:s:paramsLevel2=='_b_')  ")
                .offset(0)
                .limit(100)
                .build();
        Query query = apiUtils.parseQuery(queryParams);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);

    }


    @Test
    public void testExtendedQuantors() throws Exception {

        QueryParams queryParams = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .metrics("ym:el:users")
                .filtersBraces("ym:s:advEngine!=null")
                .offset(0)
                .limit(100)
                .build();
        Query query = apiUtils.parseQuery(queryParams);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);

    }


    private List<String> prepareEscapedFiltersWithWildcards(String[] w, Relation r) {
        QueryParams arg = getDummyParams().metrics("ym:pv:pageviews").filtersBraces(
                '(' + String.join(" OR ", F.map(w, c -> "ym:pv:title" + r.getMainRepresentation() + " '" + c + '\'')) + ')').build();
        Query query = apiUtils.parseQuery(arg);
        return F.map(((Compound) query.getDimensionFilters().get()).getChildren(),
                f -> PrintQuery.print(f.buildExpression(query.getQueryContext())));
    }

    private void checkEscapedFiltersWithWildcards(String[] w, String[] e, Relation[] ops, WildcardEscape wildcardEscape) {
        for (Relation op : ops) {
            List<String> filters = prepareEscapedFiltersWithWildcards(w, op);
            for (int i = 0; i < e.length; i++) {
                assertEquals("Invalid filter for relation " + op + " and wildcard " + w[i],
                        wildcardEscape.escape(e[i], op), filters.get(i));
            }
        }
    }

    @Test
    public void testDBWildcardEscapingEqOp() throws Exception {
        Relation[] ops = {Relation.EQ, Relation.NE};
        String[] wildcards = {"\\'", "*", "_", "%", "\\\\"};
        checkEscapedFiltersWithWildcards(wildcards, wildcards, ops,
                (w, op) -> "Title " + (op.isPositive() ? "=" : "!=") + " '" + w + '\'');
    }

    @Test
    public void testDBWildcardEscapingSubOp() throws Exception {
        Relation[] ops = {Relation.SUB, Relation.NSUB};
        String[] wildcards = {"\\'", "*", "_", "%", "\\\\"};
        checkEscapedFiltersWithWildcards(wildcards, wildcards, ops,
                (w, op) -> "positionCaseInsensitive(Title,'" + w + "') " + (op.isPositive() ? ">" : "=") + " toInt32(0)");
    }

    @Test
    public void testDBWildcardEscapingLikeOp() throws Exception {
        Relation[] ops = {Relation.LIKE, Relation.NLIKE};
        String[] wildcards = {"\\'", "*", "_", "%", "\\\\"};
        String[] expected = {"\\'", "%", "\\\\_", "\\\\%", "\\\\\\\\"};
        checkEscapedFiltersWithWildcards(wildcards, expected, ops,
                (w, op) -> "Title " + (op.isPositive() ? "" : "NOT ") + "LIKE '" + w + "'");
    }

    @Test
    public void testDBWildcardEscapingRegexOp() throws Exception {
        Relation[] ops = {Relation.RE, Relation.NRE};
        String[] wildcards = {"\\'", "\\\\*", "_", "%", "\\\\\\\\"};
        checkEscapedFiltersWithWildcards(wildcards, wildcards, ops,
                (w, op) -> (op.isPositive() ? "" : "NOT ") + "match(Title,'" + w + "')");
    }

    /*
     * тест падает, т.к. алиасинг выжражений отработал позже if-оптимизации
     */
    @Test
    @Ignore("METRIQA-936")
    public void testLastSignificantTrafficSource() throws Exception {
        QueryParams arg1 = getDummyParams().dimensions("ym:s:lastSignTrafficSource").build();
        assertTrue(sqlContainsAll(arg1,
                "StartDate > toDate('2014-11-27')?LastSignificantTraficSourceID:5 AS `ym:s:lastSignTrafficSource`",
                "LastSignificantTraficSourceID != 5"));
    }

    @Test
    public void testTimeZone() throws Exception {
        checkTimeZone("-23:59", "2011-12-30 21:01:00", "2012-01-01 21:00:59", "-97140");
        checkTimeZone("-21:00", "2011-12-31 00:00:00", "2012-01-01 23:59:59", "-86400");
        checkTimeZone("-05:00", "2011-12-31 16:00:00", "2012-01-02 15:59:59", "toInt32(-28800)");
        checkTimeZone("-03:00", "2011-12-31 18:00:00", "2012-01-02 17:59:59", "toInt32(-21600)");
        checkTimeZone("-01:00", "2011-12-31 20:00:00", "2012-01-02 19:59:59", "toInt32(-14400)");
        checkTimeZone("-00:00", "2011-12-31 21:00:00", "2012-01-02 20:59:59", "toInt32(-10800)");
        checkTimeZone("+00:00", "2011-12-31 21:00:00", "2012-01-02 20:59:59", "toInt32(-10800)");
        checkTimeZone("+01:00", "2011-12-31 22:00:00", "2012-01-02 21:59:59", "toInt32(-7200)");
        checkTimeZone("+01:30", "2011-12-31 22:30:00", "2012-01-02 22:29:59", "toInt32(-5400)");
        checkTimeZone("+02:59", "2011-12-31 23:59:00", "2012-01-02 23:58:59", "toInt32(-60)");
        checkTimeZone("Europe/Moscow", "2012-01-01", "2012-01-02", "");
        checkTimeZone("+03:01", "2012-01-01 00:01:00", "2012-01-03 00:00:59", "toInt32(60)");
        checkTimeZone("+05:00", "2012-01-01 02:00:00", "2012-01-03 01:59:59", "toInt32(7200)");
        checkTimeZone("+05:30", "2012-01-01 02:30:00", "2012-01-03 02:29:59", "toInt32(9000)");
        checkTimeZone("+21:00", "2012-01-01 18:00:00", "2012-01-03 17:59:59", "toInt32(64800)");
        checkTimeZone("+23:59", "2012-01-01 20:59:00", "2012-01-03 20:58:59", "toInt32(75540)");
    }

    @Test(expected = QueryParseException.class)
    public void testInvalidTimeZone() throws Exception {
        checkTimeZone("-24:00", "", "", "");
        checkTimeZone("+24:00", "", "", "");
    }

    private void checkTimeZone(String timeZoneId, String date1, String date2, String offset) {
        QueryParams arg = getDummyParams().dimensions("ym:s:date,ym:s:dateTime").timeZone(timeZoneId).build();
        if (StringUtil.isEmpty(offset)) {
            assertTrue(sqlContainsAll(arg,
                    "MoscowStartDate AS `ym:s:date`",
                    "UTCStartTime AS `ym:s:dateTime`",
                    "`ym:s:date` >= toDate('" + date1 + "')",
                    "`ym:s:date` <= toDate('" + date2 + "')"
            ));
        } else {
            assertTrue(sqlContainsAll(arg,
                    "toDate(`ym:s:dateTime`) AS `ym:s:date`",
                    "UTCStartTime + " + offset + " AS `ym:s:dateTime`",
                    "UTCStartTime >= toDateTime('" + date1 + "')",
                    "UTCStartTime <= toDateTime('" + date2 + "')"
            ));
        }
    }

    /*@Test
    public void testEntitiesKeyJoin() throws Exception {

        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .dimensions("ym:s:advEngine")
                .metrics("ym:s:visits")
                .filtersBraces("ym::paramsLevel1=='ololo'")
                .offset(0)
                .limit(100)
                .build();
        Query query = apiUtils.parseQuery(arg);
        {
            Filter f = new ToManyTransition(query.getDimensionFilters(), TargetTable.VISITS.getMeta().toEntity(), ToManyTransition.Type.EXISTS);
            StringBuilder sb = new StringBuilder();
            f.appendSql(sb, apiUtils.getTemplateSource(), query.getQueryContext());
            System.out.println(sb.toString());
        }
        {
            Filter f = new ToManyTransition(query.getDimensionFilters(), TargetTable.VISITS.getMeta().toEntity(), ToManyTransition.Type.FORALL);
            StringBuilder sb = new StringBuilder();
            f.appendSql(sb, apiUtils.getTemplateSource(), query.getQueryContext());
            System.out.println(sb.toString());
        }


    }*/

    // USER FUCKING CENTRIC

    @Test
    public void testUserPattern1() throws Exception {
        QueryParams arg = getDummyParams()
                .filtersBraces("user_pattern(6daysAgo, 3daysAgo, cond(ym:pv, ym:pv:URL=@'sasha_grey'))")
                .build();
        Query query = apiUtils.parseQuery(arg);
        Filter dimensionFilters = query.getDimensionFilters().get();

        assertTrue(dimensionFilters instanceof EventPattern);
        EventPattern pattern = (EventPattern) dimensionFilters;
        ZebraList<EventCondition, EventSequenceRelation> patternList = pattern.getPattern();
        assertTrue(patternList.getBlacks().size() == 1);

        EventCondition firstCondition = patternList.getBlacks().get(0);
        Filter filter = firstCondition.getFilter();

        assertEquals("ym:pv:URL", ((SelectPartFilter) filter).getSelectPart().toApiName());
    }

    @Test
    public void testUserPattern2() throws Exception {
        QueryParams arg = getDummyParams()
                .filtersBraces("user_pattern(2015-04-01, 2015-04-03, cond(ym:s, ym:s:startURL=@'sasha_grey') cond(ym:s, ym:s:startURL=@'putin'))")
                .build();
        Query query = apiUtils.parseQuery(arg);
        Filter dimensionFilters = query.getDimensionFilters().get();

        assertTrue(dimensionFilters instanceof EventPattern);
        EventPattern pattern = (EventPattern) dimensionFilters;
        ZebraList<EventCondition, EventSequenceRelation> patternList = pattern.getPattern();
        assertTrue(patternList.getBlacks().size() == 2);
        assertTrue(patternList.getWhites().size() == 1);

        Filter f1 = patternList.getBlacks().get(0).getFilter();
        assertEquals("ym:s:startURL", ((SelectPartFilter) f1).getSelectPart().toApiName());
        assertEquals("sasha_grey", ((SelectPartFilterValues) f1).getValuePart().asValuePart().get().getValue());

        assertEquals(EventSequenceRelation.Type.any, patternList.getWhites().get(0).getType());

        Filter f2 = patternList.getBlacks().get(1).getFilter();
        assertEquals("ym:s:startURL", ((SelectPartFilter) f2).getSelectPart().toApiName());
        assertEquals("putin", ((SelectPartFilterValues) f2).getValuePart().asValuePart().get().getValue());

    }

    @Test
    public void testUserPattern3() throws Exception {
        QueryParams arg = getDummyParams()
                .filtersBraces("user_pattern(2015-04-01, 2015-04-03, cond(ym:s, ym:s:startURL=@'sasha_grey') time(> 40 sec) cond(ym:s, ym:s:startURL=@'putin'))")
                .build();
        Query query = apiUtils.parseQuery(arg);
        Filter dimensionFilters = query.getDimensionFilters().get();

        assertTrue(dimensionFilters instanceof EventPattern);
        EventPattern pattern = (EventPattern) dimensionFilters;
        ZebraList<EventCondition, EventSequenceRelation> patternList = pattern.getPattern();
        assertTrue(patternList.getBlacks().size() == 2);
        assertTrue(patternList.getWhites().size() == 1);

        Filter f1 = patternList.getBlacks().get(0).getFilter();
        assertEquals("ym:s:startURL", ((SelectPartFilter) f1).getSelectPart().toApiName());
        assertEquals("sasha_grey", ((SelectPartFilterValues) f1).getValuePart().asValuePart().get().getValue());

        assertEquals(EventSequenceRelation.Type.time, patternList.getWhites().get(0).getType());
        assertEquals(EventSequenceRelation.Unit.sec, patternList.getWhites().get(0).getUnit());
        assertEquals(Relation.GT, patternList.getWhites().get(0).getRelation());

        Filter f2 = patternList.getBlacks().get(1).getFilter();
        assertEquals("ym:s:startURL", ((SelectPartFilter) f2).getSelectPart().toApiName());
        assertEquals("putin", ((SelectPartFilterValues) f2).getValuePart().asValuePart().get().getValue());

    }

    @Test
    public void testUserPattern4() throws Exception {
        QueryParams arg = getDummyParams()
                .filtersBraces("user_pattern(2015-04-01, 2015-04-03)")
                .build();
        Query query = apiUtils.parseQuery(arg);
        Filter dimensionFilters = query.getDimensionFilters().get();

        assertTrue(dimensionFilters instanceof EventPattern);
        EventPattern pattern = (EventPattern) dimensionFilters;
        ZebraList<EventCondition, EventSequenceRelation> patternList = pattern.getPattern();
        assertTrue(patternList == null);

        assertEquals("2015-04-01", pattern.getPatternStartDate());
        assertEquals("2015-04-03", pattern.getPatternEndDate());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByVisitEvent() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:gender")
                .filtersBraces("exists ym:s:userID with (ym:s:goalReachesAny==1)")
                .build();
        assertTrue(sqlContainsAll(arg, "select Sex - 1 AS `ym:s:gender`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 and UserID GLOBAL IN (select UserID AS `ym:s:userID` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 AND greatest(GoalReachesAny,0) = 1) and `ym:s:gender` != -1 " +
                "group by `ym:s:gender` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:gender` asc " +
                "limit 0"));
    }

    //@Test
    @Ignore("подзапрос с таким фильтром должен быть с группировкой и без селекта метрик. на пустой список метрик у нас много где ругается движок, надо различать ситуацию корневого запроса и подзапроса." +
            "мобильной метрике возможно для юзерцентрических вещей такие фильтры тоже будут нужны. пока отменяем их работу. " +
            "поломалось после добавления совместимости между отчетом и фильтром по юзерцентрику по событиям из директ-расходов. ")
    public void testLargeRegionFilter() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:gender")
                .filtersBraces("exists ym:s:regionCity with (ym:s:visits>1000)")
                .build();
        assertTrue(sqlContainsAll(arg, "select Sex - 1 AS `ym:s:gender`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 and regionToCity(RegionID) GLOBAL IN (select regionToCity(RegionID) AS `ym:s:regionCity` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 AND `ym:s:regionCity` != 0 " +
                "group by `ym:s:regionCity` " +
                "with totals  " +
                "having sum(Sign) > 1000.0) and `ym:s:gender` != -1 " +
                "group by `ym:s:gender` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:gender` asc " +
                "limit 0"));
    }


    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByHitEventAndDateCondition() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:gender")
                .filtersBraces("exists ym:pv:userID with (ym:pv:URL=='' and ym:pv:specialDefaultDate == '2012-01-01')")
                .build();
        assertTrue(sqlContainsAll(arg, "select Sex - 1 AS `ym:s:gender`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 and UserID GLOBAL IN (select UserID AS `ym:pv:userID` from default.hits_layer " +
                "where EventDate = toDate('2012-01-01') and CounterID = 100 and NOT DontCountHits AND NOT Refresh AND URL = '') and `ym:s:gender` != -1 " +
                "group by `ym:s:gender` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 AND uniqUpTo(10)(UserID) >= 10.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:gender` asc " +
                "limit 0"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserReportSimple() {
        QueryParams arg = getDummyParams()
                .metrics("ym:u:users,ym:u:avgUserAgeSeconds")
                .dimensions("ym:u:gender")
                .filtersBraces("ym:u:age=='45'")
                .build();
        assertTrue(sqlContainsAll(arg, "select `ym:s:gender` AS `ym:u:gender`, " +
                "count() AS `ym:u:users`, " +
                "avg(`ym:s:userAgeSeconds`) AS `ym:u:avgUserAgeSeconds` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender`, " +
                "argMax(roundAge(Age),StartDate) AS `ym:s:age`, " +
                "argMax(toInt32(StartTime) - toInt32(FirstVisit),StartTime) AS `ym:s:userAgeSeconds` " +
                "from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:age` = 45 AND `ym:s:gender` != -1 " +
                "group by `ym:s:gender` " +
                "with totals  " +
                "order by `ym:u:users` desc, " +
                "`ym:u:gender` asc " +
                "limit 0"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByUserDim() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .filtersBraces("ym:u:gender=='male'")
                .build();
        assertTrue(sqlContainsAll(arg, "select Hits AS `ym:s:hitsCount`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 AND UserID GLOBAL IN (select `ym:s:userID` AS `ym:u:userID` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 100 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:gender` = 0) " +
                "group by `ym:s:hitsCount` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:hitsCount` asc " +
                "limit 0"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByUserDim2() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .counterId(42)
                .filtersBraces("ym:u:gender=='male' or ym:u:goal169227Reaches > 0")
                .build();
        assertTrue(sqlContainsAll(arg, "select Hits AS `ym:s:hitsCount`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 AND UserID GLOBAL IN (select `ym:s:userID` AS `ym:u:userID` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender`, " +
                "sum(Sign * countEqual(`Goals.ID`,169227)) AS `ym:s:goal169227Reaches` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:gender` = 0 OR `ym:s:goal169227Reaches` > 0) " +
                "group by `ym:s:hitsCount` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:hitsCount` asc " +
                "limit 0"));
    }


    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByUserDim3() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .counterId(42)
                .filtersBraces("ym:u:gender=='male' and ym:u:goal169227Reaches > 0")
                .build();
        assertTrue(sqlContainsAll(arg, "select Hits AS `ym:s:hitsCount`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 AND UserID GLOBAL IN (select `ym:s:userID` AS `ym:u:userID` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender`, " +
                "sum(Sign * countEqual(`Goals.ID`,169227)) AS `ym:s:goal169227Reaches` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:gender` = 0 AND `ym:s:goal169227Reaches` > 0) " +
                "group by `ym:s:hitsCount` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:hitsCount` asc " +
                "limit 0"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByUserDim4() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .counterId(42)
                .filtersBraces("exists(ym:u:gender=='male' and ym:u:goal169227Reaches > 0)")
                .build();
        assertTrue(sqlContainsAll(arg, "select Hits AS `ym:s:hitsCount`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 AND UserID GLOBAL IN (select `ym:s:userID` AS `ym:u:userID` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender`, " +
                "sum(Sign * countEqual(`Goals.ID`,169227)) AS `ym:s:goal169227Reaches` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:gender` = 0 AND `ym:s:goal169227Reaches` > 0) " +
                "group by `ym:s:hitsCount` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:hitsCount` asc " +
                "limit 0"));
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterLimits() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .counterId(42)
                .filtersBraces("((((((((((" +
                        "ym:s:GCLIDPercentage\u003d\u003d1 AND " +
                        "ym:s:YCLIDPercentage\u003d\u003d1) AND " +
                        "ym:s:anyGoalConversionRate\u003d\u003d1) AND " +
                        "ym:s:avgDaysBetweenVisits\u003d\u003d1) AND " +
                        "ym:s:avgDaysSinceFirstVisit\u003d\u003d1) AND " +
                        "ym:s:avgParams\u003d\u003d1) AND " +
                        "ym:s:avgVisitDurationSeconds\u003d\u003d1) AND " +
                        "ym:s:bounceRate\u003d\u003d1) AND " +
                        "ym:s:cookieEnabledPercentage\u003d\u003d1) AND " +
                        "ym:s:ecommercePurchases\u003d\u003d1) AND " +
                        "EXISTS ym:u:userID WITH(ym:u:gender!\u003dnull))")
                .build();


        /*
0 = "ym:s:bounceRate"
1 = "ym:s:avgVisitDurationSeconds"
2 = "ym:s:avgParams"
3 = "ym:s:ecommercePurchases"
4 = "ym:s:avgDaysSinceFirstVisit"
5 = "ym:s:cookieEnabledPercentage"
6 = "ym:s:avgDaysBetweenVisits"
7 = "ym:s:YCLIDPercentage"
8 = "ym:u:gender"
9 = "ym:s:anyGoalConversionRate"
10 = "ym:s:GCLIDPercentage"
11 = "ym:s:uniqUpTo10SpecialUser"*/
        Query query = apiUtils.parseQuery(arg);
        Filter f = apiUtils.parseSimple(arg).get();
        int z = 42;
    }

    @Test
    @Ignore("METRIQA-936")
    public void testUserFilterByUserDimAndDate() {
        QueryParams arg = getDummyParams()
                .metrics("ym:s:visits")
                .dimensions("ym:s:hitsCount")
                .counterId(42)
                .filtersBraces("exists(ym:u:gender=='male' and ym:u:specialDefaultDate=='2012-01-01')")
                .build();
        assertTrue(sqlContainsAll(arg, "select Hits AS `ym:s:hitsCount`, " +
                "sum(Sign) AS `ym:s:visits` from default.visits_layer " +
                "where StartDate >= toDate('2012-01-01') and StartDate <= toDate('2012-01-02') and CounterID = 42 AND UserID GLOBAL IN (select `ym:s:userID` AS `ym:u:userID` from " +
                "(select UserID AS `ym:s:userID`, " +
                "argMax(Sex - 1,StartDate) AS `ym:s:gender` from default.visits_layer " +
                "where StartDate = toDate('2012-01-01') AND CounterID = 42 " +
                "group by `ym:s:userID` " +
                "with totals  settings max_rows_to_group_by=0) " +
                "where `ym:s:gender` = 0) " +
                "group by `ym:s:hitsCount` " +
                "with totals  " +
                "having `ym:s:visits` > 0.0 " +
                "order by `ym:s:visits` desc, " +
                "`ym:s:hitsCount` asc " +
                "limit 0"));
    }


    public boolean compareSql(String expected, QueryParams queryParams) {
        Query query = apiUtils.parseQuery(queryParams);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        return expected.equals(sql);
    }

    public boolean sqlContainsAll(QueryParams queryParams, String... fragments) {
        Query query = apiUtils.parseQuery(queryParams);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        return Arrays.stream(fragments).allMatch(f -> {
            if (!sql.contains(f)) {
                System.err.println("Not found: " + f);
                return false;
            }
            return true;
        });
    }

    public boolean sqlContainsNone(QueryParams queryParams, String... fragments) {
        Query query = apiUtils.parseQuery(queryParams);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        return !Arrays.stream(fragments).anyMatch(sql::contains);
    }

    public static QueryParams getDummyParams() {
        return QueryParams.create()
                .counterId(100)
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .metrics("ym:s:visits")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain());
    }

    private interface WildcardEscape {
        String escape(String wildcard, Relation relation);
    }

}
