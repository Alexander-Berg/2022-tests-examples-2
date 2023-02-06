package ru.yandex.metrika;

import java.util.Collections;
import java.util.List;
import java.util.function.BinaryOperator;

import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentsDao;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.locale.LocaleDecoderSimple;
import ru.yandex.metrika.locale.NotALocaleDecoder;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.parser.FilterParseResult;
import ru.yandex.metrika.segments.core.parser.filter.FilterParserBraces2;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.FilterVisitor;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterNull;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterQuery;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterValues;
import ru.yandex.metrika.segments.core.query.filter.pattern.EventPattern;
import ru.yandex.metrika.segments.core.query.filter.pattern.SimpleHavingPattern;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParams;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.site.bundles.CommonBundleFactory;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecoderType;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.collections.MapBuilder;
import ru.yandex.metrika.util.locale.LocaleDecoder;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

//import ru.yandex.metrika.metr25664.MysqlDatabaseClient;

/**
 * тут мы попробуем выполнить некоторый анализ структуры реально существующих сегментов, для этого нам
 * понадобится распарсить их, либо до состояния обычных фильтров, либо до состояния вообще фильтров и сделать sql.
 */
public class SegmentParser {
    public static void main(String[] args) throws Exception {

        //MysqlDatabaseClient conv = new MysqlDatabaseClient("localhost", 3312, "conv_main", "metrika", "v");
        MySqlJdbcTemplate convmain = null;//conv.getMySqlJdbcTemplate();

        ApiUtils nApiUtils = new ApiUtils();
        nApiUtils.setConfig(new ApiUtilsConfig());

        TableSchemaSite tableSchema = new TableSchemaSite();
        DocumentationSourceSite documentationSource = new DocumentationSourceSite();
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        DecoderBundle decoderBundle = new DecoderBundle();
        LocaleDecoderSimple tsDecoder = new LocaleDecoderSimple();
        tsDecoder.setTemplate(convmain);
        tsDecoder.setTableName("TraficSources");
        tsDecoder.setDescriptionColumnName("TraficSource");
        tsDecoder.setLocaleDictionaries(localeDictionaries);
        tsDecoder.afterPropertiesSet();
        NotALocaleDecoder seRootDecoder = new NotALocaleDecoder();
        seRootDecoder.setTemplate(convmain);
        seRootDecoder.setTableName("SearchEngines");
        seRootDecoder.setDescriptionColumnName("StrId");
        seRootDecoder.setWhereString("ParentId IS NULL");
        seRootDecoder.afterPropertiesSet();

        LocaleDecoderSimple seDecoder = new LocaleDecoderSimple();
        seDecoder.setTemplate(convmain);
        seDecoder.setTableName("SearchEngines");
        seDecoder.setDescriptionColumnName("SearchEngine");
        seDecoder.setLocaleDictionaries(localeDictionaries);
        seDecoder.afterPropertiesSet();

        LocaleDecoderSimple uaDecoder = new LocaleDecoderSimple();
        uaDecoder.setTemplate(convmain);
        uaDecoder.setTableName("UserAgent");
        uaDecoder.setDescriptionColumnName("UserAgent");
        uaDecoder.setLocaleDictionaries(localeDictionaries);
        uaDecoder.afterPropertiesSet();

        LocaleDecoderSimple snDecoder = new LocaleDecoderSimple();
        snDecoder.setTemplate(convmain);
        snDecoder.setTableName("SocialNetworks");
        snDecoder.setDescriptionColumnName("Name");
        snDecoder.setLocaleDictionaries(localeDictionaries);
        snDecoder.afterPropertiesSet();

        LocaleDecoderSimple beDecoder = new LocaleDecoderSimple();
        beDecoder.setTemplate(convmain);
        beDecoder.setTableName("BrowserEngines");
        beDecoder.setDescriptionColumnName("Name");
        beDecoder.setLocaleDictionaries(localeDictionaries);
        beDecoder.afterPropertiesSet();

        LocaleDecoderSimple inDecoder = new LocaleDecoderSimple();
        inDecoder.setTemplate(convmain);
        inDecoder.setTableName("Interests");
        inDecoder.setDescriptionColumnName("Interest");
        inDecoder.setLocaleDictionaries(localeDictionaries);
        inDecoder.afterPropertiesSet();

        decoderBundle.setDecoderMap(MapBuilder.<DecoderType, LocaleDecoder>builder()
                .put(DecoderType.TRAFFIC_SOURCE, tsDecoder)
                .put(DecoderType.BROWSER, uaDecoder)
                .put(DecoderType.BROWSER_ENGINE, beDecoder)
                .put(DecoderType.SOCIAL_NETWORK, snDecoder)
                .put(DecoderType.INTERESTS, inDecoder)
                .put(DecoderType.SEARCH_ENGINE, seDecoder)
                .put(DecoderType.SEARCH_ENGINE_ROOT, seRootDecoder).build());
        decoderBundle.afterPropertiesSet();
        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setIdDecoderBundle(decoderBundle);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        GoalIdsDaoImpl goalIdsDao = new GoalIdsDaoImpl();
        goalIdsDao.setConvMain(convmain);
        goalIdsDao.afterPropertiesSet();
        CurrencyService currencyService = new CurrencyService();
        currencyService.setConvMain(convmain);
        currencyService.afterPropertiesSet();
        CountersDao cd = new CountersDao();
        cd.setCurrencyService(currencyService);
        GeoPointDao geoPointDao = new GeoPointDao();
        AttributeParams attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService, cd);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        GoalsService goalDao2 = new GoalsService();
        goalDao2.setJdbcTemplate(convmain);
        goalDao2.setDictionaries(localeDictionaries);
        goalDao2.setValidator(null);

