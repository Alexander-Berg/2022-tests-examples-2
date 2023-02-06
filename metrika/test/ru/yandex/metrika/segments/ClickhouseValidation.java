package ru.yandex.metrika.segments;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import org.apache.logging.log4j.Level;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
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
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.bundles.UnionBundle;
import ru.yandex.metrika.segments.core.doc.DocumentationSourceImpl;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.metric.Metric;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Aggregate;
import ru.yandex.metrika.segments.site.bundles.ga.GAAttributeBundle;
import ru.yandex.metrika.segments.site.bundles.hits.HitAttributes;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.visits.VisitAttributes;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecoderType;
import ru.yandex.metrika.segments.site.decode.Decoders;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.geobase.GeoBase;
import ru.yandex.metrika.util.geobase.RegionType;
import ru.yandex.metrika.util.locale.LocaleDecoder;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.mockito.Matchers.anyString;

/**
 * Берет все дименшны и метрики и валидирует их кликхаусом
 * Если у нас когда-нибудь будет back2back тестирование,
 * нужно делать как-то так же на сете реальных данных и сравнивать все результаты
 *
 */
@Ignore
public class ClickhouseValidation {

    private static final Logger log = LoggerFactory.getLogger(ClickhouseValidation.class);

    private ApiUtils apiUtils;

    private Decoders decoders;
    private Decoders decodersEn;

    private MySqlJdbcTemplate template;

    private HttpTemplate httpTemplate;

    private LocaleDictionaries dictionaries;

