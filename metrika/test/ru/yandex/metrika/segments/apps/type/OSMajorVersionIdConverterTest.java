package ru.yandex.metrika.segments.apps.type;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.clickhouse.literals.CHString;
import ru.yandex.metrika.segments.core.query.QueryContext;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

@RunWith(Parameterized.class)
public class OSMajorVersionIdConverterTest {

    private final OSMajorVersionIdConverter osMajorVersionNameConverter = new OSMajorVersionIdConverter();

    @Parameter
    public CHString internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{s("ios 11"), "iOS 11"},
                new Object[]{s("android 6"), "android 6"},
                new Object[]{s("windows 10.1"), "WindowsPhone 10.1"},
                new Object[]{s("macos 11"), "macos 11"},
                // пока непонятно, что такое major version у Linux
                new Object[]{s("others"), "others"}
        );
    }

    @Test
    public void toExternal() throws Exception {
        assertEquals(external, osMajorVersionNameConverter.toExternal(internal, QueryContext.newBuilder().build()));
    }

    @Test
    public void toInternal() throws Exception {
        assertEquals(internal, osMajorVersionNameConverter.toInternal(external, QueryContext.newBuilder().build()));
    }

}
