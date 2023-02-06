package ru.yandex.metrika.segments.core.parser;

import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.google.common.collect.Sets;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.types.CHType;
import ru.yandex.metrika.segments.core.bundles.AbstractAttributeBundle;
import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.SpecialAttributes;
import ru.yandex.metrika.segments.core.parser.filter.FBLeafFilter;
import ru.yandex.metrika.segments.core.parser.metric.MetricFactory;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.filter.Compound;
import ru.yandex.metrika.segments.core.query.filter.Filter;
import ru.yandex.metrika.segments.core.query.filter.FilterTransformer;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterNull;
import ru.yandex.metrika.segments.core.query.filter.SelectPartFilterValues;
import ru.yandex.metrika.segments.core.query.metric.Metric;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.query.rewrite.FilterContextTransformer;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.type.Type;
import ru.yandex.metrika.segments.core.type.Types;
import ru.yandex.metrika.util.collections.F;

import static java.util.stream.Collectors.toMap;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ToString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dictGetStringOrDefault;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.regionToCountry;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateOrNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateTime;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.tuple;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfE_alias_EventID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfPu_alias_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfPu_alias_PuidVal;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_BannerID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_Load;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_OwnerID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.CounterID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.DateField;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.EventDate;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Ewv_ID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.FakeTuple_alias_String;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.IntField;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.LongField;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.NotStreamableField;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.RegionID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.StartDate;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.StartTime;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.StartURL;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.TrafficSourceID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.URL;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.UserID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.VisitID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.adfox_puid_key;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.adfox_puid_val;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_EVENT_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_PUID_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.EVENTS_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.FAKE_TUPLE;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.NORM;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_DAY;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_DEKAMINUTE;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_HOUR;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_MINUTE;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.PER_WEEK;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.SUM;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.UNIQ;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.UNIQ_UP_1;
import static ru.yandex.metrika.segments.core.query.parts.Aggregates.UNIQ_UP_10;
import static ru.yandex.metrika.segments.core.query.parts.Relation.GT;
import static ru.yandex.metrika.segments.core.query.parts.Relation.IS_NOT_NULL;
import static ru.yandex.metrika.segments.core.query.parts.Relation.LT;
import static ru.yandex.metrika.segments.core.query.parts.Relation.comparableNullableSet;
import static ru.yandex.metrika.segments.core.type.Types.DATE_DASH;
import static ru.yandex.metrika.segments.core.type.Types.INT;
import static ru.yandex.metrika.segments.core.type.Types.INT8;
import static ru.yandex.metrika.segments.core.type.Types.NULLABLE_DATE_DASH;
import static ru.yandex.metrika.segments.core.type.Types.STRING;
import static ru.yandex.metrika.segments.core.type.Types.UINT;
import static ru.yandex.metrika.segments.core.type.Types.UINT32;
import static ru.yandex.metrika.segments.core.type.Types.UINT8;
import static ru.yandex.metrika.segments.core.type.Types.UINT_ID;
import static ru.yandex.metrika.segments.core.type.Types.UINT_ID32;
import static ru.yandex.metrika.segments.core.type.Types.UINT_ID8;
import static ru.yandex.metrika.segments.site.schema.MtLog.Hits.WatchID;

public class SimpleTestAttributeBundle implements AttributeBundle {
    public static final AttributeParamsImpl attributeParams = new AttributeParamsImpl();

    private Set<Attribute> attributes = new HashSet<>();
    private Set<MetricInternalMeta> metricInternalMetas = new HashSet<>();

    /** VISITS **/
    public final Attribute visitID;
    public final Attribute userID;
    public final Attribute counterID;
    public final Attribute startTime;
    public final Attribute dateTime;
    public final Attribute specialDefaultTime;
    public final Attribute startDate;
    public final Attribute specialDefaultDate;
    public final Attribute trafficSourceID;
    public final Attribute startUrl;
    public final Attribute regionCountry;

    public final Attribute eventID;

    public final Attribute adfoxBannerID;
    public final Attribute adfoxLoad;

    public final Attribute adfoxPuidKey;
    public final Attribute adfoxPuidValue;
    public final Attribute adfoxPuidKeyName;
    public final Attribute adfoxPuidValueName;

    public final Attribute adfoxEventID;

    public final Attribute nullableAttribute;
    public final Attribute nullableAttributeWithTuple;

    public final Attribute notStreamableAttribute;

