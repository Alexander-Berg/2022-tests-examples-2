package ru.yandex.metrika.segments.core.parser;


import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Ignore;

import ru.yandex.metrika.segments.clickhouse.ast.Nested;
import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.core.query.parts.FromBaseTable;
import ru.yandex.metrika.segments.core.query.parts.FromTable;
import ru.yandex.metrika.segments.core.schema.CrossTableRelations;
import ru.yandex.metrika.segments.core.schema.TableJoin;
import ru.yandex.metrika.segments.core.schema.TableMeta;
import ru.yandex.metrika.segments.core.schema.TableSchemaImpl;
import ru.yandex.metrika.segments.core.schema.TargetTable;
import ru.yandex.metrika.segments.core.schema.TargetTuple;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;

/**
 * Created by orantius on 11/22/15.
 */
@Ignore
public class TestTableSchema extends TableSchemaImpl {
    public static final String COUNTER_ID = "counter";

    public static final TargetTable TEST = new TargetTable("TEST", "ym:s:", "counter")
            .withNames("Визиты", "визитов");
    public static final TargetTable VISITS = TableSchemaSite.VISITS;

    public static final TargetTable TEST2 = new TargetTable("TEST2", "test:", "counter")
            .withNames("Визиты", "визитов");

    public static final Table visits = new Table("visits");
    public static final Nested Goals = new Nested(visits, "Goals", "goals_alias");
    public static final Nested ParsedParams = new Nested(visits, "ParsedParams", "PP");
    public static final Nested Event = new Nested(visits, "Event", "Ewv");

    public static final TargetTuple EVENTS_TUPLE = TargetTuple.tuple(VISITS, "События визитов", Event);
    public static final TargetTuple PARAMS_TUPLE = TargetTuple.tuple(VISITS, "Параметры визитов", ParsedParams);
    public static final TargetTuple GOALS_TUPLE = TargetTuple.tuple(VISITS, "Достижения целей", Goals);

    public static final TargetTable HITS = TableSchemaSite.HITS;
    public static final TargetTable T = new TargetTable("T", "t:", "counter")
            .withNames("Визиты", "визитов");
    public static final TargetTable TT = new TargetTable("TT", "tt:", "counter")
            .withNames("Визиты", "визитов");

    protected TestTableSchema() {
        super(new TargetTable[]{VISITS,HITS,TEST,TEST2,T,TT }, new TableJoin[]{}, new TargetTuple[]{EVENTS_TUPLE});
    }

    @Override
    public boolean isCrossFilterAvailable(TableMeta rootTable, TableMeta filterTable) {
        //if(rootTable==VISITS)
        return true;
    }

    @Override
    public Map<TableMeta, FromTable> getNameConfig(Set<AbstractAttribute> attributes) {

        Table tg = new Table("мамонты, мамонты, прутся напролом");
        HashMap<TableMeta, FromTable> res = new HashMap<>();
        List<TargetTable> tables = tables();
        for (TargetTable table : tables) {
            res.put(table, new FromBaseTable(new Table(tg, table.toID()), new Table(tg, table.toID())));
        }
        return res;
    }

    @Override
    public CrossTableRelations buildRelations(Set<AbstractAttribute> attributes, Map<String, ParamAttributeParser> paramAttributeParsers) {
        CrossTableRelations.Builder builder = CrossTableRelations.builder(attributes, paramAttributeParsers);
        builder.bi(TEST, TEST2).on("eventID").add();
 //           builder
//                    .uni(VISITS, HITS, false, false).on("eventID", "watchID").add()
  //                  .uni(TEST, T, false, false).on("eventID", "watchID").add()
        ;
        return builder.build();
    }
}
