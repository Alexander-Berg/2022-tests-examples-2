package ru.yandex.metrika.segments.core.parser;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.metrika.segments.clickhouse.ast.JoinType;
import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.FromBaseTable;
import ru.yandex.metrika.segments.core.query.parts.FromTable;
import ru.yandex.metrika.segments.core.schema.CrossTableRelations;
import ru.yandex.metrika.segments.core.schema.TableJoin;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.schema.TableNotAggregatedJoin;
import ru.yandex.metrika.segments.core.schema.TableSchemaImpl;
import ru.yandex.metrika.segments.core.schema.TargetTable;
import ru.yandex.metrika.segments.core.schema.TargetTuple;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.collections.F;

import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfoxEvent;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfoxPuid;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Event;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.FakeTuple;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.hits_all;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.visits_all;

public class SimpleTestTableSchema extends TableSchemaImpl {

    public static final TargetTable VISITS = TableSchemaSite.VISITS;
    public static final TargetTable HITS = TableSchemaSite.HITS;

    public static final TargetTuple EVENTS_TUPLE = TargetTuple.tuple(VISITS, "Event", Event);

    public static final TargetTuple ADFOX_TUPLE = TargetTuple.tuple(VISITS, "Adfox", Adfox);
    public static final TargetTuple ADFOX_PUID_TUPLE = TargetTuple.tuple(VISITS, ADFOX_TUPLE, "AdfoxPuid", AdfoxPuid);
    public static final TargetTuple ADFOX_EVENT_TUPLE = TargetTuple.tuple(VISITS, ADFOX_TUPLE, "AdfoxEvent", AdfoxEvent);

    public static final TargetTuple FAKE_TUPLE = TargetTuple.tuple(VISITS, "FAKE_TUPLE", FakeTuple);

    private final Map<Pair<TargetTable, TargetTable>, NotAggregatedJoinAttrsMeta> notAggregatedJoinAttrs = new HashMap<>();

    protected SimpleTestTableSchema() {
        super(new TargetTable[]{VISITS, HITS}, new TableJoin[]{}, new TargetTuple[]{EVENTS_TUPLE, ADFOX_TUPLE, ADFOX_PUID_TUPLE, ADFOX_EVENT_TUPLE});
    }

    @Override
    public boolean isCrossFilterAvailable(TableMeta rootTable, TableMeta filterTable) {
        return true;
    }

    @Override
    public Map<TableMeta, FromTable> getNameConfig(Set<AbstractAttribute> attributes) {
        Table tg = new Table("dummy_name");
        HashMap<TableMeta, FromTable> res = new HashMap<>();
        List<TargetTable> tables = tables();
        for (TargetTable table : tables) {
            if (table.equals(VISITS)) {
                res.put(table, new FromBaseTable(visits_all, visits_all));
            } else if (table.equals(HITS)) {
                res.put(table, new FromBaseTable(hits_all, hits_all));
            } else {
                res.put(table, new FromBaseTable(new Table(tg, table.toID()), new Table(tg, table.toID())));
            }
        }
        return res;
    }

    @Override
    public CrossTableRelations buildRelations(Set<AbstractAttribute> attributes, Map<String, ParamAttributeParser> paramAttributeParsers) {
        return CrossTableRelations.builder(attributes, paramAttributeParsers)
                .bi(VISITS, HITS, true, true, true).on("eventID").add()
                .build();
    }

    @Override
    public void initNotAggregatedJoinAttrs(Set<AbstractAttribute> attributes, Map<String, ParamAttributeParser> paramAttributeParsers) {
        var byApiName = attributes.stream().collect(Collectors.toMap(AbstractAttribute::toApiName, F.id()));
        var visitEventID = byApiName.get(VISITS.getNamespace() + "eventID");
        var hitsEventID = byApiName.get(HITS.getNamespace() + "eventID");

        var notAggregatedJoinAttrsMeta = new NotAggregatedJoinAttrsMeta(VISITS, List.of(visitEventID), HITS, List.of(hitsEventID));
        notAggregatedJoinAttrs.put(notAggregatedJoinAttrsMeta.getKey(), notAggregatedJoinAttrsMeta);
    }

    @Override
    public boolean isCompatibleForJoin(TargetTable first, TargetTable second) {
        return first.equals(VISITS) && second.equals(HITS) || first.equals(HITS) && second.equals(VISITS);
    }

    @Override
    public TableNotAggregatedJoin makeNotAggregatedJoin(TargetTable forDimensions, TargetTable forMetrics) {
        assert isCompatibleForJoin(forDimensions, forMetrics);
        var metaKey = NotAggregatedJoinAttrsMeta.makeKey(forDimensions, forMetrics);
        var meta = notAggregatedJoinAttrs.get(metaKey);
        var left = pickLeft(metaKey);
        var joinType = pickJoinType(metaKey);
        var leftForDims = left.equals(forDimensions);
        var right = leftForDims ? forMetrics : forDimensions;
        return new TableNotAggregatedJoin(left, right, joinType, leftForDims, meta.getAttrsForTable(left), meta.getAttrsForTable(right));
    }

    private TargetTable pickLeft(Pair<TargetTable, TargetTable> pair) {
        if (pair.getLeft().equals(VISITS) && pair.getRight().equals(HITS) ||
                pair.getLeft().equals(HITS) && pair.getRight().equals(VISITS)) {
            return VISITS;
        }
        throw new IllegalArgumentException("Can not pick");
    }

    private JoinType pickJoinType(Pair<TargetTable, TargetTable> pair) {
        if (pair.getLeft().equals(VISITS) && pair.getRight().equals(HITS) ||
                pair.getLeft().equals(HITS) && pair.getRight().equals(VISITS)) {
            return JoinType.all_inner;
        }
        throw new IllegalArgumentException("Can not pick");
    }

    private static class NotAggregatedJoinAttrsMeta {
        final TargetTable left;
        final List<AbstractAttribute> leftAttrs;
        final TargetTable right;
        final List<AbstractAttribute> rightAttrs;

        static Pair<TargetTable, TargetTable> makeKey(TargetTable left, TargetTable right) {
            if (left.toID().compareTo(right.toID()) < 0) {
                return Pair.of(left, right);
            } else {
                return Pair.of(right, left);
            }
        }

        private NotAggregatedJoinAttrsMeta(TargetTable left, List<AbstractAttribute> leftAttrs, TargetTable right, List<AbstractAttribute> rightAttrs) {
            this.left = left;
            this.leftAttrs = leftAttrs;
            this.right = right;
            this.rightAttrs = rightAttrs;
        }

        Pair<TargetTable, TargetTable> getKey() {
            return makeKey(left, right);
        }

        List<AbstractAttribute> getAttrsForTable(TargetTable table) {
            if (table.equals(left)) {
                return leftAttrs;
            }
            if (table.equals(right)) {
                return rightAttrs;
            }
            throw new IllegalArgumentException("Unknown table");
        }
    }
}
