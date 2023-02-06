package ru.yandex.metrika.segments;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.io.ByteStreams;
import gnu.trove.set.hash.TLongHashSet;
import org.apache.http.HttpEntity;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.mockito.Mockito;

import ru.yandex.metrika.api.constructor.response.ConstructorResponseDrilldown;
import ru.yandex.metrika.api.constructor.response.ConstructorResponseStatic;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateFactory;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.locale.LocaleGeobase;
import ru.yandex.metrika.managers.CurrencyInfoProvider;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.doc.DocumentationSourceImpl;
import ru.yandex.metrika.segments.core.parser.OneMetricParser;
import ru.yandex.metrika.segments.core.parser.ParamAttributeParser;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.secure.RestrictionType;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.site.RowsUniquesProvider;
import ru.yandex.metrika.segments.site.SamplerSite;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.Decoders;
import ru.yandex.metrika.segments.site.decode.DecodersStub;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.HttpClientUtils;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.geobase.GeoBase;
import ru.yandex.metrika.util.json.ObjectMappersFactory;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.route.RouteConfigSimple;

import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.anyString;

/**
 * Created by orantius on 4/3/15.
 */
public class TableJoinTests {

    public ApiUtils apiUtils;

    private Decoders decoders;
    private Decoders decodersEn;
    private MySqlJdbcTemplate template;
    //private MySqlJdbcTemplate visorTemplate;

