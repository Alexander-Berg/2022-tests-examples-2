package ru.yandex.metrika.segments.core.parser.filter;

import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.google.common.base.Throwables;
import gnu.trove.map.hash.TObjectLongHashMap;
import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.BailErrorStrategy;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.Parser;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.tree.ParseTree;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.locale.LocaleDecoderSimple;
import ru.yandex.metrika.locale.NotALocaleDecoder;
import ru.yandex.metrika.managers.CurrencyInfoProvider;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.parse.PrintQuery;
import ru.yandex.metrika.segments.core.ApiErrors;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.parser.FilterParseResult;
import ru.yandex.metrika.segments.core.parser.QueryParseException;
import ru.yandex.metrika.segments.core.parser.filter.gen.FilterBracesLexer;
import ru.yandex.metrika.segments.core.parser.filter.gen.FilterBracesParser;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.schema.QueryEntity;
import ru.yandex.metrika.segments.core.schema.TableEntity;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.site.RowsUniquesProvider;
import ru.yandex.metrika.segments.site.SamplerSite;
import ru.yandex.metrika.segments.site.bundles.CommonBundleFactory;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecoderType;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.collections.MapBuilder;
import ru.yandex.metrika.util.locale.LocaleDecoder;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.log.Log4jSetup;

import static ru.yandex.metrika.segments.site.schema.TableSchemaSite.ADFOX_PUID_TUPLE;
import static ru.yandex.metrika.segments.site.schema.TableSchemaSite.ADFOX_TUPLE;


/**
 * партнерский интерфейс.
 * Created by orantius on 10/19/15.
 */
@Ignore("METRIQA-936")
public class FilterParserBraces2Test {

    private static final Logger log = LoggerFactory.getLogger(FilterParserBraces2Test.class);

    private static ApiUtils apiUtils;
    private static FilterParserBraces2 fpb;
    private static FilterParserBraces2 pp;

    @BeforeClass
    public static void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        MySqlJdbcTemplate conv = AllDatabases.getTemplate("localhost", 3309, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main"); // prod

        apiUtils = getApiUtils(conv);
        pp = (FilterParserBraces2) apiUtils.getFilterParser();
        //pp = new FilterParserBraces2(fpb.getSelectPartParser(), apiUtils.getCrossTableRelations());
    }

    /*@Test
    public void testFilterNPE() throws Exception {
        String fullFilterString = "( ym:s:visits )";
        QueryContext qc = getQueryContext();
        Pair<Filter, Filter> split = pp.parseFilters(fullFilterString, qc).asPair();
        System.out.println("split = " + split);
    }*/

    /*@Test
    public void testNPE() throws Exception {
        String fullFilterString = "ym:s:visits ( Λ ) == 1";
        QueryContext qc = getQueryContext();
        Pair<Filter, Filter> split = pp.parseFilters(fullFilterString, qc).asPair();
        System.out.println("split = " + split);
    }*/

    /*@Test
    public void testCast() throws Exception {
        String fullFilterString = "ym:s:gender ( Λ ) == ym:s:visits ( Λ )";
        QueryContext qc = getQueryContext();
        Pair<Filter, Filter> split = pp.parseFilters(fullFilterString, qc).asPair();
        System.out.println("split = " + split);

    }*/

    public String parseString(String arg) {
        ANTLRInputStream input = new ANTLRInputStream(arg);
        FilterBracesLexer lexer = new FilterBracesLexer(input);
        lexer.removeErrorListeners();
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        FilterBracesParser parser = new FilterBracesParser(tokens);
        parser.removeErrorListeners();
        parser.setErrorHandler(new BailErrorStrategy() {
            @Override
            public void recover(Parser recognizer, RecognitionException e) {
                throw QueryParseException.create(ApiErrors.ERR_WRONG_FILTER, arg);

            }

            @Override
            public Token recoverInline(Parser recognizer) throws RecognitionException {
                throw QueryParseException.create(ApiErrors.ERR_WRONG_FILTER, arg);
            }
        });
        ParseTree tree = parser.filterTop();
        return tree.toStringTree();
    }


