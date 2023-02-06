package ru.yandex.metrika.segments.core.parser;

import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Ignore;

import ru.yandex.metrika.segments.core.bundles.SpecialAttributes;
import ru.yandex.metrika.segments.core.bundles.SpecialInfoProvider;
import ru.yandex.metrika.segments.core.schema.TableMeta;

/**
 * Created by orantius on 6/15/15.
 */
@Ignore
public class SpecialAttributesConfigTest implements SpecialInfoProvider {
    // "CounterID", "StartDate", "StartTime", "MoscowStartDate", "UTCStartTime"
    public SpecialAttributes visitAttributes = new SpecialAttributes(TestTableSchema.VISITS)
            .key(TestTableSchema.COUNTER_ID, "CounterID")
            .dateAttributes("Default", 0)
            .utcDate("SpecialMoscowDate")
            .utcDateTime("SpecialMoscowDateTime")
            .user("SpecialUser")
            .count("visits");

    public SpecialAttributes hitsAttributes = new SpecialAttributes(TestTableSchema.HITS)
            .key(TestTableSchema.COUNTER_ID, "CounterID")
            .dateAttributes("Default", 0)
            .utcDate("SpecialMoscowDate")
            .utcDateTime("SpecialMoscowDateTime")
            .user("SpecialUser")
            .count("pageviews");

    public SpecialAttributes tAttributes = new SpecialAttributes(TestTableSchema.T)
            .count("tCount");
    public SpecialAttributes ttAttributes = new SpecialAttributes(TestTableSchema.TT)
            .count("ttCount");


    public SpecialAttributes testAttributes = new SpecialAttributes(TestTableSchema.TEST)
            .count("testCount");
    public SpecialAttributes testAttributes2 = new SpecialAttributes(TestTableSchema.TEST2)
            .count("testCount");

    @Override
    public Map<TableMeta,SpecialAttributes> getSpecialInfo() {
        SpecialAttributes[] data = {visitAttributes, hitsAttributes,tAttributes, ttAttributes, testAttributes,testAttributes2};
        return Stream.of(data).collect(Collectors.toMap(SpecialAttributes::getTableMeta, t -> t));
    }

}
