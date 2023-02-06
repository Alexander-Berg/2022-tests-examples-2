package ru.yandex.metrika.segments.core.parser;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import com.google.common.collect.Sets;
import org.junit.Ignore;

import ru.yandex.metrika.segments.core.bundles.AttributeBundle;
import ru.yandex.metrika.segments.core.bundles.SpecialAttributes;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParams;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.Attribute;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.type.Types;

/**
 * Created by orantius on 9/28/15.
 */
@Ignore
public class TrTestAttributeBundle implements AttributeBundle {
    Attribute visitString;
    Attribute hitString;
    Attribute visitParamsString;
    Attribute goalString;
    Attribute watchIds;
    Attribute watchId;
    Attribute sUserId;
    Attribute uUserId;
    Attribute csuUserId;
    Attribute csUserId;
    Attribute cUserId;
    Attribute adUserId;
    Attribute aduUserId;

    Attribute pvUserId;
    Attribute elUserId;
    Attribute dlUserId;
    Attribute shUserId;
    Attribute spUserId;
    Attribute ahUserId;
    Attribute pvEventId;
    Attribute elEventId;
    Attribute dlEventId;
    Attribute shEventId;
    Attribute spEventId;
    Attribute ahEventId;

    Attribute upUserId;
    public TrTestAttributeBundle() {

        AttributeParams params = new AttributeParamTest();

        visitString = new Attribute("VS", "ym:s:", Types.STRING, TestTableSchema.VISITS, params);
        hitString = new Attribute("HS", "ym:pv:", Types.STRING, TestTableSchema.HITS, params);
        visitParamsString = new Attribute("VPS", "ym:s:", Types.STRING, TestTableSchema.VISITS, params).withTupleJoinAndAlias(TestTableSchema.PARAMS_TUPLE);
        goalString = new Attribute("GOAL", "ym:s:", Types.STRING, TestTableSchema.VISITS, params).withTupleJoinAndAlias(TestTableSchema.GOALS_TUPLE);

        watchIds = new Attribute("EventID", "ym:s:", Types.INT_ID, TestTableSchema.VISITS, params).withTupleJoinAndAlias(TestTableSchema.EVENTS_TUPLE);
        sUserId = new Attribute("UserID", "ym:s:", Types.INT_ID, TestTableSchema.VISITS, params);
        uUserId = new Attribute("UserID", "ym:u:", Types.INT_ID, TestTableSchema.VISITS, params);
        csuUserId = new Attribute("UserID", "ym:csu:", Types.INT_ID, TestTableSchema.VISITS, params);
        csUserId = new Attribute("UserID", "ym:cs:", Types.INT_ID, TestTableSchema.VISITS, params);
        cUserId = new Attribute("UserID", "ym:c:", Types.INT_ID, TestTableSchema.VISITS, params);
        adUserId = new Attribute("UserID", "ym:ad:", Types.INT_ID, TestTableSchema.VISITS, params);
        aduUserId = new Attribute("UserID", "ym:adu:", Types.INT_ID, TestTableSchema.VISITS, params);

        watchId = new Attribute("WatchID", "ym:pv:", Types.INT_ID, TestTableSchema.HITS, params);
        pvEventId = new Attribute("EventID", "ym:pv:", Types.INT_ID, TestTableSchema.HITS, params);
        elEventId = new Attribute("EventID", "ym:el:", Types.INT_ID, TestTableSchema.HITS, params);
        dlEventId = new Attribute("EventID", "ym:dl:", Types.INT_ID, TestTableSchema.HITS, params);
        shEventId = new Attribute("EventID", "ym:sh:", Types.INT_ID, TestTableSchema.HITS, params);
        spEventId = new Attribute("EventID", "ym:sp:", Types.INT_ID, TestTableSchema.HITS, params);
        ahEventId = new Attribute("EventID", "ym:ah:", Types.INT_ID, TestTableSchema.HITS, params);
        pvUserId = new Attribute("UserID", "ym:pv:", Types.INT_ID, TestTableSchema.HITS, params);
        elUserId = new Attribute("UserID", "ym:el:", Types.INT_ID, TestTableSchema.HITS, params);
        dlUserId = new Attribute("UserID", "ym:dl:", Types.INT_ID, TestTableSchema.HITS, params);
        shUserId = new Attribute("UserID", "ym:sh:", Types.INT_ID, TestTableSchema.HITS, params);
        spUserId = new Attribute("UserID", "ym:sp:", Types.INT_ID, TestTableSchema.HITS, params);
        ahUserId = new Attribute("UserID", "ym:ah:", Types.INT_ID, TestTableSchema.HITS, params);

        upUserId = new Attribute("UserID", "ym:up:", Types.INT_ID, TestTableSchema.HITS, params);
        //specialAttributesConfigSite.getSpecialInfo().values().stream().forEach(SpecialAttributes::init);
    }

    @Override
    public Set<AbstractAttribute> getAttributes() {
        return Sets.newHashSet(visitString, hitString, visitParamsString, goalString, watchId, watchIds,
                sUserId,uUserId,csuUserId,csUserId,cUserId,adUserId,aduUserId,
                pvEventId, elEventId, dlEventId, shEventId, spEventId, ahEventId,
                pvUserId, elUserId, dlUserId, shUserId, spUserId, ahUserId,
                upUserId);
    }

    @Override
    public Map<String, AbstractAttribute> getByApiName() {
        return getAttributes().stream().collect(Collectors.toMap(a->a.toApiName(),a->a));
    }

    @Override
    public Map<String, ParamAttributeParser> getParamAttributeParsers() {
        return new HashMap<>();
    }

    @Override
    public Set<MetricInternalMeta> getMetrics() {
        return new HashSet<>();
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
        SpecialAttributes value = new SpecialAttributes(TestTableSchema.TEST);
        value.count("uniqVS");
        value.dateAttributesDefault();
        HashMap<TableMeta, SpecialAttributes> res = new HashMap<>();
        res.put(TestTableSchema.TEST, value);
        res.put(TestTableSchema.VISITS, value);
        res.put(TestTableSchema.HITS, value);
        return res;
    }
}