    @Test
    public void testSlash() {
        {
            String s = parseString("x=='как активировать корпоративную карту сбербанк' and y==''");
            System.out.println("s = " + s);
        }
        {
            String s = parseString("x=='как активировать корпоративную карту сбербанк\\\\' and y==''");
            System.out.println("s = " + s);
        }
        {
            try {
                String s = parseString("x=='как активировать корпоративную карту сбербанк\\' and y==''");
                System.out.println("s = " + s);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        {
            String s = parseString("x=='\u0000'");
            System.out.println("s = " + s);
        }
        {
            String s = parseString("x=='\\0'");
            System.out.println("s = " + s);
        }
        {
            FBFilter s =pp.buildSimpleAST("ym:pv:URLParamName=='\n'");
            System.out.println("s = " + s);
        }
    }

    @Test
    public void testParse() {
        Iterable<String> phrases = FiltersGen.getFiltersStream();
        Map<String,Integer> errorByType = new HashMap<>();
        for (String phrase : phrases) {
            try {
                FBFilter ast = pp.buildSimpleAST(phrase);
                Pair<Optional<FBFilter>,Optional<FBFilter>> pairF = FilterParserBraces2.splitDimMetr(ast, phrase, Collections.emptySet());
                System.out.println("split = " + pairF);
                errorByType.merge("OK", 1, Integer::sum);
            } catch (Exception e) {
                errorByType.merge(e.getMessage(), 1, Integer::sum);
                System.out.println(e.getMessage()+ " arg: " +phrase);
            }
        }
        for (Map.Entry<String, Integer> e : errorByType.entrySet()) {
            System.out.println(e.getKey() +" "+ e.getValue());
        }
    }

    @Test
    public void metricFilteredTest() {
        {
            FBExpr fbExpr = pp.parseExpr("ym:s:visits[ym:s:gender=='male']");
            log.info(FBFilterTransformers.printExpr(fbExpr));
        }
        {
            FBExpr fbExpr = pp.parseExpr("ym:s:visits[ym:s:gender=='male'][ym:s:age==25]");
            log.info(FBFilterTransformers.printExpr(fbExpr));
        }
        {
            FBExpr fbExpr = pp.parseExpr("ym:s:visits/ym:s:users[ym:s:gender=='male']");
            log.info(FBFilterTransformers.printExpr(fbExpr));
        }
        {
            FBExpr fbExpr = pp.parseExpr("(ym:s:visits/ym:s:users)[ym:s:gender=='male']");
            log.info(FBFilterTransformers.printExpr(fbExpr));
        }
    }

    @Test
    public void testFilterAST() {
        String fullFilterString = "ym:s:visits > 0 and EXISTS ym:pv:eventID WITH (ym:pv:URLParamName == 'abc')";

        // вторая фаза - с наличием query context транслируем фильтр в наш обычный фильтр.
        QueryContext qc = getQueryContext();

        Pair<Optional<Filter>, Optional<Filter>> split = pp.parseFilters(fullFilterString, qc).asPair();
        log.info(split.getLeft().get().toApiString());
        log.info(split.getRight().get().toApiString());
        int z = 42;
    }

    @NotNull
    public QueryContext getQueryContext() {
        return QueryContext.newBuilder().tableSchema(apiUtils.getTableSchema())
                    .startDate("2016-01-01")
                    .endDate("2016-01-03")
                    .domain("")
                    .lang("ru")
                    .targetTable(TableSchemaSite.VISITS)
                    .apiUtils(apiUtils)
                    .userType(UserType.OWNER)
                    .otherParams(Collections.emptyMap())
                    .idsByName(MapBuilder.<String, int[]>builder().put("counter", new int[]{}).build()).build();
    }

    @Test
    public void testNN() throws Exception {
        String filter = "(ym:s:startURL!n)";
        FilterParseResult fpr = pp.parseFilters(filter, getQueryContext());
        int z = 42;
    }

    @Test
    public void parseErrorTest() throws Exception {
        String filter = "ym:s:startURL!'.*'";
        FilterParseResult fpr = pp.parseFilters(filter, getQueryContext());
        int z = 42;
    }

    @Test
    public void testMETR24405() throws Exception {
        String filter = "ym:pv:URLParamName=='\u001A><18' or ym:pv:URLParamName=='\u001A><19' ";
        FBFilter fbFilter = pp.buildSimpleAST(filter);
        String backToString = fbFilter.toString();
        FilterParseResult fpr = pp.parseFilters(filter, getQueryContext());
        int z = 42;
    }
/*
    select count() from default.hits_layer where EventDate >= toDate('2017-01-08') and CounterID = 18343495 and
    arrayExists(x_0 -> extract(x_0,'([^=]+)=') IN ('f','equals, оператор a ','\Z><18','@>872>48B5;L'),extractURLParameters(URL)) and
    arrayExists(x_0 -> extract(x_0,'([^=]+)=') IN ('@>872>48B5;L','\Z><18','f','equals, оператор a '),extractURLParameters(URL))


    select arrayExists(x_0 -> extract(x_0,'([^=]+)=') IN ('f','equals, оператор a ','\Z><18','@>872>48B5;L'),extractURLParameters('abc?f=a'))

    select arrayExists(x_0 -> extract(x_0,'([^=]+)=') IN ('g','f','@>'),extractURLParameters('abc?f=a'))
    */
    @Test
    public void testUserCentric() throws Exception {
        String filter =     "exists ym:s:userID with (ym:s:visits>3 and ym:s:specialDefaultDate <= '2daysAgo' and ym:s:specialDefaultDate >= '5daysAgo')\n"+
                "and\n"+
                "exists ym:s:userID with (ym:u:gender=='male' and ym:s:specialDefaultDate <= '2daysAgo' and ym:s:specialDefaultDate >= '5daysAgo')\n"+
                "and\n"+
                "exists ym:pv:userID with (ym:pv:URL=@'cart' and ym:pv:specialDefaultDate <= '20daysAgo' and ym:pv:specialDefaultDate >= '30daysAgo')";
        FBFilter fbFilter = pp.parseStringWithANTLR(filter);
        int z = 42;
    }

    /**
     * @return
     * @throws Exception
     */
    public static @NotNull ApiUtils getApiUtils() throws Exception {
        return getApiUtils(null);
    }
    public static @NotNull ApiUtils getApiUtils(MySqlJdbcTemplate template) throws Exception {
        ApiUtils apiUtils = new ApiUtils();
        CurrencyService currencyService = new CurrencyService();
        CurrencyInfoProvider cd = counterIds -> "RUB";
        GoalIdsDaoImpl goalIdsDao = new GoalIdsDaoImpl();
        if(template!=null) {
            goalIdsDao.setConvMain(template);
            goalIdsDao.afterPropertiesSet();
        }
        GeoPointDao geoPointDao = new GeoPointDao();
        AttributeParamsSite attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService, cd);
        apiUtils.setAttributeParams(attributeParams);
        apiUtils.setSampler(new SamplerSite(new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new RowsUniquesProvider() {}));
        TableSchemaSite tableSchema = new TableSchemaSite();
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        DocumentationSourceSite documentationSource = new DocumentationSourceSite();

        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setAttributeParams(attributeParams);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        DecoderBundle decoderBundle = new DecoderBundle();
        decoderBundle.setCheckDecoderMapCompleteness(false);
        Map<DecoderType, LocaleDecoder> decoderMap = new EnumMap<>(DecoderType.class);
        if(template!=null) {
          /*  LocaleDecoder ts = getSimpleDecoder(template, localeDictionaries, "TraficSources", "traficSource");
            decoderMap.put( DecoderType.TRAFFIC_SOURCE      , ts);
            LocaleDecoder se        = getSimpleDecoder(template, localeDictionaries, "SearchEngines", "SearchEngine");
            decoderMap.put( DecoderType.SEARCH_ENGINE       , se);
            LocaleDecoder seRoot    = getSimpleDecoder(template, localeDictionaries, "SearchEngines", "SearchEngine", "ParentId IS NULL");
            decoderMap.put( DecoderType.SEARCH_ENGINE_ROOT  , seRoot);
            NotALocaleDecoder seUrl = getNotALocaleDecoder(template, "SearchEngines", "CONCAT(URL, '?', field_name, '=')");
            decoderMap.put( DecoderType.SEARCH_PHRASE_URL  , seUrl);
            LocaleDecoder adv       = getSimpleDecoder(template, localeDictionaries, "AdvEngines2"  , "AdvEngine");
            decoderMap.put( DecoderType.ADV_ENGINE          , adv);
            LocaleDecoder advPlace  = getSimpleDecoder(template, localeDictionaries, "AdvPlaces"  , "AdvPlaceID");
            decoderMap.put( DecoderType.ADV_PLACE          , advPlace);
            LocaleDecoder advPlaceFull = getSimpleDecoder(template, localeDictionaries, "Place"  , "PlaceID", "PlaceDescription", "Options != 'Deleted'");
            decoderMap.put( DecoderType.ADV_PLACE_FULL          , advPlaceFull);*/
        }
        decoderBundle.setDecoderMap(decoderMap);
        decoderBundle.afterPropertiesSet();

        DecoderBundle idDecoderBundle = new DecoderBundle();
        idDecoderBundle.setCheckDecoderMapCompleteness(false);
        Map<DecoderType, LocaleDecoder> idDecoderMap = new EnumMap<>(DecoderType.class);
        if(template!=null) {
            /*    <bean id="tsIdDecoder" class="ru.yandex.metrika.locale.NotALocaleDecoder">
        <property name="template" ref="countersTemplate"/>
        <property name="tableName" value="TraficSources"/>
        <property name="descriptionColumnName" value="StrId"/>
        <property name="useIdIfNameNull" value="true"/>
    </bean>
*/
            LocaleDecoder ts = getSimpleDecoder(template, localeDictionaries, "TraficSources", "StrId");
            idDecoderMap.put( DecoderType.TRAFFIC_SOURCE      , ts);
            LocaleDecoder adv       = getNotALocaleDecoder(template, "AdvEngines2"  , "StrId");
            idDecoderMap.put( DecoderType.ADV_ENGINE          , adv);
            LocaleDecoder advPlace  = getNotALocaleDecoder(template, "AdvPlaces", "AdvPlaceID", "StrId");
            idDecoderMap.put( DecoderType.ADV_PLACE          , advPlace);
            LocaleDecoder advPlaceFull = getNotALocaleDecoder(template, "Place"  , "PlaceID", "PlaceID", "Options != 'Deleted'");
            idDecoderMap.put( DecoderType.ADV_PLACE_FULL          , advPlaceFull);

            LocaleDecoder se        = getNotALocaleDecoder(template, "SearchEngines", "StrId");
            idDecoderMap.put( DecoderType.SEARCH_ENGINE       , se);
            LocaleDecoder seRoot    = getNotALocaleDecoder(template, "SearchEngines", "Id", "StrId", "ParentId IS NULL");
            idDecoderMap.put( DecoderType.SEARCH_ENGINE_ROOT  , seRoot);
            LocaleDecoder sn        = getNotALocaleDecoder(template, "SocialNetworks", "StrId");
            idDecoderMap.put( DecoderType.SOCIAL_NETWORK       , sn);
            LocaleDecoder intr      = getNotALocaleDecoder(template, "Interests", "StrId");
            idDecoderMap.put( DecoderType.INTERESTS      , intr);
            LocaleDecoder brE      = getSimpleDecoder(template, localeDictionaries, "BrowserEngines", "Name");
            idDecoderMap.put( DecoderType.BROWSER_ENGINE      , brE);
            /*
                <bean id="browserEngineDecoder"  class="ru.yandex.metrika.locale.LocaleDecoderSimple">
        <property name="template" ref="countersTemplate"/>
        <property name="tableName" value="BrowserEngines"/>
        <property name="descriptionColumnName" value="Name"/>
        <property name="localeDictionaries" ref="localeDictionaries"/>
    </bean>

            NotALocaleDecoder seUrl = getNotALocaleDecoder(template, "SearchEngines", "CONCAT(URL, '?', field_name, '=')");
            idDecoderMap.put( DecoderType.SEARCH_PHRASE_URL  , seUrl);
*/
        }
        idDecoderBundle.setDecoderMap(idDecoderMap);
        idDecoderBundle.afterPropertiesSet();

        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setIdDecoderBundle(idDecoderBundle);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        visitProvidersBundle.afterPropertiesSet();
        GAProvidersBundle gaProvidersBundle = new GAProvidersBundle();
        gaProvidersBundle.setAttributeParams(attributeParams);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.afterPropertiesSet();

        apiUtils.setBundleFactory(new CommonBundleFactory(tableSchema, documentationSource, visitProvidersBundle, gaProvidersBundle));
        apiUtils.setTableSchema(tableSchema);
        apiUtils.setDocumentationSource(documentationSource);
        apiUtils.setConfig(new ApiUtilsConfig());
        apiUtils.setProvidersBundle(visitProvidersBundle);
        apiUtils.afterPropertiesSet();
        return apiUtils;
    }

    @NotNull
    public static NotALocaleDecoder getNotALocaleDecoder(MySqlJdbcTemplate template, String tableName, String idCol, String descriptionColumnName, String where) {
        NotALocaleDecoder res    = new NotALocaleDecoder();
        res.setTemplate(template);
        res.setTableName(tableName);
        res.setIdColumnName(idCol);
        res.setDescriptionColumnName(descriptionColumnName);
        res.setInsertNull(true);
        res.setUseIdIfNameNull(true);
        if(where!=null) {
            res.setWhereString(where);
        }
        try {
            res.afterPropertiesSet();
        } catch (Exception e){
            throw Throwables.propagate(e);
        }
        return res;
    }
    @NotNull
    public static NotALocaleDecoder getNotALocaleDecoder(MySqlJdbcTemplate template, String tableName, String idCol, String descriptionColumnName) {
        return getNotALocaleDecoder(template, tableName, idCol, descriptionColumnName, null);
    }

        @NotNull
    public static NotALocaleDecoder getNotALocaleDecoder(MySqlJdbcTemplate template, String tableName, String descriptionColumnName) {
            return getNotALocaleDecoder(template, tableName, "Id", descriptionColumnName);
    }

    private static LocaleDecoder getSimpleDecoder(MySqlJdbcTemplate template, LocaleDictionaries dictionaries, String table, String column, String where) throws Exception {
        return getSimpleDecoder(template, dictionaries, table, "Id", column, where);
    }

    private static LocaleDecoder getSimpleDecoder(MySqlJdbcTemplate template, LocaleDictionaries dictionaries, String table, String idColumn, String column, String where) throws Exception {
        LocaleDecoderSimple ld;
        ld = new LocaleDecoderSimple();
        ld.setTableName(table);
        ld.setIdColumnName(idColumn);
        ld.setDescriptionColumnName(column);
        if (!StringUtil.isEmpty(where)) ld.setWhereString(where);
        ld.setTemplate(template);
        ld.setLocaleDictionaries(dictionaries);
        ld.afterPropertiesSet();
        return ld;
    }

    private static LocaleDecoder getSimpleDecoder(MySqlJdbcTemplate template, LocaleDictionaries dictionaries, String table, String column) throws Exception {
        return getSimpleDecoder(template, dictionaries, table, column, null);
    }

    @Test
    public void testWrap() {
        String arg = " (ym:s:goal22994835IsReached=='Yes') and (ym:s:goal22994840IsReached=='No' and ym:s:goal22994640IsReached=='No' and ym:s:goal22994845IsReached=='No' and ym:s:goal23178510IsReached=='No' and ym:s:goal22994865IsReached=='No')";
        FBFilter fbFilter = pp.buildSimpleAST(arg);
        FBFilter wrap = FBFilterTransformers.wrapForTable(fbFilter, new TableEntity(TableSchemaSite.VISITS));
        System.out.println("wrap = " + wrap);
    }

    @Test
    public void testWrap2() {
        var s = "ym:s:age>10 and ym:s:adfoxSiteID==20 and ym:s:adfoxPuidKey==30";
        FBFilter fbFilter = pp.buildSimpleAST(s);
        FBFilter wrap = FBFilterTransformers.wrapForTuples(fbFilter, QueryEntity.fromTargetTuples(Set.of(ADFOX_TUPLE, ADFOX_PUID_TUPLE)));
        System.out.println("fbFilter = " + wrap);

        QueryContext queryContext = QueryContext.defaultFields().targetTable(TableSchemaSite.VISITS).lang("en").apiUtils(apiUtils).build();
        FilterParserBraces2.FBTranslator translator = new FilterParserBraces2.FBTranslator(
                queryContext, queryContext.getCrossTableRelations(), queryContext.getApiUtils().getSelectPartParser());
        Filter filter = wrap.visit(translator);
        Condition condition = filter.buildExpression(queryContext);
        System.out.println("sql code = " + PrintQuery.print(condition));
        /*
        fbFilter = ((ym:s:age > '10')) AND (EXISTS ((ym:s:adfoxSiteID == '20') AND EXISTS (ym:s:adfoxPuidKey == '30')))
        sql code = roundAge(Age) > 10 AND arrayExists(x_0,x_1 -> x_1 = toUInt64(20) AND arrayExists(x_0 -> x_0 = 30,x_0),`Adfox.PuidKey`,`Adfox.SiteID`)
         */
    }

}
