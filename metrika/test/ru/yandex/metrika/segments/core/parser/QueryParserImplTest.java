package ru.yandex.metrika.segments.core.parser;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import com.google.common.collect.Lists;
import org.apache.logging.log4j.Level;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.core.ApiErrors;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.bundles.UnionBundle;
import ru.yandex.metrika.segments.core.meta.MetricMeta;
import ru.yandex.metrika.segments.core.parser.filter.FBFilter;
import ru.yandex.metrika.segments.core.parser.filter.FBLeafFilter;
import ru.yandex.metrika.segments.core.parser.metric.ParamAttributeMetricFactory;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.SortPart;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.metric.AggregateMetric;
import ru.yandex.metrika.segments.core.query.metric.Metric;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamMeta;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.AttributeNameImpl;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.query.rewrite.QueryRewriter;
import ru.yandex.metrika.segments.core.schema.CrossTableRelations;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.segments.core.type.Types;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.collections.FunctionalHacks;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.AVG;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.SUM;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.UNIQ;

/**
 * todo теперь тут можно создать тестовую схему со своими тестовыми таблицами, и привязывать атрибуты к ним.
 * @author jkee
 */

public class QueryParserImplTest {

    QueryParserFactory queryParserFactory;
    private QueryRewriter queryRewriter = QueryRewriter.buildRewriter();
    @Rule
    public ExpectedException exception = ExpectedException.none();
    private AttributeParamTest params;

    TestAttributeBundle bundle = new TestAttributeBundle();
    public ApiUtils apiUtils;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        TestTableSchema tableSchema = new TestTableSchema();
        CrossTableRelations ctrs = tableSchema.buildRelations(bundle.getAttributes(), bundle.getParamAttributeParsers());
        params = new AttributeParamTest();
        apiUtils = new ApiUtils();
        SimpleProvidersBundle providersBundle = new SimpleProvidersBundle();
        providersBundle.setRequiredFilterBuilder(ctx -> Optional.empty());
        apiUtils.setProvidersBundle(providersBundle);
        apiUtils.setTableSchema(tableSchema);
        apiUtils.setAttributeParams(params);
        apiUtils.setBundleFactory(()->new UnionBundle(Collections.singletonList(bundle)));
        apiUtils.setDocumentationSource(new DocumentationSourceEmpty());
        apiUtils.afterPropertiesSet();