    @Rule
    public ExpectedException exception = ExpectedException.none();
    private GeoBase geoBase;
    private LocaleGeobase localeGeobase;
    private DecoderBundle decoderBundle;
    private LocaleDictionaries localeDictionaries;
    SimpleProvidersBundle providersBundle = new SimpleProvidersBundle();
    GAProvidersBundle gaProvidersBundle = new GAProvidersBundle(); // TODO init
    VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle(); // TODO init
    private TableSchemaSite tableSchema;
    private DocumentationSourceImpl documentationSource;
    private AttributeParamsImpl attributeParams;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);

        template = AllDatabases.getTemplate("localhost", 3308, "root", "qwerty", "conv_main");

        httpTemplate = AllDatabases.getCHTemplate("localhost", 8123, "default");

        decoderBundle = new DecoderBundle();
        GoalIdsDaoImpl goalIdsDao = new GoalIdsDaoImpl();

        dictionaries = new LocaleDictionaries();
        dictionaries.afterPropertiesSet();

        LocaleDecoder ts        = getSimpleDecoder(dictionaries, "TraficSources", "traficSource");
        LocaleDecoder adv       = getSimpleDecoder(dictionaries, "AdvEngines2"  , "AdvEngine");
        LocaleDecoder seRoot    = getSimpleDecoder(dictionaries, "SearchEngines", "SearchEngine", "ParentId IS NULL");
        LocaleDecoder se        = getSimpleDecoder(dictionaries, "SearchEngines", "SearchEngine");

        LocaleDecoder sn        = getNotALocaleDecoder("SocialNetworks" , "Name"     );
        LocaleDecoder ua        = getNotALocaleDecoder("UserAgent"      , "UserAgent");
        LocaleDecoder os        = getNotALocaleDecoder("OS2"            , "OS"       );

        geoBase = new GeoBase();

        localeGeobase = new LocaleGeobase();
        localeGeobase.afterPropertiesSet();
        localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();

        providersBundle.setLocaleDictionaries(localeDictionaries);
        providersBundle.afterPropertiesSet();

        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        visitProvidersBundle.afterPropertiesSet();
        gaProvidersBundle.setDecoderBundle(decoderBundle);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.setGoalIdsDao(goalIdsDao);
        gaProvidersBundle.afterPropertiesSet();

        LocaleDecoder geoCountry = getGeoDecoder(RegionType.COUNTRY);
        LocaleDecoder geoCity = getGeoDecoder(RegionType.CITY);
        LocaleDecoder geoRegion = getGeoDecoder(RegionType.REGION);

        Map<DecoderType, LocaleDecoder> decoderMap = new EnumMap<>(DecoderType.class);
        decoderMap.put( DecoderType.TRAFFIC_SOURCE      , ts);
        decoderMap.put( DecoderType.SEARCH_ENGINE_ROOT  , seRoot);
        decoderMap.put( DecoderType.SEARCH_ENGINE       , se);
        decoderMap.put( DecoderType.ADV_ENGINE          , adv);
        decoderMap.put( DecoderType.SOCIAL_NETWORK      , sn);
        decoderMap.put( DecoderType.BROWSER             , ua);
        decoderMap.put( DecoderType.GEO_COUNTRY         , geoRegion);
        decoderMap.put( DecoderType.GEO_REGION          , geoCity);
        decoderMap.put(DecoderType.GEO_CITY, geoCountry);
        decoderMap.put(DecoderType.OS, os);

        decoderBundle.setDecoderMap(decoderMap);
        decoders = decoderBundle.getDecodersForLang(LocaleLangs.RU);
        decodersEn = decoderBundle.getDecodersForLang(LocaleLangs.EN);

        documentationSource = new DocumentationSourceSite();

        apiUtils = new ApiUtils();
        apiUtils.setConfig(new ApiUtilsConfig());
        CurrencyService currencyService = Mockito.mock(CurrencyService.class);
        Mockito.when(currencyService.getCurrency(anyString())).thenReturn(Optional.of(new Currency(42, "ABC", "name")));
        Mockito.when(currencyService.getCurrenciesMap()).thenReturn(new HashMap<String, String>());
        CurrencyInfoProvider cip = Mockito.mock(CurrencyInfoProvider.class);
        //currencyService.afterPropertiesSet();
        visitProvidersBundle.setCurrencyService(currencyService);
        GeoPointDao geoPointDao = new GeoPointDao();
        attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService, cip);
        apiUtils.setAttributeParams(attributeParams);
        tableSchema = new TableSchemaSite();
        apiUtils.setTableSchema(tableSchema);
        apiUtils.setProvidersBundle(providersBundle);
        apiUtils.afterPropertiesSet();

    }

    @Test
    @Ignore
    public void testTest() throws Exception {
        int hash = 0;
        QueryParams arg = QueryParams.create()
                .lang(LocaleLangs.RU)
                .counterId(4242)
                .startDate("2013-04-01")
                .endDate("2013-05-01")
                .dimensions("ym:s:trafficSource,ym:s:isWoman,ym:s:visitStartWeek,ym:s:silverlight,ym:s:browser")
                .metrics("ym:s:normVisits,ym:s:sumVisits,ym:s:sumVisitTime,ym:s:avgBounce,ym:s:percentBouncePrecise,ym:s:sumPrice,ym:s:normPrice,ym:s:sumMen,ym:s:dailyAvgVisits,ym:s:sumVisits")
                .offset(1)
                .limit(100)
                .build();
        for (int i = 0; i < 10000000; i++) {
            Query query = apiUtils.parseQuery(arg);
            String sql = apiUtils.toChQuery(query);
            hash += sql.hashCode();
        }
        System.out.println(hash);


    }

    @Test
    public void testConstrAttributes() throws Exception {
        Set<AbstractAttribute> attributes = new HashSet<>(new VisitAttributes(tableSchema, visitProvidersBundle, documentationSource).getAttributes());
        attributes.addAll(new GAAttributeBundle(gaProvidersBundle, new UnionBundle(Lists.<AttributeBundle>newArrayList())).getAttributes());
        for (AbstractAttribute attribute : attributes) {
            Set<String> badAttributes = Sets.newHashSet("ga:goal", "ga:visitParam", "ym:s:visitParamsDots");
            if (!attribute.isDimension() || badAttributes.contains(attribute.toApiName())) {
                continue;
            }
            String metric;
            if (attribute.getTarget() == TableSchemaSite.HITS) metric = "ga:pageLoadTime";
            else metric = "ga:visits";
            QueryParams arg = QueryParams.create()
                    .lang(LocaleLangs.RU)
                    .domain(LocaleDomain.getDefaultChDomain())
                    .counterId(4242)
                    .startDate("2013-04-01")
                    .endDate("2013-05-01")
                    .dimensions(attribute.toApiName())
                    .metrics(metric)
                    .offset(1)
                    .limit(100)
                    .build();
            Query query = apiUtils.parseQuery(arg);
            String sql = apiUtils.toChQuery(query);
            log.info(sql);
            httpTemplate.query(sql, rs -> {
            });

        }

    }

    @Test
    public void testConstrAttributesHits() throws Exception {
        Set<AbstractAttribute> attributes = new HashSet<>(new HitAttributes(tableSchema, visitProvidersBundle, documentationSource).getAttributes());
        for (AbstractAttribute attribute : attributes) {
            Set<String> badAttributes = Sets.newHashSet();
            if (!attribute.isDimension() || badAttributes.contains(attribute.toApiName())) {
                continue;
            }
            String metric;
            if (attribute.getTarget() == TableSchemaSite.HITS) metric = "ga:pageLoadTime";
            else metric = "ga:visits";
            QueryParams arg = QueryParams.create()
                    .lang(LocaleLangs.RU)
                    .domain(LocaleDomain.getDefaultChDomain())
                    .counterId(4242)
                    .startDate("2013-04-01")
                    .endDate("2013-05-01")
                    .dimensions(attribute.toApiName())
                    .metrics(metric)
                    .offset(1)
                    .limit(100)
                    .build();
            Query query = apiUtils.parseQuery(arg);
            String sql = apiUtils.toChQuery(query);
            log.info(sql);
            httpTemplate.query(sql, rs -> {
            });

        }

    }

    @Test
    public void testConstrAttributesMetrics() throws Exception {
        Set<AbstractAttribute> attributes = new HashSet<>(new VisitAttributes(tableSchema, visitProvidersBundle, documentationSource).getAttributes());
        for (AbstractAttribute attribute : attributes) {
            if (!"ym:s:visitParamsDots".equals(attribute.toApiName())) {
                for (Aggregate aggregate : attribute.getType().aggregates()) {
                    Metric metric = attribute.getMetric(aggregate);
                    QueryParams arg = QueryParams.create()
                            .lang(LocaleLangs.RU)
                            .domain(LocaleDomain.getDefaultChDomain())
                            .counterId(4242)
                            .startDate("2013-04-01")
                            .endDate("2013-05-01")
                            .metrics(metric.toApiName())
                            .offset(1)
                            .limit(100)
                            .build();
                    Query query = apiUtils.parseQuery(arg);
                    String sql = apiUtils.toChQuery(query);
                    httpTemplate.query(sql, rs -> {
                    });
                }
            }


        }

    }

    @Test
    public void testGAMetrics() throws Exception {
        Set<MetricInternalMeta> metrics = new GAAttributeBundle(null, new UnionBundle(Lists.<AttributeBundle>newArrayList())).metrics;

        for (MetricInternalMeta metric : metrics) {
            QueryParams arg = QueryParams.create()
                    .lang(LocaleLangs.RU)
                    .domain(LocaleDomain.getDefaultChDomain())
                    .counterId(4242)
                    .startDate("2013-04-01")
                    .endDate("2013-05-01")
                    .metrics(metric.getDim())
                    .offset(1)
                    .limit(100)
                    .build();
            Query query = apiUtils.parseQuery(arg);
            String sql = apiUtils.toChQuery(query);
            httpTemplate.query(sql, rs -> {
            });
        }
    }

    private LocaleDecoder getGeoDecoder(RegionType regionType) throws Exception {
        LocaleDecoderGeo geoDecoder = new LocaleDecoderGeo();
        geoDecoder.setGeoBase(geoBase);
        geoDecoder.setLocaleGeobase(localeGeobase);
        geoDecoder.setRegionType(regionType);
        geoDecoder.afterPropertiesSet();
        return geoDecoder;
    }

    private LocaleDecoder getSimpleDecoder(LocaleDictionaries dictionaries, String table, String column, String where) throws Exception {
        LocaleDecoderSimple ld;
        ld = new LocaleDecoderSimple();
        ld.setTableName(table);
        ld.setDescriptionColumnName(column);
        if (!StringUtil.isEmpty(where)) ld.setWhereString(where);
        ld.setTemplate(template);
        ld.setLocaleDictionaries(dictionaries);
        ld.afterPropertiesSet();
        return ld;
    }

    private LocaleDecoder getSimpleDecoder(LocaleDictionaries dictionaries, String table, String column) throws Exception {
        return getSimpleDecoder(dictionaries, table, column, null);
    }

    private NotALocaleDecoder getNotALocaleDecoder(String table, String column) throws Exception {
        NotALocaleDecoder ld = new NotALocaleDecoder();
        ld.setTableName(table);
        ld.setDescriptionColumnName(column);
        ld.setTemplate(template);
        ld.afterPropertiesSet();
        return ld;
    }

}