    public final Attribute intAttr;
    public final Attribute longAttr;
    public final Attribute dateAttr;


    public final MetricInternalMeta visits;
    public final MetricInternalMeta users;
    public final MetricInternalMeta adfoxLoads;
    public final MetricInternalMeta sumAdfoxPuidKey;

    /** HITS **/
    public final Attribute hitsCounterID;
    public final Attribute pageView;
    public final Attribute hitsEventID;
    public final Attribute hitsSpecialDefaultDate;
    public final Attribute url;

    private final MetricInternalMeta pageViews;

    public SimpleTestAttributeBundle() {
        visitID = aV("VisitID", UINT, VisitID);
        userID = aV("UserID", UINT, UserID);
        counterID = aV("CounterID", UINT32.withAggregateSet(Sets.newHashSet(UNIQ_UP_1, UNIQ_UP_10)), CounterID);
        startTime = aV("StartTime", Types.DATE_TIME, toDateTime(StartTime));
        dateTime = aV("DateTime", Types.DATE_TIME, toDateTime(StartTime));
        specialDefaultTime = aV("SpecialDefaultTime", Types.DATE_TIME, toDateTime(StartTime));
        startDate = aV("StartDate", Types.METRIKA_API_DATE, StartDate);
        specialDefaultDate = aV("SpecialDefaultDate", Types.METRIKA_API_DATE, StartDate);
        trafficSourceID = aV("TrafficSourceID", INT8, TrafficSourceID);
        startUrl = aV("StartURL", STRING, StartURL);
        regionCountry = aV("RegionCountry", UINT32, regionToCountry(RegionID));

        eventID = aV("EventID", UINT_ID, Ewv_ID).withTupleJoinAndAlias(EVENTS_TUPLE).since("2014-01-01");

        adfoxBannerID = aV("AdfoxBannerID", UINT_ID, Adfox_alias_BannerID).withTupleJoinAndAlias(ADFOX_TUPLE);
        adfoxLoad = aV("AdfoxLoad", UINT8, Adfox_alias_Load).withTupleJoinAndAlias(ADFOX_TUPLE);

        adfoxPuidKey = aV("AdfoxPuidKey", UINT_ID8.withAddAggregates(SUM).withRelationSet(comparableNullableSet), AdfPu_alias_PuidKey).withTupleJoinAndAlias(ADFOX_PUID_TUPLE);
        adfoxPuidValue = aV("AdfoxPuidValue", UINT_ID32, AdfPu_alias_PuidVal).withTupleJoinAndAlias(ADFOX_PUID_TUPLE);
        adfoxPuidKeyName = aV("AdfoxPuidKeyName", STRING, dictGetStringOrDefault(adfox_puid_key.name, tuple(Adfox_alias_OwnerID, toUInt64(AdfPu_alias_PuidKey)), ToString(AdfPu_alias_PuidKey))).withTupleJoinAndAlias(ADFOX_PUID_TUPLE);
        adfoxPuidValueName = aV("AdfoxPuidValueName", STRING, dictGetStringOrDefault(adfox_puid_val.name, toUInt64(AdfPu_alias_PuidVal), ToString(AdfPu_alias_PuidVal))).withTupleJoinAndAlias(ADFOX_PUID_TUPLE);

        adfoxPuidKey.setWithTypeNullValue(true);
        adfoxPuidValue.setWithTypeNullValue(true);

        adfoxEventID = aV("AdfoxEventID", UINT_ID32, AdfE_alias_EventID).withTupleJoinAndAlias(ADFOX_EVENT_TUPLE);

        nullableAttribute = aV("NullableAttribute", NULLABLE_DATE_DASH, toDateOrNull(s("2020-01-01")));
        nullableAttributeWithTuple = aV("NullableAttributeWithTuple", NULLABLE_DATE_DASH, toDateOrNull(FakeTuple_alias_String)).withTupleJoinAndAlias(FAKE_TUPLE);

        notStreamableAttribute = aV("NotStreamableAttribute", STRING, NotStreamableField);

        intAttr = aV("IntAttr", UINT32, IntField);
        intAttr.setWithTypeNullValue(true);
        intAttr.addNotNullFilterFB(Optional.of(new FBLeafFilter(intAttr, LT, 10)));
        intAttr.setRewriteRule(new FilterContextTransformer() {
            @Override
            public FilterTransformer apply(QueryContext context) {
                return new FilterTransformer() {
                    @Override
                    public Filter visit(SelectPartFilterNull filter) {
                        return filter;
                    }

                    @Override
                    public Filter visit(SelectPartFilterValues filter) {
                        if (filter.getRelation().equals(Relation.LT)) {
                            return Compound.and(
                                    filter,
                                    SelectPartFilterValues.singleValue(filter.getSelectPart(), GT, "5", filter.isSelfFilter())
                            );
                        }
                        return filter;
                    }
                };
            }
        });

        dateAttr = aV("DateAttr", DATE_DASH, DateField);
        dateAttr.setWithTypeNullValue(true);

        longAttr = aV("LongAttr", UINT.withRelationSet(comparableNullableSet), LongField);
        longAttr.setWithTypeNullValue(true);
        longAttr.addNotNullFilterFB(Optional.of(new FBLeafFilter(dateAttr, IS_NOT_NULL)));

        visits = mimV("visits", aV("visits", UINT, ClickHouse.un64(1L)).getMetricFactory(SUM));
        users = mimV("users", userID.getMetricFactory(UNIQ));
        adfoxLoads = mimV("adfoxLoads", adfoxLoad.getMetricFactory(SUM));
        sumAdfoxPuidKey = mimV("sumAdfoxPuidKey", adfoxPuidKey.getMetricFactory(SUM));

        hitsCounterID = aH("CounterID", UINT32.withAggregateSet(Sets.newHashSet(UNIQ_UP_1, UNIQ_UP_10)), ClickHouseMeta.HitsCounterID);
        pageView = aH("PageView", INT.withAggregates(SUM, NORM, PER_WEEK, PER_DAY, PER_HOUR, PER_DEKAMINUTE, PER_MINUTE), n64(1));
        hitsEventID = aH("EventID" , UINT_ID, WatchID);
        hitsSpecialDefaultDate = aH("SpecialDefaultDate", Types.METRIKA_API_DATE, EventDate);
        url = aH("URL", STRING, URL);

        pageViews = mimH("pageViews", pageView.getMetricFactory(SUM));


    }