        visitProvidersBundle.setGoalDao2(goalDao2);
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setAttributeParams(attributeParams);
        visitProvidersBundle.afterPropertiesSet();
        GAProvidersBundle gaProvidersBundle = new GAProvidersBundle();
        gaProvidersBundle.setDecoderBundle(decoderBundle);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.setAttributeParams(attributeParams);
        gaProvidersBundle.setGoalIdsDao(goalIdsDao);
        gaProvidersBundle.afterPropertiesSet();

        nApiUtils.setProvidersBundle(visitProvidersBundle);
        nApiUtils.setAttributeParams(attributeParams);
        nApiUtils.setTableSchema(tableSchema);
        nApiUtils.setDocumentationSource(documentationSource);
        nApiUtils.setBundleFactory(new CommonBundleFactory(tableSchema, documentationSource, visitProvidersBundle, gaProvidersBundle));
        nApiUtils.afterPropertiesSet();

        FilterParserBraces2 fb = new FilterParserBraces2(nApiUtils.getSelectPartParser());
//        fb.buildSimpleAST("ym:s:startURL=*'http://kofeteka.ru/catalog/coffee/?arrFilter_pf[MANUFACTURER][\\=487&set_filter=Y'");
        int s = 0;
        int sRet = 0;
        int flat = 0;
        int flatRet = 0;
        List<Segment> segments = convmain.query("select * from segments where `status` != 'deleted'", SegmentsDao.SEGMENT_ROW_MAPPER);
        for (Segment segment : segments) {
            QueryContext qc = QueryContext.defaultFields().apiUtils(nApiUtils).targetTable(TableSchemaSite.VISITS)
                    .idsByName(Collections.singletonMap(TableSchemaSite.COUNTER_ID, new int[]{segment.getCounterId() }))
                    .startDate("2018-01-01").endDate("2018-01-01").lang("ru").domain("").userType(UserType.MANAGER)
                    .build();
            if(!StringUtil.isEmpty(segment.getExpression())) {
                try {
                    FilterParseResult parseResult = fb.parseFilters(segment.getExpression(), qc);
                    if(parseResult.getDimFilter().isPresent()) {
                        Filter filter =parseResult.getDimFilter().get();
                        FilterVisitor<Boolean> visi = new FilterVisitor<Boolean>() {
                            @Override
                            public Boolean visit(EventPattern filter) {
                                return false;
                            }

                            @Override
                            public Boolean visit(SimpleHavingPattern filter) {
                                return false;
                            }

                            @Override
                            public BinaryOperator<Boolean> reducer() {
                                return (a, b) -> a && b;
                            }

                            @Override
                            public Boolean visit(SelectPartFilterQuery filter) {
                                return false;
                            }

                            @Override
                            public Boolean visit(SelectPartFilterNull filter) {
                                return true;
                            }

                            @Override
                            public Boolean visit(SelectPartFilterValues filter) {
                                return true;
                            }
                        };
                        Boolean res = filter.visit(visi);
                        System.out.println(res+" segment = " +segment.getSegmentId());
                        if(res) flat++;
                        if(segment.getIsRetargeting()) {
                            sRet++;
                            if(res) flatRet++;
                        }
                        int z = 42;
                    } else {
                        System.out.println("NO DIM FILTER " );
                    }
                    s++;
                    if((s%1000) == 0) {
                        System.out.println("s = " + s+", flat = "+ flat);
                    }
                } catch (Exception e) {
                    System.out.println(segment.getSegmentId()+": error e = " + e);
                    System.out.println(s+" segments parsed so far");
                }

            }
        }
        System.out.println("s = " + s+", flat = "+ flat+ " "+sRet + " " +flatRet);

    }
}
