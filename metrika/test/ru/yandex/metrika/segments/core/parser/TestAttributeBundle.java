package ru.yandex.metrika.segments.core.parser;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import org.junit.Ignore;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.SpecialAttributes;
import ru.yandex.metrika.segments.core.doc.AttributeDocumentation;
import ru.yandex.metrika.segments.core.parser.filter.FBLeafFilter;
import ru.yandex.metrika.segments.core.parser.metric.ParamAttributeMetricFactory;
import ru.yandex.metrika.segments.core.query.metric.Metric;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.schema.CrossTableRelations;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.type.Types;
import ru.yandex.metrika.util.collections.MapBuilder;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.AVG;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.NORM;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PERCENT;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_DAY;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_DEKAMINUTE;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_HOUR;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_MINUTE;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_WEEK;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.SUM;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.UNIQ;

/**
 * Created by orantius on 9/28/15.
 */
@Ignore
public class TestAttributeBundle implements AttributeBundle {

    Set<AbstractAttribute> testAttributes;
    Attribute idString;
    Attribute dateDimension;
    Attribute feijoaCount;
    Attribute a;
    Attribute bHits;
    Attribute bVisits;
    Attribute restricted;
    Attribute restrictedInternal;
    Attribute uniqStrings;

    Attribute stringFromHits;
    Attribute stringFromExternals;
    Attribute withAdditional;
    AttributeParamTest params;
    ParamAttributeParserImpl фейхоаРазмером;
    ParamAttributeParserImpl фейхоаЦветаАлиась;
    final ParamAttributeParser paramAttributeParser2;
    final ParamAttributeParser paramAttributeParser3;
    final ArrayList<MetricInternalMeta> metas;

    TestTableSchema tableSchema = new TestTableSchema();

