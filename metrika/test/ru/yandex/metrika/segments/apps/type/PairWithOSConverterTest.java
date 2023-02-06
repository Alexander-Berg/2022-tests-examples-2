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
public class PairWithOSConverterTest {

    private final PairWithOSConverter pairWithOsConverter = new PairWithOSConverter();

    @Parameter
    public CHString internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{s("8.1 (ios)"), "8.1 (iOS)"},
                new Object[]{s("3.45 (android)"), "3.45 (android)"},
                new Object[]{s("3.45 (macos)"), "3.45 (macos)"},
                new Object[]{s("3.12 (linux)"), "3.12 (linux)"},
                new Object[]{s("545.45 (windows)"), "545.45 (WindowsPhone)"},
                new Object[]{s("234 (unknown)"), "234"}
        );
    }

    @Test
    public void toExternal() {
        assertEquals(external, pairWithOsConverter.toExternal(internal, QueryContext.newBuilder().build()));
    }

    @Test
    public void toInternal() {
        assertEquals(internal, pairWithOsConverter.toInternal(external, QueryContext.newBuilder().build()));
    }
}
