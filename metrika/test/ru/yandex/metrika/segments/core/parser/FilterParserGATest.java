package ru.yandex.metrika.segments.core.parser;

import java.util.Optional;

import com.google.common.collect.Lists;
import org.apache.commons.lang3.tuple.Pair;
import org.jetbrains.annotations.NotNull;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.filter.FilterParserBraces2Test;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;

import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */

public class FilterParserGATest {
    FilterParserGA parser;
    TestAttributeBundle bundle = new TestAttributeBundle();
    private QueryParserImplTest queryParserTest;
    TestTableSchema tableSchema = new TestTableSchema();

    private @NotNull ApiUtils apiUtils;
    QueryContext context;
    QueryContext contextTest;
    QueryContext contextT;

    @Before
    public void setUp() throws Exception {
        apiUtils = FilterParserBraces2Test.getApiUtils();
        queryParserTest = new QueryParserImplTest();
        queryParserTest.setUp();
        QueryParser qp = queryParserTest.queryParserFactory.createParser(queryParserTest.builder().build());
        qp.parse();
        parser = (FilterParserGA)(((QueryParserImpl)qp).getFilterParserGA());

        context = QueryContext.defaultFields()
                .apiUtils(apiUtils)
                .targetTable(TestTableSchema.VISITS)
                .tableSchema(tableSchema)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .useDimensionNotNullFilters(false)
                .excludeInsignificant(false)
                .build();
        contextTest = QueryContext.newBuilder(context).targetTable(TestTableSchema.TEST).build();
        contextT = QueryContext.newBuilder(context).targetTable(TestTableSchema.T).build();
    }

    @Test
    @Ignore("METRIQA-936")
    public void testParse() throws Exception {
        String testString = ",q1;q2;;q\\3,,,q4\\;;q5;";
        parser.split(testString);
        assertEquals(Lists.newArrayList("q1", "q2", "q\\3", "q4\\;", "q5"), parser.getSplittedFilters());
        assertEquals(Lists.newArrayList(
                new FilterParserGA.Separator(Compound.Type.AND, 1),
                new FilterParserGA.Separator(Compound.Type.AND, 2),
                new FilterParserGA.Separator(Compound.Type.OR,  3),
                new FilterParserGA.Separator(Compound.Type.AND, 1)
        ), parser.getSeparators());

    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterParse() throws Exception {
        String filter = "t:a>0";
        FilterParseResult fpr = parser.parseFilters(filter, contextT);
        Pair<Optional<Filter>,Optional<Filter>> filterFilterPair = fpr.asPair();
        assertEquals(Optional.empty(), filterFilterPair.getRight());
        assertEquals(
                SelectPartFilter.singleValue(bundle.a, Relation.GT, "0"),
                filterFilterPair.getLeft().get());

    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterParse2() throws Exception {
        //((0 and 1) or 2) and (((3 and 7) or 4) and 5 and 6)
        String filter = "t:a>0;;t:a>1,t:a>2;t:a>3;;;;;t:a>7,,t:a>4;;t:a>5;;t:a>6";
        FilterParseResult fpr = parser.parseFilters(filter, contextT);
        Pair<Optional<Filter>,Optional<Filter>> filterFilterPair = fpr.asPair();
        assertEquals(Optional.empty(), filterFilterPair.getRight());
        assertEquals(Optional.of(
                new Compound(
                        Compound.Type.AND,
                        new Compound(Compound.Type.OR,
                                new Compound(Compound.Type.AND, f(0), f(1)),
                                f(2)
                        ),
                        new Compound(Compound.Type.OR,
                                new Compound(Compound.Type.AND, f(3), f(7)),
                                f(4)
                        ),
                        f(5), f(6)
                )),

                filterFilterPair.getLeft());

    }

    @Test
    @Ignore("METRIQA-936")
    public void testFilterParse3() throws Exception {
        String filter = "t:a>0,t:a>1";
        FilterParseResult fpr = parser.parseFilters(filter, contextT);
        Pair<Optional<Filter>,Optional<Filter>> filterFilterPair = fpr.asPair();
        assertEquals(Optional.empty(), filterFilterPair.getRight());
        assertEquals(Optional.of(
                new Compound(Compound.Type.OR, f(0), f(1))),
                filterFilterPair.getLeft());

    }

    Filter f(int i) {
        return SelectPartFilter.singleValue(bundle.a, Relation.GT, String.valueOf(i));
    }
}
