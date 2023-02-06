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
public class OSMajorVersionNameConverterTest {

    private final OSMajorVersionNameConverter osMajorVersionNameConverter = new OSMajorVersionNameConverter();

    @Parameter
    public CHString internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{s("ios 11"), "iOS 11"},
                new Object[]{s("android 6"), "Android 6"},
                new Object[]{s("windows 10"), "Windows 10"},
                new Object[]{s("windows 8"), "WindowsPhone 8"},
                new Object[]{s("windows 7"), "WindowsPhone 7"},
                new Object[]{s("windows 6"), "WindowsMobile 6"},
                new Object[]{s("windows 5"), "WindowsMobile 5"},
                new Object[]{s("windows 11"), "Windows 11"},
                new Object[]{s("macos 11"), "macOS 11"}
                // пока непонятно, что такое major version у Linux
        );
    }

    @Test
    public void toExternalNoNull() throws Exception {
        assertEquals(external, osMajorVersionNameConverter.toExternal(internal, QueryContext.newBuilder().build()));
    }

    @Test
    public void toInternalNoNull() throws Exception {
        assertEquals(internal, osMajorVersionNameConverter.toInternal(external, QueryContext.newBuilder().build()));
    }

}