    @Override
    public Set<AbstractAttribute> getAttributes() {
        return new HashSet<>(attributes);
    }

    @Override
    public Map<String, AbstractAttribute> getByApiName() {
        return attributes.stream().collect(toMap(Attribute::toApiName, F.id()));
    }

    @Override
    public Map<String, ParamAttributeParser> getParamAttributeParsers() {
        return Map.of();
    }

    @Override
    public Set<MetricInternalMeta> getMetrics() {
        return new HashSet<>(metricInternalMetas);
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
        return Map.of(
                SimpleTestTableSchema.VISITS,
                new SpecialAttributes(SimpleTestTableSchema.VISITS)
                        .count("visits")
                        .dateAttributes("Default", 0)
                        .key("counter", "CounterID")
                        .init((AbstractAttributeBundle<?>) null),
                SimpleTestTableSchema.HITS,
                new SpecialAttributes(SimpleTestTableSchema.HITS)
                        .count("pageViews")
                        .dateAttributes("Default", 0)
                        .key("counter", "CounterID")
                        .init((AbstractAttributeBundle<?>) null)

        );
    }

    private <T extends CHType> Attribute aV(String name, Type<T> type, Expression<T> template) {
        var a = new Attribute(name, "ym:s:", type, SimpleTestTableSchema.VISITS, attributeParams);
        a.setTemplate(template);
        attributes.add(a);
        return a;
    }

    private MetricInternalMeta mimV(String name, MetricFactory factory) {
        Metric metric = factory.build(ParameterMap.empty());
        var mim = new MetricInternalMeta("ym:s:", SimpleTestTableSchema.VISITS, name, factory, metric.getMeta());
        metricInternalMetas.add(mim);
        return mim;
    }

    private <T extends CHType> Attribute aH(String name, Type<T> type, Expression<T> template) {
        var a = new Attribute(name, "ym:pv:", type, SimpleTestTableSchema.HITS, attributeParams);
        a.setTemplate(template);
        attributes.add(a);
        return a;
    }

    private MetricInternalMeta mimH(String name, MetricFactory factory) {
        Metric metric = factory.build(ParameterMap.empty());
        var mim = new MetricInternalMeta("ym:pv:", SimpleTestTableSchema.HITS, name, factory, metric.getMeta());
        metricInternalMetas.add(mim);
        return mim;
    }
}
