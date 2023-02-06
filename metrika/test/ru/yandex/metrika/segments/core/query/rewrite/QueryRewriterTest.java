package ru.yandex.metrika.segments.core.query.rewrite;

import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.google.common.collect.Sets;
import gnu.trove.map.TLongObjectMap;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.segments.core.parser.AttributeParamTest;
import ru.yandex.metrika.segments.core.parser.QueryParserImplTest;
import ru.yandex.metrika.segments.core.query.Query;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.QueryImpl;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.FilterTransformer;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilter;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterNull;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterValues;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParams;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.type.Types;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecoderType;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.EmptyArrays;
import ru.yandex.metrika.util.locale.LocaleAbstractDecoder;
import ru.yandex.metrika.util.locale.LocaleDecoder;
import ru.yandex.metrika.util.locale.LocaleDomain;
import ru.yandex.metrika.util.locale.LocaleLangs;

import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */

public class QueryRewriterTest {

    QueryRewriter queryRewriter;

    //Attribute decodingFeijoa;
    Attribute intWithComparisonConditions;
    Attribute intWithFilterRewrite;

    QueryContext queryContext;
    TableSchemaSite tableSchema = new TableSchemaSite();

    @Rule
    public ExpectedException exception = ExpectedException.none();

    @Before
    public void setUp() throws Exception {
        QueryParserImplTest  qt = new QueryParserImplTest();
        qt.setUp();
        AttributeParams params = new AttributeParamTest();

        final HashMap<String, Map<String, long[]>> langMap = new HashMap<>();
        for (String lang : LocaleLangs.getAvailableLangs()) {
            Map<String, long[]> localMap = new HashMap<>();
            localMap.put("фейхоа3", new long[]{1, 2, 3});
            localMap.put("фейхоа1", new long[]{1});
            localMap.put("фейхоа0", EmptyArrays.LONGS);
            langMap.put(lang, localMap);
        }
        LocaleDecoder decoder = new LocaleAbstractDecoder() {
            @Override
            protected Map<String, Map<String, long[]>> getMap(Object obj) {
                return langMap;
            }

            @Override
            protected Map<String, TLongObjectMap<String>> getEncodeMap(Object obj) {
                return null;
            }
        };

        DecoderBundle decoderBundle = new DecoderBundle();
        Map<DecoderType, LocaleDecoder> decoderMap = new EnumMap<>(DecoderType.class);
        decoderMap.put(DecoderType.TRAFFIC_SOURCE, decoder);
        decoderBundle.setDecoderMap(decoderMap);
        //decodingFeijoa = new Attribute("Фейхоа", "test:",
        //        DecodeTypeConverters.getDecodingStringType(decoderBundle, DecoderType.TRAFFIC_SOURCE), TableSchemaSite.VISITS);
        intWithComparisonConditions = new Attribute("StringCc", "test:", Types.INT, TableSchemaSite.VISITS, params);
        intWithComparisonConditions.withNotNullFilter(Optional.of(SelectPartFilter.singleValue(intWithComparisonConditions, Relation.NE, "-1", true)));
        intWithFilterRewrite = new Attribute("SWFR", "test:", Types.INT, TableSchemaSite.VISITS, params);
        intWithFilterRewrite.setRewriteRule(new FilterContextTransformer() {
            @Override
            public FilterTransformer apply(QueryContext queryContext) {
                return new FilterTransformer() {
                    @Override
                    public Filter visit(SelectPartFilterNull filter) {
                        return filter;
                    }

                    @Override
                    public Filter visit(SelectPartFilterValues src) {
                        if (intWithFilterRewrite.equals(src.getSelectPart()) && src.getRelation() == Relation.EQ) {
                            return src.getValuePart().asValuePart().<Filter>map(vp->{
                                String value = vp.getValue();
                                return new Compound(Compound.Type.AND,
                                        SelectPartFilter.singleValue(intWithFilterRewrite, Relation.GE, value + "10"),
                                        SelectPartFilter.singleValue(intWithFilterRewrite, Relation.LE, value + "20")
                                );
                            }).orElse(src);
                        }
                        return src;
                    }
                };
            }
        });
        queryRewriter = QueryRewriter.buildRewriter();

        queryContext = QueryContext.defaultFields()
                .targetTable(TableSchemaSite.VISITS)
                .tableSchema(tableSchema)
                .lang(LocaleLangs.RU)
                .domain(LocaleDomain.getDefaultChDomain())
                .useDimensionNotNullFilters(false)
                .excludeInsignificant(false)
                .apiUtils(qt.apiUtils)
                .build();
    }
    /*@Test - теперь rewrite в декодировании не участвует
    public void testDecode3() throws Exception {
        Filter dimensionFilter = SelectPartFilter.singleValue(decodingFeijoa, Relation.EQ, "фейхоа3");
        Query query = new Query(queryContext, null, null, dimensionFilter, null, null, null);
        Query rewrited = queryRewriter.rewriteQuery(query);
        assertEquals(SelectPartFilter.singleValue(decodingFeijoa, Relation.IN, "1, 2, 3", false), rewrited.getDimensionFilters());

    }*/