        queryParserFactory = apiUtils.getParserFactory();
        queryParserFactory.setAppendNonZeroRowsFilter(false);
    }

    // :::::::::::: Проверка парсинга start-date, end-date
    @Test
    public void testWrongDate() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_START_END_DATE, "2012-01-51"));
        QueryParams queryParams = builder()
                .startDate("2012-01-51")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        List<AbstractAttribute> attributeList = query.getDimensions();
        assertEquals(Lists.newArrayList(bundle.idString, bundle.dateDimension), attributeList);
    }

    // :::::::::::: Проверка парсинга ключей
    @Test
    @Ignore("METRIQA-936")
    public void testDimensionList0() throws Exception {
        QueryParams queryParams = builder()
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Collections.<Attribute>emptyList(), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testDimensionList1() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:idString")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.idString), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testDimensionList2() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:idString,test:date")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.idString, bundle.dateDimension), query.getDimensions());
    }

    @Test
    public void testDimensionList8() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_TOO_MANY_KEYS, null));
        QueryParams queryParams = builder()
                .dimensions(StringUtil.repeat("test:idString", ',', 12))
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.idString, bundle.dateDimension), query.getDimensions());
    }

    @Test
    public void testWrongAttribute() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_ATTRIBUTE, "test:alala"));
        QueryParams queryParams = builder()
                .dimensions("test:idString,test:alala")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        List<AbstractAttribute> attributeList = query.getDimensions();
        assertEquals(Lists.newArrayList(bundle.idString, bundle.dateDimension), attributeList);
    }

    // :::::::::::: Парсинг метрик
    @Test
    public void testMetricList0() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_NO_METRICS, null));
        QueryParams queryParams = builder()
                .metrics("")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Collections.<Attribute>emptyList(), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricList1() throws Exception {
        QueryParams queryParams = builder()
                .metrics("test:avgКоличествоФейхоа")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.feijoaCount.getMetric(AVG)), query.getMetrics());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricList2() throws Exception {
        QueryParams queryParams = builder()
                .metrics("test:avgКоличествоФейхоа,test:uniqUniqString")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(
                Lists.newArrayList(bundle.feijoaCount.getMetric(AVG), bundle.uniqStrings.getMetric(UNIQ)),
                query.getMetrics()
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricsList11() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_TOO_MANY_METRICS, null));
        QueryParams queryParams = builder();
        queryParams.metrics(StringUtil.repeat("test:avgКоличествоФейхоа", ',',
                queryParams.getQueryLimits().getMetricsLimit() + 1)).build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.idString, bundle.dateDimension), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testWrongMetric() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_METRIC, "test:qTime99КоличествоФейхоа"));
        QueryParams queryParams = builder()
                .metrics("test:qTime99КоличествоФейхоа")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricWithNotNullFilter() throws Exception {
        QueryParams queryParams = builder()
                .metrics("test:avgКоличествоФейхоа(test:количествоФейхоа>5)")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        AggregateMetric metric = bundle.feijoaCount.getMetric(AVG);
        FBFilter actual = new FBLeafFilter(bundle.feijoaCount, Relation.GT, "5");
        Metric metric1 = metric.withExternalNullFilterFB(Optional.of(actual)).withFilterString("(test:количествоФейхоа>5)");
        assertEquals(Lists.newArrayList(metric1), query.getMetrics());
        assertEquals(((AggregateMetric) query.getMetrics().get(0)).getExternalNotNullFilter().get(),
                actual);
    }

    // :::::::::::: Фильтры
    @Test
    @Ignore("METRIQA-936")
    public void testFilter1() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>=5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterOr() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>=5,test:uniqUniqString<3")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(
                new Compound(
                        Compound.Type.OR,
                        SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5"),
                        SelectPartFilter.singleValue(bundle.uniqStrings.getMetric(UNIQ), Relation.LT, "3")
                )),
                query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterAnd() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>=5;test:uniqUniqString<3")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(
                new Compound(
                        Compound.Type.AND,
                        SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5"),
                        SelectPartFilter.singleValue(bundle.uniqStrings.getMetric(UNIQ), Relation.LT, "3")
                )),
                query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterMDAnd() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>=5;test:idString=@варенье")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterMDOrError() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_METRIC_AND_DIMENSION_FILTER, null));
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>=5,test:idString=@варенье")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testWrongOperation() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_OPERATOR_NOT_SUPPORTED_METRIC, "test:avgКоличествоФейхоа =@"));
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа=@5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testWrongFilter() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_FILTER, "test:avgКоличествоФейхоаВШтуках>5"));
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоаВШтуках>5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testWrongValue() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_VALUE_NOT_SUPPORTED_METRIC, "test:avgКоличествоФейхоа>двинадцать"));
        QueryParams queryParams = builder()
                .filters("test:avgКоличествоФейхоа>двинадцать")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    // :::::::::::: Фильтры - скобки
    @Test
    @Ignore("METRIQA-936")
    public void testFilterBraces1() throws Exception {
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>=5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterBracesOr() throws Exception {
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>=5 or test:uniqUniqString<3")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(
                new Compound(
                        Compound.Type.OR,
                        SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5"),
                        SelectPartFilter.singleValue(bundle.uniqStrings.getMetric(UNIQ), Relation.LT, "3")
                )),
                query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterBracesAnd() throws Exception {
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>=5 and test:uniqUniqString<3")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(
                new Compound(
                        Compound.Type.AND,
                        SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5"),
                        SelectPartFilter.singleValue(bundle.uniqStrings.getMetric(UNIQ), Relation.LT, "3")
                )),
                query.getMetricFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterBracesMDAnd() throws Exception {
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>=5 and test:idString=@'варенье'")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterBracesMDOrError() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_METRIC_AND_DIMENSION_FILTER, null));
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>=5 or test:idString=@'варенье'")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testBracesWrongOperation() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_OPERATOR_NOT_SUPPORTED_METRIC, "test:avgКоличествоФейхоа =@"));
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа=@5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testBracesWrongFilter() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_ATTRIBUTE, "test:avgКоличествоФейхоаВШтуках"));
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоаВШтуках>5")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testBracesWrongValue() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_VALUE_NOT_SUPPORTED_METRIC, "test:avgКоличествоФейхоа>двинадцать"));
        QueryParams queryParams = builder()
                .filtersBraces("test:avgКоличествоФейхоа>'двинадцать'")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.feijoaCount.getMetric(AVG), Relation.GE, "5")), query.getMetricFilters());
        assertEquals(Optional.of(SelectPartFilter.singleValue(bundle.idString, Relation.SUB, "варенье")), query.getDimensionFilters());
    }

    // :::::::::::: Лимит
    @Test
    @Ignore("METRIQA-936")
    public void testLimit() throws Exception {
        QueryParams queryParams = builder()
                .limit(95)
                .offset(10)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(95, query.getLimitOffset().get().getLimit());
        assertEquals(10, query.getLimitOffset().get().getOffset());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testLimitOutOfRange() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_LIMIT_OUT_OF_RANGE, "100001"));
        QueryParams queryParams = builder()
                .limit(100001)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
    }

    // :::::::::::: Сортировки

    @Test
    @Ignore("METRIQA-936")
    public void testSort1() throws Exception {
        QueryParams queryParams = builder()
                .sort("test:avgКоличествоФейхоа")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPart(bundle.feijoaCount.getMetric(AVG), false)), query.getSortParts());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testSort2() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:idString")
                .sort("test:avgКоличествоФейхоа,-test:idString")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(
                new SortPart(bundle.feijoaCount.getMetric(AVG), false),
                new SortPart(bundle.idString, true)
        ), query.getSortParts());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testWrongSort() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_SORT, "+test:avgКоличествоФейхоаВШТуках"));
        QueryParams queryParams = builder()
                .sort("+test:avgКоличествоФейхоаВШТуках")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPart(bundle.feijoaCount.getMetric(AVG), false)), query.getSortParts());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testSortNotInList() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_SORT_KEY_NOT_IN_METRIC_OR_DIM, "-test:idString"));
        QueryParams queryParams = builder()
                .sort("-test:idString")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPart(bundle.feijoaCount.getMetric(AVG), false)), query.getSortParts());
    }

    // :::::::::::: Кросс-фильтры

    @Test
    @Ignore("METRIQA-936")
    public void testCrossDimensionError() throws Exception {
       // exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "test:stringFromHits is incompatible with test:avgКоличествоФейхоа"));
        QueryParams queryParams = builder()
                .dimensions("test:stringFromHits")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPart(bundle.feijoaCount.getMetric(AVG), true),
                new SortPart(bundle.stringFromHits, false)), query.getSortParts());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testCrossDimensionError2() throws Exception { // непонятно почему тут должна быть ошибка.
        //exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "test:stringFromExternals is incompatible with test:avgКоличествоФейхоа"));
        QueryParams queryParams = builder()
                .dimensions("test:stringFromExternals")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPart(bundle.feijoaCount.getMetric(AVG), true) ,new SortPart(bundle.stringFromExternals, false)),
                query.getSortParts());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testCrossTableOracleDecide() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "t:b is incompatible with test:avgКоличествоФейхоа"));
        QueryParams queryParams = builder()
                .metrics("test:avgКоличествоФейхоа")
                .dimensions("t:b")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.feijoaCount.getMetric(AVG)), query.getMetrics());
    }

    @Test
    public void testCrossTableOracleDecide2() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "t:b is incompatible with test:uniqStringFromHits"));
        QueryParams queryParams = builder()
                .metrics("test:uniqStringFromHits")
                .dimensions("t:b")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.stringFromHits.getMetric(UNIQ)), query.getMetrics());
    }

    @Test
    public void testCrossTableOracleDecide3() throws Exception {
        // тест тестирует некорректное поведение, мне больше нравится бросать эксепшн. Но люди не поймут
        QueryParams queryParams = builder()
                .metrics("t:avgB")
                .dimensions("t:b")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.bVisits.getMetric(AVG)), query.getMetrics());
    }

    @Test
    public void testCrossTableOracleDecide4() throws Exception {
        QueryParams queryParams = builder()
                .metrics("t:avgB")
                .dimensions("t:a")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.bVisits.getMetric(AVG)), query.getMetrics());
    }

    @Test
    public void testCrossTableOracleDecide5() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "test:stringFromHits is incompatible with t:avgB"));
        QueryParams queryParams = builder()
                .metrics("t:avgB")
                .dimensions("test:stringFromHits")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(bundle.bHits.getMetric(AVG)), query.getMetrics());
    }
