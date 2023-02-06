package ru.yandex.metrika.segments.core.query.filter;

import java.util.Collections;
import java.util.HashMap;
import java.util.Optional;

import org.junit.Test;

import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.QueryImpl;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.schema.AttributeEntity;
import ru.yandex.metrika.segments.core.type.Types;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;

import static org.junit.Assert.assertTrue;

/**
 * Created by orantius on 19.05.16.
 */
public class FilterTransformersTest {

    private final AttributeParamsSite attributeParams = new AttributeParamsSite();
    private final TableSchemaSite tableSchema = new TableSchemaSite();


    @Test
    public void mergeEquivalentTransitions() {

        Attribute eventId = new Attribute("EventID", "ym:s:", Types.UINT, TableSchemaSite.VISITS, attributeParams);
        Attribute eventId2 = new Attribute("EventID", "ym:pv:", Types.UINT, TableSchemaSite.VISITS, attributeParams);

        Attribute url = new Attribute("URL", "ym:pv:", Types.STRING, TableSchemaSite.HITS, attributeParams);

        QueryContext qctx = QueryContext
                .smallContextBuilder(new HashMap<>(), "ru", "ru")
                .startDate("today")
                .endDate("today")
                .targetTable(TableSchemaSite.VISITS)
                .build();

        Filter f = Compound.or(
                new TupleFilter(Quantifier.EXISTS, new AttributeEntity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
                        new SelectPartFilterQuery(eventId, Relation.IN, filter ->
                                new QueryImpl(qctx, null, Collections.singletonList(eventId2),
                                        Collections.emptyList(), Collections.emptyList(), Collections.emptyMap(), Optional.of(filter),
                                        Optional.empty(), Optional.empty(), Collections.emptyList(), Optional.empty()),
                                SelectPartFilter.singleValue(url, Relation.EQ, "url_0"),
                                "exists ym:s:eventID with ")),
                new TupleFilter(Quantifier.EXISTS, new AttributeEntity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
                        new SelectPartFilterQuery(eventId, Relation.IN, filter ->
                                new QueryImpl(qctx, null, Collections.singletonList(eventId2),
                                        Collections.emptyList(), Collections.emptyList(), Collections.emptyMap(), Optional.of(filter),
                                        Optional.empty(), Optional.empty(), Collections.emptyList(), Optional.empty()),
                                SelectPartFilter.singleValue(url, Relation.EQ, "url_1"),
                                "exists ym:s:eventID with ")),
                new TupleFilter(Quantifier.EXISTS, new AttributeEntity(TableSchemaSite.VISITS, TableSchemaSite.EVENTS_TUPLE),
                        new SelectPartFilterQuery(eventId, Relation.IN, filter ->
                                new QueryImpl(qctx, null, Collections.singletonList(eventId2),
                                        Collections.emptyList(), Collections.emptyList(), Collections.emptyMap(), Optional.of(filter),
                                        Optional.empty(), Optional.empty(), Collections.emptyList(), Optional.empty()),
                                SelectPartFilter.singleValue(url, Relation.EQ, "url_2"),
                                "exists ym:s:eventID with "))
        );

        Optional<Filter> filter = FilterTransformers.mergeEquivalentTransitions(Optional.of(f), TableSchemaSite.VISITS, tableSchema);

        // or(tuple(query(==)), tuple(query(==)))
        // VVV
        // tuple(or(query(==), query(==)))
        // VVV
        // tuple(query(or(==, ==)))


        assertTrue(filter.isPresent() && filter.get() instanceof TupleFilter);
        TupleFilter tf = (TupleFilter) filter.get();
        Filter child = tf.getChild();
        // Мы должны схлопнуть фильтры выше в один, потому что можем
        assertTrue(child instanceof SelectPartFilterQuery);
    }

}
