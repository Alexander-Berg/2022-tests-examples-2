package ru.yandex.metrika.segments.core.parser;

import java.util.Map;
import java.util.Optional;

import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.Level;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.springframework.util.StringUtils;

import ru.yandex.metrika.segments.core.ApiErrors;
import ru.yandex.metrika.segments.core.meta.ClickhouseTableMeta;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.filter.CustomFilterBuilder;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.NegatedFilter;
import ru.yandex.metrika.segments.core.query.filter.Quantifier;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.filter.TupleFilter;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.query.rewrite.QueryRewriter;
import ru.yandex.metrika.segments.core.schema.AttributeEntity;
import ru.yandex.metrika.segments.core.schema.CrossTableRelations;
import ru.yandex.metrika.segments.core.schema.Entity;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.schema.TableSchema;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */

public class TransitionTest {


    QueryParserFactory queryParserFactory;
    private QueryRewriter queryRewriter = QueryRewriter.buildRewriter();
    @Rule
    public ExpectedException exception = ExpectedException.none();


    AttributeEntity ppEntity = TestTableSchema.VISITS.toEntity().withTuple(TestTableSchema.PARAMS_TUPLE);
    AttributeEntity evEntity = TestTableSchema.VISITS.toEntity().withTuple(TestTableSchema.EVENTS_TUPLE);
    AttributeEntity testGoalEntity = TestTableSchema.TEST.toEntity().withTuple(TestTableSchema.GOALS_TUPLE);
    AttributeEntity goalEntity = TestTableSchema.VISITS.toEntity().withTuple(TestTableSchema.GOALS_TUPLE);
    Entity visitsEntity = TestTableSchema.VISITS.toEntity();
    Entity hitsEntity = TestTableSchema.HITS.toEntity();
    private TableSchema tableSchema;
    private CrossTableRelations ctrs;
    TrTestAttributeBundle bundle = new TrTestAttributeBundle();

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        QueryParserImplTest qpi = new QueryParserImplTest();
        qpi.setUp();
        tableSchema = new TableSchemaSite();
        ctrs = tableSchema.buildRelations(bundle.getAttributes(), bundle.getParamAttributeParsers());

