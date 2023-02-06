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
public class OSNameConverterTest {

    private final OSNameConverter osNameConverter = new OSNameConverter();

    @Parameter
    public CHString internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{s("ios"), "iOS"},
                new Object[]{s("android"), "Android"},
                new Object[]{s("windows"), "Windows"},
                new Object[]{s("macos"), "macOS"},
                new Object[]{s("linux"), "Linux"},
                new Object[]{s("unknown"), null}
        );
    }

    @Test
    public void toExternal() throws Exception {
        assertEquals(external, osNameConverter.toExternal(internal, QueryContext.newBuilder().build()));
    }

    @Test
    public void toInternal() throws Exception {
        assertEquals(internal, osNameConverter.toInternal(external, QueryContext.newBuilder().build()));
    }

}
