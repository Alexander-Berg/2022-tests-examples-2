package ru.yandex.metrika.segments.core.query.rewrite;

import java.util.Optional;
import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.segments.core.parser.AbstractTest;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.FilterTransformers;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterValues;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.instanceOf;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.test.matchers.MoreMatchers.isPresent;

public class QueryRewriterTest2 extends AbstractTest {

    @Test
    public void testSelfFilteringRewriteFilterEq() {
        var filter = SelectPartFilterValues.intValue(bundle.intAttr.cloneIt(), Relation.EQ, 7);

        var queryContext = contextBuilder().build();
        var rewritten = apiUtils.getQueryRewriter().rewriteFilter(Optional.of(filter), queryContext).orElseThrow();

        assertThat(rewritten, instanceOf(SelectPartFilterValues.class));
        assertThat(rewritten, equalTo(filter));

        var selectPart = ((SelectPartFilterValues) rewritten).getSelectPart();
        assertThat(selectPart, instanceOf(Attribute.class));

        var nnfO  = ((Attribute) selectPart).getDimensionNotNullFilter();
        assertThat(nnfO, isPresent());

        var nnf = nnfO.orElseThrow();
        var flatten = FilterTransformers.flattenCompound(nnf);
        assertThat(flatten, instanceOf(Compound.class));

        var children = ((Compound) flatten).getChildren();
        assertThat(children, hasSize(3));
        assertThat(children, containsInAnyOrder(
                SelectPartFilter.intValue(bundle.intAttr, Relation.GT, 5),
                SelectPartFilter.intValue(bundle.intAttr, Relation.LT, 10),
                SelectPartFilter.nullValue(bundle.intAttr, Relation.IS_NOT_NULL)
        ));
    }

    @Test
    public void testSelfFilteringRewriteFilterLt() {
        var filter = SelectPartFilter.intValue(bundle.intAttr.cloneIt(), Relation.LT, 7);

        var queryContext = contextBuilder().build();
        var rewritten = apiUtils.getQueryRewriter().rewriteFilter(Optional.of(filter), queryContext).orElseThrow();

        var flatten = FilterTransformers.flattenCompound(rewritten);
        assertThat(flatten, instanceOf(Compound.class));

        // тут нужен Set потому что мы 2 раза пишем < 5, но это +- ожидаемо
        var children = Set.copyOf(((Compound) flatten).getChildren());
        assertThat(children, hasSize(4));
        assertThat(children, containsInAnyOrder(
                SelectPartFilter.intValue(bundle.intAttr, Relation.GT, 5),
                SelectPartFilter.intValue(bundle.intAttr, Relation.LT, 10),
                SelectPartFilter.intValue(bundle.intAttr, Relation.LT, 7),
                SelectPartFilter.nullValue(bundle.intAttr, Relation.IS_NOT_NULL)
        ));


        var selectPart = children.stream()
                .map(SelectPartFilter.class::cast)
                .map(SelectPartFilter::getSelectPart)
                .filter(bundle.intAttr::equals)
                .findAny()
                .orElseThrow();
        assertThat(selectPart, instanceOf(Attribute.class));

        var nnfO  = ((Attribute) selectPart).getDimensionNotNullFilter();
        assertThat(nnfO, isPresent());

        var nnf = nnfO.orElseThrow();
        var flattenNNF = FilterTransformers.flattenCompound(nnf);
        assertThat(flatten, instanceOf(Compound.class));

        var childrenNNF = ((Compound) flattenNNF).getChildren();
        assertThat(childrenNNF, hasSize(3));
        assertThat(childrenNNF, containsInAnyOrder(
                SelectPartFilter.intValue(bundle.intAttr, Relation.GT, 5),
                SelectPartFilter.intValue(bundle.intAttr, Relation.LT, 10),
                SelectPartFilter.nullValue(bundle.intAttr, Relation.IS_NOT_NULL)
        ));
    }

    @Test
    public void testMetr46485Case() {
        var filter = SelectPartFilter.intValue(bundle.longAttr.cloneIt(), Relation.LT, 42);

        var queryContext = contextBuilder().build();
        var rewritten = apiUtils.getQueryRewriter().rewriteFilter(Optional.of(filter), queryContext).orElseThrow();

        var flatten = FilterTransformers.flattenCompound(rewritten);
        assertThat(flatten, instanceOf(Compound.class));

        var children = ((Compound) flatten).getChildren();
        assertThat(children, hasSize(3));
        assertThat(children, containsInAnyOrder(
                SelectPartFilter.intValue(bundle.longAttr, Relation.LT, 42),
                SelectPartFilter.nullValue(bundle.longAttr, Relation.IS_NOT_NULL),
                SelectPartFilter.nullValue(bundle.dateAttr, Relation.IS_NOT_NULL)
        ));


        var selectPart = children.stream()
                .map(SelectPartFilter.class::cast)
                .map(SelectPartFilter::getSelectPart)
                .filter(bundle.longAttr::equals)
                .findAny()
                .orElseThrow();
        assertThat(selectPart, instanceOf(Attribute.class));

        var nnfO  = ((Attribute) selectPart).getDimensionNotNullFilter();
        assertThat(nnfO, isPresent());

        var nnf = nnfO.orElseThrow();
        var flattenNNF = FilterTransformers.flattenCompound(nnf);
        assertThat(flatten, instanceOf(Compound.class));

        var childrenNNF = ((Compound) flattenNNF).getChildren();
        assertThat(childrenNNF, hasSize(2));
        assertThat(childrenNNF, containsInAnyOrder(
                SelectPartFilter.nullValue(bundle.longAttr, Relation.IS_NOT_NULL),
                SelectPartFilter.nullValue(bundle.dateAttr, Relation.IS_NOT_NULL)
        ));
    }
}