        Map<TableMeta, ClickhouseTableMeta> tableMetas = tableSchema.loadTableMetadata();
        ClickhouseTableMeta testMeta = new ClickhouseTableMeta();
        tableMetas.put(TestTableSchema.TEST, testMeta);
        queryParserFactory = QueryParserFactory.build(qpi.apiUtils, tableSchema, ctrs);
        queryParserFactory.setAppendNonZeroRowsFilter(false);

    }

    // one-to-many aj foreach types
    @Test
    @Ignore("METRIQA-936")
    public void testO2MAJ() {
        test02MAJ("EXISTS", Quantifier.EXISTS);
        test02MAJ("ALL", Quantifier.FORALL);
        test02MAJ("NONE", Quantifier.NONE);
    }

    private void test02MAJ(String str, Quantifier type) {
        QueryParams queryParams = builder()
                .filtersBraces(str + "(ym:s:VPS=='ololo')")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.visitParamsString, Relation.EQ, "ololo");
        Optional<Filter> dimensionFilters = query.getDimensionFilters();

        if (type == Quantifier.NONE) {
            assertEquals(NegatedFilter.of(new TupleFilter(Quantifier.EXISTS, new AttributeEntity(TestTableSchema.VISITS, TestTableSchema.PARAMS_TUPLE), filter)), dimensionFilters.orElseThrow());
        } else {
            assertEquals(new TupleFilter(type, new AttributeEntity(TestTableSchema.VISITS, TestTableSchema.PARAMS_TUPLE), filter), dimensionFilters.orElseThrow());
        }
    }

    // one-to-many kj foreach types
    @Test
    @Ignore("METRIQA-936")
    public void testO2MKJ() {
        test02MKJ("EXISTS", Quantifier.EXISTS);
        test02MKJ("ALL", Quantifier.FORALL);
        test02MKJ("NONE", Quantifier.NONE);
    }

    private void test02MKJ(String str, Quantifier type) {
        QueryParams queryParams = builder()
                .filtersBraces(str + "(ym:pv:HS=='ololo')")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.hitString, Relation.EQ, "ololo");

        if (type == Quantifier.NONE) {
            assertEquals(NegatedFilter.of(new TupleFilter(Quantifier.EXISTS, new AttributeEntity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
                            CustomFilterBuilder.buildKeyJoinFilter(query.getQueryContext(), TableSchemaSite.HITS.toEntity(), filter, singletonList(bundle.watchIds),
                                    singletonList(bundle.pvEventId), true, false, false, Pair.of(0, 0)))).toString(),
                    query.getDimensionFilters().toString());

        } else {
            assertEquals(new TupleFilter(type, new AttributeEntity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
                            CustomFilterBuilder.buildKeyJoinFilter(query.getQueryContext(), TableSchemaSite.HITS.toEntity(), filter, singletonList(bundle.watchIds),
                                    singletonList(bundle.pvEventId), true, false, false, Pair.of(0, 0))).toString(),
                    query.getDimensionFilters().toString());
        }
    }

    // one-to-one/many-to-one quantifier error
    @Test
    @Ignore("METRIQA-936")
    public void testO2MQError() {
        exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "ym:s:VS=='ololo'"));
        QueryParams queryParams = builder()
                .filtersBraces("EXISTS(ym:s:VS=='ololo')")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        System.out.println(query.getDimensionFilters());
    }

    // one-to-many compatibility mode
    @Test
    @Ignore("METRIQA-936")
    public void test02MCompatibility() {
        test02MCompatibility("==", Relation.EQ, "'ololo'", false);
        test02MCompatibility("!=", Relation.NE, "'ololo'", true);
        test02MCompatibility("!n", Relation.IS_NOT_NULL, "'ololo'", false);
        test02MCompatibility("=n", Relation.IS_NULL, "'ololo'", true);
        test02MCompatibility("==", Relation.EQ, null, true);
        test02MCompatibility("!=", Relation.NE, null, false);
    }

    /**
     * TODO сейчас не инвертируются negative relations.
     */
    private void test02MCompatibility(String relationStr, Relation relation, String value, boolean negated) {
        QueryParams queryParams = builder()
                .filtersBraces("ym:pv:HS" + relationStr + value)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.hitString, negated ? relation.getOpposite() : relation, StringUtils.replace(value, "'", ""));
        //Filter f =new TupleFilter(Quantifier.EXISTS, new Entity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
        Filter f = CustomFilterBuilder.buildKeyJoinFilter(query.getQueryContext(), TestTableSchema.HITS.toEntity(), filter,
                singletonList(bundle.watchIds), singletonList(bundle.pvEventId), true, false, false, Pair.of(0, 0));
        //ToManyTransition(tableSchema, filter, TableSchemaSite.VISITS.toEntity(), filter.collectEntities(), Quantifier.EXISTS, ctrs);
        assertEquals((negated ? NegatedFilter.of(f) : f).toString(), query.getDimensionFilters().toString());
    }

    // many-to-many compatibility mode
    @Test
    @Ignore("METRIQA-936")
    public void testM2MCompatibility() {
        testM2MCompatibility("==", Relation.EQ, "'ololo'", !Relation.EQ.isPositive());
        testM2MCompatibility("!=", Relation.NE, "'ololo'", true);
        testM2MCompatibility("!n", Relation.IS_NOT_NULL, "'ololo'", false);
        testM2MCompatibility("=n", Relation.IS_NULL, "'ololo'", true);
        testM2MCompatibility("!=", Relation.NE, null, false);
        testM2MCompatibility("==", Relation.EQ, null, true);
    }

    // TODO сейчас не инвертируются negative relations.
    private void testM2MCompatibility(String relationStr, Relation relation, String value, boolean negated) {
        QueryParams queryParams = builder()
                .dimensions("ym:s:VPS")
                .filtersBraces("ym:pv:HS" + relationStr + value)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.hitString, negated ? relation.getOpposite() : relation, StringUtils.replace(value, "'", ""));
        Filter f = CustomFilterBuilder.buildKeyJoinFilter(query.getQueryContext(), TestTableSchema.HITS.toEntity(), filter, singletonList(bundle.watchIds),
                singletonList(bundle.pvEventId), true, false, false, Pair.of(0, 0));
        assertEquals((negated ? NegatedFilter.of(f) : f).toString(), query.getDimensionFilters().get().toString());
    }

    // many-to-one
    @Test
    @Ignore("METRIQA-936")
    public void testM2OAJ() {
        QueryParams queryParams = builder()
                .dimensions("ym:s:VPS")
                .filtersBraces("ym:s:VS=='ololo'")

                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.visitString, Relation.EQ, "ololo");
        assertEquals(filter, query.getDimensionFilters().orElseThrow());
    }

    // many-to-many aj - kj
    @Test
    @Ignore("METRIQA-936")
    public void testM2MAJKJ() {
        QueryParams queryParams = builder()
                .dimensions("ym:s:VPS")
                .filtersBraces("EXISTS(ym:pv:HS=='ololo')")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.hitString, Relation.EQ, "ololo");
        Filter kj = CustomFilterBuilder.buildKeyJoinFilter(query.getQueryContext(), TestTableSchema.HITS.toEntity(), filter, singletonList(bundle.watchIds),
                singletonList(bundle.pvEventId), true, false, false, Pair.of(0, 0));
        assertEquals(new TupleFilter(Quantifier.EXISTS, evEntity, kj).toString(),
                query.getDimensionFilters().toString());
        //          ru.yandex.metrika.segments.s2.query.filter.TupleFilter<TupleFilter{type=EXISTS, entity=Entity{targetTable={targetTable='VISITS', namespace='ym:s:'}, targetTuple=Event as Ewv}, child=class ru.yandex.metrika.segments.s2.query.filter.SelectPartFilterQuery{selectPart=Attribute{name='ym:s:eventID', type='TypeImpl{name='INT_ID'}'}, relation=среди}, values='Query{queryContext=QueryContext{Ids=app=[100],counter=[100], startDate='2012-01-01', endDate='2012-01-02', timeZone='null', targetTable={targetTable='HITS', namespace='ym:pv:'}}, dimensions=[Attribute{name='ym:pv:watchID', type='TypeImpl{name='INT_ID'}'}], metrics=[], dimensionFilters=class ru.yandex.metrika.segments.s2.query.filter.SelectPartFilterValues{selectPart=Attribute{name='s:HS', type='TypeImpl{name='STRING'}'}, relation==}, values='[ololo]'}, metricFilters=null, sortParts=[SortPartImpl{selectPart=Attribute{name='ym:pv:watchID', type='TypeImpl{name='INT_ID'}'}, desc=false}], limitOffset=Optional.empty}'}}>
        // but was: ru.yandex.metrika.segments.s2.query.filter.TupleFilter<TupleFilter{type=EXISTS, entity=Entity{targetTable={targetTable='VISITS', namespace='ym:s:'}, targetTuple=Event as Ewv}, child=class ru.yandex.metrika.segments.s2.query.filter.SelectPartFilterQuery{selectPart=Attribute{name='ym:s:eventID', type='TypeImpl{name='INT_ID'}'}, relation=среди}, values='Query{queryContext=QueryContext{Ids=app=[100],counter=[100], startDate='2012-01-01', endDate='2012-01-02', timeZone='null', targetTable={targetTable='HITS', namespace='ym:pv:'}}, dimensions=[Attribute{name='ym:pv:watchID', type='TypeImpl{name='INT_ID'}'}], metrics=[], dimensionFilters=class ru.yandex.metrika.segments.s2.query.filter.SelectPartFilterValues{selectPart=Attribute{name='s:HS', type='TypeImpl{name='STRING'}'}, relation==}, values='[ololo]'}, metricFilters=null, sortParts=[SortPartImpl{selectPart=Attribute{name='ym:pv:watchID', type='TypeImpl{name='INT_ID'}'}, desc=false}], limitOffset=Optional.empty}'}}>

    }

    // many-to-many aj - aj
    @Test
    @Ignore("METRIQA-936")
    public void testM2MAJAJ() {
        QueryParams queryParams = builder()
                .dimensions("ym:s:VPS")
                .filtersBraces("EXISTS(ym:s:GOAL=='ololo')")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        SelectPartFilter filter = SelectPartFilter.singleValue(bundle.goalString, Relation.EQ, "ololo");
        TupleFilter tf = new TupleFilter(Quantifier.EXISTS, goalEntity, filter);
        assertEquals(tf.toString(), query.getDimensionFilters().toString());
    }

    private BaseMatcher<QueryParseException> matcher(final int code, final String text) {
        return new BaseMatcher<>() {
            @Override
            public boolean matches(Object o) {
                if (!(o instanceof QueryParseException)) return false;
                if (((QueryParseException) o).errorCode != code) return false;
                if (text != null) {
                    return text.equals(((QueryParseException) o).errorValue);
                }
                return true;
            }

            @Override
            public void describeTo(Description description) {
            }
        };
    }

    QueryParams builder() {
        // дефолты
        return QueryParams.create()
                .counterId(100)
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .dimensions("ym:s:VS")
                .metrics("ym:s:uniqVS")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain());
    }
}