    @Rule
    public ExpectedException exception = ExpectedException.none();
    private GeoBase geoBase;
    private LocaleGeobase localeGeobase;
    public DecoderBundle decoderBundle;
    public SimpleProvidersBundle providersBundle;
    private DocumentationSourceImpl documentationSource;
    private TestJoinBundleFactory bundleFactory;
    private AttributeParamsImpl attributeParams;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        decoders = new DecodersStub();
        decodersEn = new DecodersStub();
        decoderBundle = Mockito.mock(DecoderBundle.class);
        Mockito.when(decoderBundle.getDecodersForLang(Mockito.anyString()))
                .thenReturn(new DecodersStub());
        GoalIdsDaoImpl goalIdsDao = Mockito.mock(GoalIdsDaoImpl.class);
        Mockito.when(goalIdsDao.getGoals(Mockito.anyInt()))
                .thenReturn(new TLongHashSet(Arrays.asList(12345L, 23456L, 34567L, 45678L)));
        apiUtils = new ApiUtils();
        CurrencyService currencyService = Mockito.mock(CurrencyService.class);
        Mockito.when(currencyService.getCurrency(anyString())).thenReturn(Optional.of(new ru.yandex.metrika.managers.Currency(42, "ABC","name")));
        Mockito.when(currencyService.getCurrenciesMap()).thenReturn(new HashMap<String, String>());
        CurrencyInfoProvider cip = Mockito.mock(CurrencyInfoProvider.class);
        //currencyService.afterPropertiesSet();
        GeoPointDao geoPointDao = new GeoPointDao();
        attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService,cip);
        apiUtils.setAttributeParams(attributeParams);
        ApiUtilsConfig apiUtilsConfig = new ApiUtilsConfig();
        apiUtils.setConfig(apiUtilsConfig);
        TableSchemaSite tableSchema = new TableSchemaSite();
        apiUtils.setTableSchema(tableSchema);
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        providersBundle = new SimpleProvidersBundle();
        providersBundle.setLocaleDictionaries(localeDictionaries);
        providersBundle.setAttributeParams(attributeParams);
        providersBundle.afterPropertiesSet();


        apiUtils.setProvidersBundle(providersBundle);
        apiUtils.setSampler(new SamplerSite(apiUtilsConfig.getSampleSizes(), apiUtilsConfig.getGlobalSampleSizes(), apiUtilsConfig.getTuplesSampleSizes(), new RowsUniquesProvider() {}));

        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setIdDecoderBundle(decoderBundle);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        visitProvidersBundle.setAttributeParams(attributeParams);
        visitProvidersBundle.afterPropertiesSet();

        apiUtils.setProvidersBundle(visitProvidersBundle);

        documentationSource = new DocumentationSourceSite();
        apiUtils.setDocumentationSource(documentationSource);
        bundleFactory = new TestJoinBundleFactory(tableSchema, visitProvidersBundle, documentationSource);
        apiUtils.setBundleFactory(bundleFactory);
        apiUtils.afterPropertiesSet();

    }

    public void grabData2d() throws Exception {
        String url = "http://localhost:8082/stat/v1/data?offset=1&limit=100&date1=2015-03-24&date2=2015-06-23" +
                "&dimensions=ym:s:paramsLevel1,ym:s:isMobile" +
                "&sort=ym:s:isMobile,ym:s:paramsLevel1" +
                "&ids=101024" +
                "&filters=ym:s:paramsLevel1=='goods' and ym:s:isMobile=='yes'" +
                "&metrics=ym:s:visits,ym:s:sumParams,ym:s:countParams&attribution=Last&accuracy=low&lang=ru" +
                "&request_domain=ru&";
        System.out.println("url = " + url);
        HttpEntity entity = HttpClientUtils.httpGet(url);
        ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();
        String content = new String(ByteStreams.toByteArray(entity.getContent()));
        ConstructorResponseStatic er = mapper.readValue(content, ConstructorResponseStatic.class);
        er.getData().forEach(row -> {
            System.out.println(String.format("%20s", row.getDimensions().get(0).get("name")) + "\t" +
                    "\"" + String.format("%s", row.getDimensions().get(1).get("name")) + "\"\t" +
                    Arrays.stream(row.getMetrics()).map(d -> String.format("%13d", (long) (double) d)).collect(Collectors.joining("\t")));
        });
        System.out.println(String.format("%20s", "totals") + "\t" +
                String.format("%s", "totals") + "\t" +
                Arrays.stream(er.getTotals()).map(d -> String.format("%13d", (long) (double) d)).collect(Collectors.joining("\t")));
    }

    public void grabData1d() throws Exception {
        String url = "http://localhost:8082/stat/v1/data?offset=1&limit=100&date1=2015-03-24&date2=2015-06-23" +
                "&dimensions=ym:s:paramsLevel1" +
                "&ids=101024" +
                "&filters=all(ym:s:paramsLevel1!='goods')" +
                "&metrics=ym:s:visits,ym:s:sumParams,ym:s:countParams&attribution=Last&accuracy=low&lang=ru" +
                "&request_domain=ru&";
        System.out.println("url = " + url);
        HttpEntity entity = HttpClientUtils.httpGet(url);
        ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();
        String content = new String(ByteStreams.toByteArray(entity.getContent()));
        ConstructorResponseStatic er = mapper.readValue(content, ConstructorResponseStatic.class);
        er.getData().forEach(row -> {
            System.out.println(
                    String.format("%20s", row.getDimensions().get(0).get("name")) + "\t" +
                    //"\"" + String.format("%s", row.getDimensions().get(0).get("name")) + "\"\t" +
                    Arrays.stream(row.getMetrics()).map(d -> String.format("%13d", (long) (double) d)).collect(Collectors.joining("\t")));
        });
        System.out.println(String.format("%20s", "totals") + "\t" +
                Arrays.stream(er.getTotals()).map(d -> String.format("%13d",(long)(double)d)).collect(Collectors.joining("\t")));
    }

    public void grabDataDD() throws Exception {
        String url = "http://localhost:8082/stat/v1/data/drilldown?offset=1&limit=100&date1=2015-03-24&date2=2015-06-23" +
                //"&dimensions=ym:s:paramsLevel1,ym:s:isMobile" +
                //"&parent_id=[\"yes\"]"+
                "&dimensions=ym:s:isMobile,ym:s:paramsLevel1" +
                "&ids=101024" +
                "&filters=" +
                "&metrics=ym:s:visits,ym:s:sumParams,ym:s:countParams&attribution=Last&accuracy=low&lang=ru" +
                "&request_domain=ru&";
        System.out.println("url = " + url);
        HttpEntity entity = HttpClientUtils.httpGet(url);
        ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();
        String content = new String(ByteStreams.toByteArray(entity.getContent()));
        ConstructorResponseDrilldown er = mapper.readValue(content, ConstructorResponseDrilldown.class);
        er.getData().forEach(row -> {
            System.out.println(
                    String.format("%20s", row.getDimension().get("name")) + "\t" +
                            //"\"" + String.format("%s", row.getDimensions().get(0).get("name")) + "\"\t" +
                            Arrays.stream(row.getMetrics()).map(d -> String.format("%13d", (long) (double) d)).collect(Collectors.joining("\t")));
        });
        System.out.println(String.format("%20s", "totals") + "\t" +
                Arrays.stream(er.getTotals()).map(d -> String.format("%13d",(long)(double)d)).collect(Collectors.joining("\t")));
    }

    @Ignore
    @Test
    public void testJoin() throws Exception {
        QueryParams arg = getDummyParams()
                .dimensions("ym:ad:directCampaignName")
                .metrics("ym:ad:visits,ym:ad:uniqLogID")
                .offset(0)
                .limit(100)
                .build();
        //Map<String, List<Metric>> byApiNameMetrics = apiUtils.getParserFactory().getByApiNameMetrics();
        //List<String> collect = byApiNameMetrics.keySet().stream().filter(m -> m.startsWith("ym:ad:")).collect(Collectors.toList());
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        System.out.println(sql);
        assertTrue(sql.contains("bitmaskToArray(Interests) AS interests_alias"));
        assertTrue(sql.contains("arrayEnumerateUniq(bitmaskToArray(Interests)) "));
    }

    private QueryParams getDummyParams() {
        return QueryParams.create()
                .counterId(101024)
                .startDate("2015-01-01")
                .endDate("2015-01-02")
                .metrics("ym:s:visits")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain());
    }

    @Ignore
    @Test
    public void testJoin2() throws Exception {
        // common attributes. = browser , networkID , OS , regionCountry
        // ym:s:visits , ym:s:hitsCount
        // ym:pv:windowName , ym:pv:hits
        QueryParams arg = getDummyParams()
                .dimensions("ym:vh:browser")
                .metrics("ym:vh:sumHits,ym:vh:sumHitsCount")
                .filtersBraces("ym:vh:regionCountry==225 and ym:vh:sumHits > 10")
                .sort("-ym:vh:sumHits")
                .offset(0)
                .limit(100)
                .build();
        //Map<String, List<Metric>> byApiNameMetrics = apiUtils.getParserFactory().getByApiNameMetrics();
        //List<String> collect = byApiNameMetrics.keySet().stream().filter(m -> m.startsWith("ym:vh:")).collect(Collectors.toList());
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);

        System.out.println(sql);
        assertTrue(sql.contains("bitmaskToArray(Interests) AS interests_alias"));
        assertTrue(sql.contains("arrayEnumerateUniq(bitmaskToArray(Interests)) "));
    }

    // ssh -A -L 33123:localhost:8123 mtlog03-01-1
    @Ignore
    @Test
    public void testMETR15395() throws Exception {
        HttpTemplate template = new HttpTemplateFactory().getTemplate(new RouteConfigSimple("localhost", 33123), new MetrikaClickHouseProperties());
        QueryParams arg = QueryParams.create()
                .counterIds(new int[]{160656})
                .directClientIds(new int[]{3126011})
                .startDate("2015-06-20")
                .endDate("2015-06-21")
                .metrics("ym:s:visits")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .dimensions("ym:ad:URLPathLevel1Hash")
                .metrics("ym:ad:anyGoalConversionRate")
                .limit(100)
                .build();
        // перебираем все атрибуты в визитах и хитах.
        //Map<String, List<Metric>> byApiNameMetrics = apiUtils.getParserFactory().getByApiNameMetrics();
        //List<String> collect = byApiNameMetrics.keySet().stream().filter(m -> m.startsWith("ym:vh:")).collect(Collectors.toList());
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        template.query(sql, (r, i)->{
            System.out.println(r.getString(1)+" "+ r.getString(2)+" "+ r.getString(3)+" ");
            return null;
        });
    }

    // ssh -A -L 31123:localhost:8123 mtlog01-01-1
    @Ignore
    @Test
    public void testJoin3() throws Exception {
        Set<String> commonAtts = getCommonAttributeNames();

        Set<String> mNames = getUnionMetricNames();
        HttpTemplate template = new HttpTemplateFactory().getTemplate(new RouteConfigSimple("localhost", 31123), new MetrikaClickHouseProperties());

        // в таком виде метрики и атрибуты генерят внятный sql, теми оговорками, которые приведены в методе ниже.
        for (String attribute : commonAtts) {
            processAttributeAndMetric(template, attribute, "avgAge");
        }
        for (String metric : mNames) {
            processAttributeAndMetric(template, "Age", metric);
        }
    }

    public void processAttributeAndMetric(HttpTemplate template, String attribute, String metric) {
        if("uniqInterestID".compareTo(metric) > 0) return;
        try {
            Thread.sleep(150);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("common att name = " + attribute+" metric="+metric);
        // WTF
        if(attribute.endsWith("IconType")) return; // атрибут пустой, но по нему можно группировать и запрос падает уже в базе.
        // ClientData имеет тип дата и выражение toString(..) FIXED
        // MetrageFlash3 MetrageFlash4 были и в хитах и в визитах, хотя в визитах нет колонок. FIXED
        if(attribute.endsWith("ParsedParamsRaw")) return;

        if("SearchPhrase".equals(attribute)) return;
        if(attribute.startsWith("Moscow")) return; // unknown colmn UTCStartTime - баг в CH. задача есть.

        // argMax fix, quantileDeterministic fix.
        if(metric.startsWith("qDeterm")) return; // глючит в том числе на стороне CH.
        if(metric.startsWith("uniqVal")) return; // можно использовать только в additionalKeys, иначе запрос падает без группировки по основному атрибуту.
        if(metric.endsWith("ParsedParamsRaw")) return; // массив строк не работает нормально нигде.
        if(metric.contains("Mirror")) return; // no mirrorDao in TableJoinTests.
        if(metric.contains("DirectClickOrderOwner")) return; // wrong configuration of DirectClickService
        if(metric.endsWith("ParamsQuantity")) return; // этот атрибут, по-моему, вообще не работает.
        if(metric.endsWith("Params")) return; // avgParams тоже не работает, потому что без джойна
        if(metric.endsWith("ParamsValueDouble")) return; // ValueDouble в arrayMap, а Quantity просто так. не работает.
        if(metric.endsWith("paramsNumber")) return; // ValueDouble в arrayMap, а Quantity просто так. не работает.
        if(metric.endsWith("uniqInterestID")) return; // массив не работает в агрегате в тупую uniq(bitmaskToArray(Interests))

        if(metric.endsWith("AdvEngineWVID")) return; // пустой атрибут, который нельзя вставлять в sql. но для него создалась метрика.
        if(metric.endsWith("GoalDimensionID")) return; // атрибут в sql равен ID, такой колонки нет.

        if(metric.contains("Metrage")) return; // фейковые атрибуты, вообще не нужны в этом неймспейсе. и уж хотя бы в VisitAttributes

        // мы не умеем в метрики которые MIM, metric factory, вот это все. поэтому целевые вещи не работают, хотя должны.
        if(metric.startsWith("goal<goal_id>")) return; // видимо не работают парметризованные метрики. или метрики по параметризованным атрибутам.
        /*if(metric.endsWith("<currency>AdCost")) return;// goal42RUBAdCost параметр в атрибуте и параметр в метрике - не сработало. надо разбираться.
        if(metric.endsWith("<currency>AdCostPerVisit")) return;// goal42RUBAdCost параметр в атрибуте и параметр в метрике - не сработало. надо разбираться.
        if(metric.endsWith("<currency>CPA")) return;// goal42RUBAdCost параметр в атрибуте и параметр в метрике - не сработало. надо разбираться.
        if(metric.endsWith("<currency>ROI")) return;// goal42RUBAdCost параметр в атрибуте и параметр в метрике - не сработало. надо разбираться.*/

        // декодер декодит TraficSource == organic в TSID = 1234567890.  - @see DecoderStub.
        // а также их неправильное кол-во для фраз в хитах.


        // TODO CounterID / OrderID фильтры.
        // TODO Transition
        // TODO UserCentric
        QueryParams arg = getDummyParams()
                //.dimensions("ym:vh:datePeriodWeekName")
                //.dimensions("ym:vh:datePeriod<group>Name")
                .dimensions("ym:vh:" + buildGoodQPName(attribute))
                .metrics("ym:vh:sumHits,ym:vh:sumHitsCount,ym:vh:" + buildGoodQPName(metric))
                .filtersBraces("ym:vh:regionCountry==225 and ym:vh:sumHits > 10")
                .sort("-ym:vh:sumHits")
                .group(GroupType.week)
                        //.otherParams(new HashMap<>())
                .offset(0)
                .limit(100)
                .build();
        // перебираем все атрибуты в визитах и хитах.
        //Map<String, List<Metric>> byApiNameMetrics = apiUtils.getParserFactory().getByApiNameMetrics();
        //List<String> collect = byApiNameMetrics.keySet().stream().filter(m -> m.startsWith("ym:vh:")).collect(Collectors.toList());
        Query query = apiUtils.parseQuery(arg);
        String sql = apiUtils.toChQuery(query);
        int rows = template.query(sql, (rs, rowNum) -> null).size();
        System.out.println(//sql +
                "\n rows="+rows);
    }

    @NotNull
    public Set<String> getUnionMetricNames() {

        Set<String> bundleMetricNames = getBundleMetricNames(bundleFactory.getHitAttributes());
        Set<String> bundleMetricNames2 = getBundleMetricNames(bundleFactory.getVisitAttributes());
        bundleMetricNames.addAll(bundleMetricNames2);
        return bundleMetricNames;
    }

    @NotNull
    public Set<String> getBundleMetricNames(AttributeBundle hitAttributes) {
        Set<String> mNames = new TreeSet<>();
        Map<String, List<OneMetricParser>> metrics = hitAttributes.buildMetrParsers(apiUtils.getAttributeParams());
        // TODO fix
        metrics.values().stream().flatMap(f->f.stream()).map(m->m.getPrefixSuffix().getLeft()).forEach(n->mNames.add(n));
        /*for (MetricInternalMeta metric : metrics) {
            String mName = metric.getName();
            mNames.add(mName);
        }*/
        Set<AbstractAttribute> attributes = hitAttributes.getAttributes().stream()
                .filter(a -> a.getRestrictionType() == RestrictionType.COMMON).collect(Collectors.toSet());

        /*Map<String, List<Metric>> aggs = AttributeBundle.makeByNameMetrics(attributes, Collections.emptySet());
        for (List<Metric> metricList : aggs.values()) {
            Metric metric = metricList.get(0);
            String mName = metric.toApiName();
            String ns = metric.getTarget().getNamespace();
            mNames.add(mName.substring(ns.length(), mName.length()));
        }*/
        return mNames;
    }

    @NotNull
    public Set<String> getCommonAttributeNames() {
        AttributeBundle hitAttributes = bundleFactory.getHitAttributes();
        AttributeBundle visitAttributes = bundleFactory.getVisitAttributes();
        return getCommonAttributeNames(hitAttributes, visitAttributes);
    }

    @NotNull
    public Set<String> getCommonAttributeNames(AttributeBundle hitAttributes, AttributeBundle visitAttributes) {
        Set<String> hitNames = new TreeSet<>(); //404
        for (AbstractAttribute attribute : hitAttributes.getAttributes()) {
            hitNames.add(attribute.getNameWithoutParameter());
        }
        for (ParamAttributeParser paramAttributeParser : hitAttributes.getParamAttributeParsers().values()) {
            hitNames.add(paramAttributeParser.getId());
        }

        Set<String> visitNames = new TreeSet<>();//859
        for (AbstractAttribute attribute : visitAttributes.getAttributes()) {
            visitNames.add(attribute.getNameWithoutParameter());
        }
        for (ParamAttributeParser paramAttributeParser : visitAttributes.getParamAttributeParsers().values()) {
            visitNames.add(paramAttributeParser.getId());
        }
        hitNames.retainAll(visitNames); //335.
        return hitNames;
    }

    private String buildGoodQPName(String attname) { // QP = query part.
        return StringUtil.smartUncapitalize(attname)
                .replaceAll("<group>", attributeParams.getGroupParam().getDefaultValue(null))
                .replaceAll("<auto_group_size>", "1")
                .replaceAll("<attribution>", "Last")
                .replaceAll("<currency>", "RUB")
                .replaceAll("<goal_id>", "42")
                .replaceAll("<quantile>", attributeParams.getQuantileParam().getDefaultValue(null));

    }


}