    /*@Test - теперь rewrite в декодировании не участвует
    public void testDecode1() throws Exception {
        Filter dimensionFilter = SelectPartFilter.singleValue(decodingFeijoa, Relation.EQ, "фейхоа1");
        Query query = new Query(queryContext, null, null, dimensionFilter, null, null, null);
        Query rewrited = queryRewriter.rewriteQuery(query);
        assertEquals(SelectPartFilter.singleValue(decodingFeijoa, Relation.EQ, "1"), rewrited.getDimensionFilters());
    } */


    /*@Test - теперь rewrite в декодировании не участвует
    public void testDecode0() throws Exception {
        Filter dimensionFilter = SelectPartFilter.singleValue(decodingFeijoa, Relation.EQ, "фейхоа0");
        Query query = new Query(queryContext, null, null, dimensionFilter, null, null, null);
        Query rewrited = queryRewriter.rewriteQuery(query);
        assertEquals(Filters.NO, rewrited.getDimensionFilters());
    } */

    @Test
    public void testComparisonConditions() throws Exception {
        for (Relation relation : Relation.comparableOnlySet) {
            Filter dimensionFilter = SelectPartFilter.singleValue(intWithComparisonConditions, relation, "10");
            Query query = new QueryImpl(queryContext, queryContext.getTargetMetadata().getTableTemplate(), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), null, Optional.of(dimensionFilter), Optional.empty(), Optional.empty(), Collections.emptyList(), null);
            Query rewrited = queryRewriter.rewriteQuery(query);
            assertEquals(
                    Optional.of(new Compound(
                        Compound.Type.AND,
                        dimensionFilter,
                        SelectPartFilter.singleValue(intWithComparisonConditions, Relation.NE, "-1")
                    )),
                    rewrited.getDimensionFilters()
            );
        }
        Set<Relation> woComparable = Sets.newHashSet(Relation.comparableSet);
        woComparable.removeAll(Relation.comparableOnlySet);
        for (Relation relation : woComparable) {
            Filter dimensionFilter = SelectPartFilter.singleValue(intWithComparisonConditions, relation, "10");
            Query query = new QueryImpl(queryContext, queryContext.getTargetMetadata().getTableTemplate(), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), null, Optional.of(dimensionFilter), Optional.empty(), Optional.empty(), Collections.emptyList(), null);
            Query rewrited = queryRewriter.rewriteQuery(query);
            assertEquals(
                    Optional.of(dimensionFilter),
                    rewrited.getDimensionFilters()
            );
        }
    }

    @Test
    @Ignore("METRIQA-936")
    public void testExternalRewrite() throws Exception {
        for (Relation relation : Relation.comparableSet) {
            Filter dimensionFilter = SelectPartFilter.singleValue(intWithFilterRewrite, relation, "100");
            Query query = new QueryImpl(queryContext, queryContext.getTargetMetadata().getTableTemplate(), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), null, Optional.of(dimensionFilter), Optional.empty(), Optional.empty(), Collections.emptyList(), null);
            Query rewrited = queryRewriter.rewriteQuery(query);
            if (relation == Relation.EQ) {
                assertEquals(Optional.of(new Compound(Compound.Type.AND,
                        SelectPartFilter.singleValue(intWithFilterRewrite, Relation.GE,  "10010"),
                        SelectPartFilter.singleValue(intWithFilterRewrite, Relation.LE,  "10020"))
                ), rewrited.getDimensionFilters());
            } else {
                assertEquals(Optional.of(dimensionFilter), rewrited.getDimensionFilters());
            }
        }

    }

}