/*
    @Test
    public void testCrossFilterError() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_CROSS_TABLE_QUERY, "test:stringFromExternals"));
        QueryParams queryParams = builder()
                .filters("test:stringFromExternals=~подстрока")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(new SortPartImpl(feijoaCount.getMetric(AVG), false)), query.getSortParts());
    }

    @Test
    public void testCrossFilter() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:stringFromHits=~подстрока")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(new CrossFilter(SelectPartFilter.singleValue(stringFromHits, Relation.RE, "подстрока"), TargetTable.VISITS, TargetTable.HITS), query.getDimensionFilters());
    }

    @Test
    public void testCrossFilterBraces() throws Exception {
        QueryParams queryParams = builder()
                .filtersBraces("test:stringFromHits=~'подстрока'")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(new CrossFilter(SelectPartFilter.singleValue(stringFromHits, Relation.RE, "подстрока"), TargetTable.VISITS, TargetTable.HITS), query.getDimensionFilters());
    }*/

    // :::::::::::: Additional conditions

    @Test
    @Ignore("METRIQA-936")
    public void testAdditionalConditionsNo() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:withAdditional==0")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
        assertEquals(
                Optional.of(SelectPartFilter.singleValue(bundle.withAdditional, Relation.EQ, "0")),
                query.getDimensionFilters()
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testAdditionalConditionsYes() throws Exception {
        QueryParams queryParams = builder()
                .filters("test:withAdditional>=0")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
        assertEquals(Optional.of(
                Compound.and(
                        SelectPartFilter.singleValue(bundle.withAdditional, Relation.GE, "0"),
                        bundle.withAdditional.getNotNullFilter().get()
                )),
                query.getDimensionFilters()
        );
    }

    // :::::::: parametrized attributes

    @Test
    @Ignore("METRIQA-936")
    public void testParamDimension() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:фейхоа50Размером")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(
                new Attribute("test:", Types.INT, TestTableSchema.TEST2, null, new AttributeNameImpl(
                        new AttributeParamMeta("size","размер",qc->"42", null, ".*", v->Collections.singletonMap("size", e -> ClickHouse.s(v))), "фейхоа", "50", "Размером"
                ))), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testParamDimension2() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:фейхоаЦветаБорща")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        Attribute attribute = new Attribute("test:", Types.STRING, TestTableSchema.TEST2, null,
                new AttributeNameImpl(bundle.params.getColorMeta(), "фейхоаЦвета", "Борща", ""));
        assertEquals(Lists.newArrayList(attribute), query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testParamDimension3() throws Exception {
        QueryParams queryParams = builder()
                .dimensions("test:firstАттрибуцияФейхоа")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(Lists.newArrayList(
                new Attribute("test:", Types.INT, TestTableSchema.TEST2, null, new AttributeNameImpl(
                        new AttributeParamMeta("ordinal", "номер",qc->"5",null, ".*", v->Collections.singletonMap("ordinal", e -> ClickHouse.s(v))),"", "first", "АттрибуцияФейхоа"))),
                query.getDimensions());
    }

    @Test
    @Ignore("METRIQA-936")
    public void testParamMetricDim() throws Exception {
        QueryParams queryParams = builder()
                .metrics("test:avgФейхоа50Размером")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        AttributeParamMeta size = params.getSizeMeta();//new AttributeParamMeta("quantile", "цель", null,null, ".*", v->Collections.singletonMap("quantile", e -> ClickHouse.s(v)));
        AttributeParamMeta goal_id = new AttributeParamMeta("goal_id", "цель", null,null, ".*", v->Collections.singletonMap("goal_id", e -> ClickHouse.s(v)));
        Attribute attribute = new Attribute("test:", Types.INT, TestTableSchema.TEST, null,
                new AttributeNameImpl(size,"фейхоа", "50", "Размером"));
        AggregateMetric aggregateMetric = new AggregateMetric(attribute, AVG, Optional.empty());
        aggregateMetric = aggregateMetric.withParameterMap(ParameterMap.of(size, "50"));
        assertEquals(Lists.newArrayList(aggregateMetric),
                query.getMetrics());
        int z = 42;
    }

    // :::::::: restrictions :::::::

    @Test
    public void testRestriction() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_RESTRICTED, "t:restricted"));
        QueryParams queryParams = builder()
                .dimensions("t:restricted")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    public void testRestrictionInternal() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_ATTRIBUTE, "t:restrictedInternal"));
        QueryParams queryParams = builder()
                .dimensions("t:restrictedInternal")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    public void testRestrictionMetric() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_RESTRICTED, "t:uniqRestricted"));
        QueryParams queryParams = builder()
                .metrics("t:uniqRestricted")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    public void testRestrictionInternalMetric() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_METRIC, "t:uniqRestrictedInternal"));
        QueryParams queryParams = builder()
                .metrics("t:uniqRestrictedInternal")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionMetricComposite() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_RESTRICTED, "t:uniqRestricted"));
        QueryParams queryParams = builder()
                .metrics("t:uniqRestricted/t:sumA")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionInternalMetricComposite() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_METRIC, "t:uniqRestrictedInternal/t:sumA"));
        QueryParams queryParams = builder()
                .metrics("t:uniqRestrictedInternal/t:sumA")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionMetricFiltered() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_WRONG_METRIC, "t:sumA(t:a>0)"));
        QueryParams queryParams = builder()
                .metrics("t:sumA(t:a>0)")
                .userType(UserType.OWNER)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    public void testRestrictionMetricFiltered2() throws Exception {
        QueryParams queryParams = builder()
                .metrics("t:sumA(t:a>0)")
                .userType(UserType.MANAGER)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionFilter() throws Exception {
        exception.expect(matcher(ApiErrors.ERR_RESTRICTED, "t:restricted"));
        QueryParams queryParams = builder()
                .filters("t:restricted=='1'")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionInternalFilter() {
        exception.expect(matcher(ApiErrors.ERR_WRONG_FILTER, "t:restrictedInternal=='1'"));
        QueryParams queryParams = builder()
                .filters("t:restrictedInternal=='1'")
                .userType(UserType.ANONYMOUS)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        query = queryRewriter.rewriteQuery(query);
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionParam() {
        exception.expect(matcher(ApiErrors.ERR_WRONG_ATTRIBUTE, "test:фейхоа5Размером"));
        QueryParams queryParams = builder()
                .dimensions("test:фейхоа5Размером")
                .userType(UserType.OWNER)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
    }

    @Test
    @Ignore("METRIQA-936")
    public void testRestrictionParamMetric() {
        exception.expect(matcher(ApiErrors.ERR_WRONG_METRIC, "test:sumФейхоа5Размером"));
        QueryParams queryParams = builder()
                .metrics("test:sumФейхоа5Размером")
                .userType(UserType.OWNER)
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
    }

    QueryParams builder() {
        // дефолты
        return QueryParams.create()
                .counterId(100)
                .startDate("2012-01-01")
                .endDate("2012-01-02")
                .metrics("test:avgКоличествоФейхоа")
                .userType(UserType.MANAGER)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain());
    }

    // :::::::: no group requests :::::

    @Test
    public void testNoGroupRequest() throws Exception {
        final QueryParams params = QueryParams.create()
            .counterId(100)
            .startDate("2014-07-24")
            .endDate("2014-07-24")
            .enableSampling(false)
            .dimensions("t:a")
            .userType(UserType.MANAGER)
            .lang(LocaleLangs.RU)
            .domain(LocaleDomain.getDefaultChDomain())
            .noGroup(true);

        queryParserFactory.createParser(params).parse();

    }


    // :::::::: metric parsers ::::::::

    private List<MetricParser>  initMetricParsers() {
        ArrayList<MetricInternalMeta> metas = Lists.newArrayList(
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "avgAAlias", bundle.a.getMetricFactory(AVG)),
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "sumAAlias", bundle.a.getMetricFactory(SUM)),
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "uniqStringAlias", bundle.uniqStrings.getMetricFactory(UNIQ)),
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "сумФейхоаРазмером<quantile>Алиась", bundle.фейхоаРазмером.buildMetricFactory(SUM)),
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "авэгэФейхоаЦветаАлиась<currency>", new ParamAttributeMetricFactory(bundle.фейхоаЦветаАлиась, AVG, Optional.empty()) {
                    @Override
                    public Metric build(ParameterMap parameterMap) {
                        assertEquals("Рыжего", parameterMap.get(params.getColorMeta()));
                        return super.build(parameterMap);
                    }
                }),
                new MetricInternalMeta("tt:", TestTableSchema.HITS, "авэгэФейхоаЦвета<currency>Алиась<quantile>", new ParamAttributeMetricFactory (bundle.фейхоаРазмером, SUM, Optional.empty()) {
                    @Override
                    public Metric build(ParameterMap parameterMap) {
                        assertEquals("95", parameterMap.get(params.getQuantileParam()));
                        assertEquals("Синеватого", parameterMap.get(params.getColorMeta()));
                        return super.build(parameterMap);
                    }
                })
        );
        return F.map(metas, input -> input.buildParser(params));
    }

    @Test
    public void testMetricParser1() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:avgAAlias,tt:sumAAlias,tt:uniqStringAlias")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(
                Lists.newArrayList(bundle.a, bundle.a, bundle.uniqStrings),
                FunctionalHacks.map(query.getMetrics(), "getAttribute")
        );
        assertEquals(
                Lists.newArrayList(AVG, SUM, UNIQ),
                FunctionalHacks.map(query.getMetrics(), "getAggregate")
        );
        assertEquals(
                Lists.newArrayList("tt:avgAAlias", "tt:sumAAlias", "tt:uniqStringAlias"),
                FunctionalHacks.map(query.getMetricMetas(), "getDim")
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricParser2() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:сумФейхоаРазмером75Алиась,tt:авэгэФейхоаЦветаАлиасьРыжего")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
        assertEquals(
                Lists.newArrayList(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(bundle.фейхоаРазмером.getAttributeParamMeta(),"75"),
                                Optional.empty()),
                        bundle.фейхоаЦветаАлиась.buildAttribute(ParameterMap.of(bundle.фейхоаЦветаАлиась.getAttributeParamMeta(),"Рыжего"),
                                Optional.empty())),
                FunctionalHacks.map(query.getMetrics(), "getAttribute")
        );
        // testing that equality works well
        assertFalse(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(bundle.фейхоаРазмером.getAttributeParamMeta(), "14"),
                Optional.empty()).equals(((AggregateMetric) query.getMetrics().get(0)).getAttribute()));
        assertFalse(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(bundle.фейхоаРазмером.getAttributeParamMeta(), "Рыжеватого"),
                Optional.empty()).equals(((AggregateMetric) query.getMetrics().get(1)).getAttribute()));
        assertEquals(
                Lists.newArrayList(SUM, AVG),
                F.map(query.getMetrics(), m->((AggregateMetric)m).getAggregate())
        );
        assertEquals(
                Lists.newArrayList("tt:сумФейхоаРазмером75Алиась", "tt:авэгэФейхоаЦветаАлиасьРыжего"),
                F.map(query.getMetricMetas(), MetricMeta::getDim)
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricParser3() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:авэгэФейхоаЦветаСиневатогоАлиась95")
                .build();
        Query query = queryParserFactory.createParser(queryParams).parse();
    }

    @Test
    public void testMetricParser1Radix() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:avgAAlias,tt:sumAAlias,tt:uniqStringAlias")
                .build();
        QueryParser parser = queryParserFactory.createParser(queryParams);
        Query query = parser.parse();
        assertEquals(
                Lists.newArrayList(bundle.a, bundle.a, bundle.uniqStrings),
                FunctionalHacks.map(query.getMetrics(), "getAttribute")
        );
        assertEquals(
                Lists.newArrayList(AVG, SUM, UNIQ),
                FunctionalHacks.map(query.getMetrics(), "getAggregate")
        );
        assertEquals(
                Lists.newArrayList("tt:avgAAlias", "tt:sumAAlias", "tt:uniqStringAlias"),
                FunctionalHacks.map(query.getMetricMetas(), "getDim")
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricParser2Radix() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:сумФейхоаРазмером90Алиась,tt:авэгэФейхоаЦветаАлиасьРыжего")
                .build();
        QueryParser parser = queryParserFactory.createParser(queryParams);
        Query query = parser.parse();
        assertEquals(
                Lists.newArrayList(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(params.getQuantileMeta(),"90"),
                                Optional.empty()),
                        bundle.фейхоаЦветаАлиась.buildAttribute(ParameterMap.of(bundle.фейхоаЦветаАлиась.getAttributeParamMeta(), "Рыжего"),
                                Optional.empty())),
                FunctionalHacks.map(query.getMetrics(), "getAttribute")
        );
        // testing that equality works well
        assertFalse(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(bundle.фейхоаРазмером.getAttributeParamMeta(), "14"),
                Optional.empty()).equals(((AggregateMetric) query.getMetrics().get(0)).getAttribute()));
        assertFalse(bundle.фейхоаРазмером.buildAttribute(ParameterMap.of(bundle.фейхоаРазмером.getAttributeParamMeta(), "Рыжеватого"),
                Optional.empty()).equals(((AggregateMetric) query.getMetrics().get(1)).getAttribute()));
        assertEquals(
                Lists.newArrayList(SUM, AVG),
                FunctionalHacks.map(query.getMetrics(), "getAggregate")
        );
        assertEquals(
                Lists.newArrayList("tt:сумФейхоаРазмером90Алиась", "tt:авэгэФейхоаЦветаАлиасьРыжего"),
                FunctionalHacks.map(query.getMetricMetas(), "getDim")
        );
    }

    @Test
    @Ignore("METRIQA-936")
    public void testMetricParser3Radix() throws Exception {
        initMetricParsers();
        QueryParams queryParams = builder()
                .metrics("tt:авэгэФейхоаЦветаСиневатогоАлиась95")
                .build();
        QueryParser parser = queryParserFactory.createParser(queryParams);
        Query query = parser.parse();
    }

    private BaseMatcher<QueryParseException> matcher(final int code, final String text) {
        return new BaseMatcher<QueryParseException>() {
            @Override
            public boolean matches(Object o) {
                if (!(o instanceof QueryParseException)) return false;
                if (((QueryParseException) o).errorCode != code) return false;
                if (text != null) {
                    if (!text.equals (((QueryParseException) o).errorValue)) return false;
                }
                return true;
            }

            @Override
            public void describeTo(Description description) {
            }
        };
    }
}
