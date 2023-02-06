package ru.yandex.metrika.segments.apps.type;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TTuple2;
import ru.yandex.metrika.segments.clickhouse.types.TUInt32;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.type.TypeConverter;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.apps.type.CommonTypeConverterBuilder.tupleWithUInt32AndOSType;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t2;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;


@RunWith(Parameterized.class)
public class TupleWithOSConverterTest {

    private final TypeConverter<TTuple2<TUInt32, TString>> clientKitVersionTypeConverter =
            tupleWithUInt32AndOSType(new ClientKitVersionTypeConverter())
                    .getTypeConverter();

    @Parameter
    public CHLiteral<TTuple2<TUInt32, TString>> internal;

    @Parameter(1)
    public String external;

    @Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return Arrays.asList(
                new Object[]{t2(un32("280"), s("android")), "280 (Android)"},
                new Object[]{t2(un32("3002000"), s("ios")), "3.2.0 (iOS)"},
                new Object[]{t2(un32("255"), s("macos")), "255 (macOS)"},
                new Object[]{t2(un32("100"), s("linux")), "100 (Linux)"},
                new Object[]{t2(un32("0"), s("unknown")), null},
                new Object[]{t2(un32("10"), s("unknown")), "10"}
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