    public TestAttributeBundle() {
        testAttributes = new HashSet<>();
        params = new AttributeParamTest();

        idString = new Attribute("IdString", "test:", Types.getStringType("NULL").withNoAggregates(), TestTableSchema.TEST2, params);
        idString.setTemplate(ClickHouse.s("ids"));
        feijoaCount = new Attribute("КоличествоФейхоа", "test:", Types.INT.withAggregateSet(Sets.newHashSet(AVG,
                                    PERCENT, SUM, PER_WEEK, PER_DAY, PER_HOUR, PER_DEKAMINUTE, PER_MINUTE, NORM, UNIQ)), TestTableSchema.TEST2, params);
        feijoaCount.setTemplate(ClickHouse.n64("2"));
        dateDimension = new Attribute("Date", "test:", Types.DATE_DASH, TestTableSchema.TEST2, params);
        dateDimension.setTemplate(ClickHouse.d("2008-01-01"));
        uniqStrings = new Attribute("UniqString", "test:", Types.STRING, TestTableSchema.TEST2, params);
        uniqStrings.setTemplate(ClickHouse.s("uni"));

        stringFromHits = new Attribute("StringFromHits", "test:", Types.STRING, TestTableSchema.TEST2, params);
        stringFromHits.setTemplate(ClickHouse.s("uni"));
        stringFromExternals = new Attribute("StringFromExternals", "test:", Types.STRING, TestTableSchema.TEST2, params);
        stringFromExternals.setTemplate(ClickHouse.s("uni"));

        withAdditional = new Attribute("WithAdditional", "test:", Types.INT, TestTableSchema.TEST2, params);
        withAdditional.withNotNullFilterFB(Optional.of(new FBLeafFilter(feijoaCount, Relation.GE, "10")));
        withAdditional.setTemplate(ClickHouse.n64("3"));

        a = new Attribute("a", "t:", Types.INT, TestTableSchema.T, params);
        a.setWithTypeNullValue(true);
        a.setDocumentation(new AttributeDocumentation("TestAttribute"));
        a.setTemplate(ClickHouse.n64("4"));

        restricted = new Attribute("Restricted", "t:", Types.INT, TestTableSchema.T, params);
        restricted.restrictPrivate();
        restricted.setTemplate(ClickHouse.n64("5"));

        restrictedInternal = new Attribute("RestrictedInternal", "t:", Types.INT, TestTableSchema.T, params);
        restrictedInternal.restrictInternal();
        restrictedInternal.setTemplate(ClickHouse.n64("6"));

        bHits   = new Attribute("b", "t:", Types.INT, TestTableSchema.T, params);
        bHits.setTemplate(ClickHouse.n64("7"));
        bVisits = new Attribute("b", "t:", Types.INT, TestTableSchema.T, params);
        bVisits.setTemplate(ClickHouse.n64("8"));


        Attribute watchIds = new Attribute("WatchIDs", "ym:s:", Types.INT_ID, TestTableSchema.VISITS, params);
        watchIds.setTemplate(ClickHouse.n64("9"));
        Attribute watchId = new Attribute("WatchID", "ym:pv:", Types.INT_ID, TestTableSchema.HITS, params);
        watchId.setTemplate(ClickHouse.n64("10"));

        Attribute sEventID = new Attribute("EventID", "ym:s:", Types.INT, TestTableSchema.TEST, params);
        sEventID.setTemplate(ClickHouse.n64("11"));
        Attribute testEventID = new Attribute("EventID", "test:", Types.INT, TestTableSchema.TEST2, params);
        testEventID.setTemplate(ClickHouse.n64("12"));


        testAttributes.addAll(Lists.newArrayList(
                sEventID,
                testEventID,
        idString,
        feijoaCount,
        dateDimension,
        uniqStrings,
        stringFromHits,
        stringFromExternals,
        withAdditional,
        a,
        restricted,
        restrictedInternal,
        bHits,
        bVisits,
        watchId,
        watchIds
        ));

        Supplier<CrossTableRelations> ctrs = () -> tableSchema.buildRelations(testAttributes,Collections.emptyMap());



        фейхоаРазмером = new ParamAttributeParserImpl("test:", "фейхоа<quantile>Размером", Types.INT, TestTableSchema.TEST2, params, null);
        фейхоаРазмером.getPrototype().restrictInternal();

        фейхоаЦветаАлиась = new ParamAttributeParserImpl("test:", "фейхоаЦветаАлиась<currency>", Types.INT, TestTableSchema.TEST2, params, null);
        paramAttributeParser2 = new ParamAttributeParserImpl("test:", "фейхоаЦвета<currency>", Types.STRING, TestTableSchema.TEST2, params, null);

        paramAttributeParser3 = new ParamAttributeParserImpl("test:", "<attribution>АттрибуцияФейхоа", Types.INT, TestTableSchema.TEST2, params, null);

        metas = Lists.newArrayList(
                new MetricInternalMeta("t:", TestTableSchema.T, "tCount", a.getMetricFactory(SUM)),
                new MetricInternalMeta("test:", TestTableSchema.TEST, "eventCount", sEventID.getMetricFactory(SUM)),
                new MetricInternalMeta("test:", TestTableSchema.TEST2, "testCount", testEventID.getMetricFactory(SUM)),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "ttCount", a.getMetricFactory(SUM)),

                new MetricInternalMeta("tt:", TestTableSchema.TT, "avgAAlias", a.getMetricFactory(AVG)),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "sumAAlias", a.getMetricFactory(SUM)),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "uniqStringAlias", uniqStrings.getMetricFactory(UNIQ)),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "сумФейхоаРазмером<quantile>Алиась", фейхоаРазмером.buildMetricFactory(SUM)),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "авэгэФейхоаЦветаАлиась<currency>", new ParamAttributeMetricFactory(фейхоаЦветаАлиась, AVG, Optional.empty()) {
                    @Override
                    public Metric build(ParameterMap parameterMap) {
                        assertEquals("Рыжего", parameterMap.get(params.getColorMeta()));
                        return super.build(parameterMap);
                    }
                }),
                new MetricInternalMeta("tt:", TestTableSchema.TT, "авэгэФейхоаЦвета<currency>Алиась<quantile>", new ParamAttributeMetricFactory(фейхоаРазмером, SUM, Optional.empty()) {
                    @Override
                    public Metric build(ParameterMap parameterMap) {
                        assertEquals("95", parameterMap.get(params.getQuantileParam()));
                        assertEquals("Синеватого", parameterMap.get(params.getColorMeta()));
                        return super.build(parameterMap);
                    }
                })
        );

    }


    @Override
    public Set<AbstractAttribute> getAttributes() {
        return testAttributes;
    }

    @Override
    public Map<String, AbstractAttribute> getByApiName() {
        return testAttributes.stream().collect(Collectors.toMap(a->a.toApiName(),a->a));
    }

    @Override
    public Map<String, ParamAttributeParser> getParamAttributeParsers() {
        return Lists.newArrayList(фейхоаРазмером, paramAttributeParser2, paramAttributeParser3).stream()
                .collect(Collectors.toMap(pap->pap.getIdWithNamespace(), pap->pap));
    }

    @Override
    public Set<MetricInternalMeta> getMetrics() {
        return new HashSet<>(metas);
    }

    @Override
    public void postInit() {

    }

    @Override
    public Set<TableMeta> getTableMetaSet() {
        return getSpecialInfo().keySet();
    }

    @Override
    public Map<TableMeta, SpecialAttributes> getSpecialInfo() {
        return MapBuilder.<TableMeta, SpecialAttributes>builder()
                .put(TestTableSchema.TEST, new SpecialAttributes(TestTableSchema.TEST).count("eventCount"))
                .put(TestTableSchema.T, new SpecialAttributes(TestTableSchema.T).count("tCount"))
                .put(TestTableSchema.TT, new SpecialAttributes(TestTableSchema.TT).count("ttCount"))
                .put(TestTableSchema.TEST2, new SpecialAttributes(TestTableSchema.TEST2).count("testCount"))
                .build();
    }
}
