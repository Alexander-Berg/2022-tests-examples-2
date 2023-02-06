package ru.yandex.metrika.segments.apps.type;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.clickhouse.literals.CHUInt32;
import ru.yandex.metrika.segments.core.query.QueryContext;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;


@RunWith(Parameterized.class)
public class ClientKitVersionTypeConverterTest {

    private final ClientKitVersionTypeConverter clientKitVersionTypeConverter = new ClientKitVersionTypeConverter();

    @Parameter
    public CHUInt32 internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{un32("280"), "280"},
                new Object[]{un32("3002000"), "3.2.0"}
        );
    }

    @Test
    public void toExternal() {
        assertEquals(external, clientKitVersionTypeConverter.toExternal(internal, QueryContext.newBuilder().build()));
    }

    @Test
    public void toInternal() {
        assertEquals(internal, clientKitVersionTypeConverter.toInternal(external, QueryContext.newBuilder().build()));
    }
}
