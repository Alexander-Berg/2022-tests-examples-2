package ru.yandex.metrika.segments.core.type;

import java.util.function.Function;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.core.query.QueryContext;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

/**
 * Проверяем обертку над TypeConverter-ом, которая умеет красиво отображать null значения
 * <p>
 * Created by graev on 13/04/2017.
 */
public class LocalizedNullConverterTest {

    public static final String ФЕЙХОА = "фейхоа";

    public static final String NULL = "null";

    public static final String НАЛЛ = "налл";

    private static final TypeConverter<TString> identityConverter = TypeConverters.STRING;

    private static final Function<String, String> nullValueByLang = lang ->
            ImmutableMap.of("en", NULL, "ru", НАЛЛ).get(lang);

    private static final QueryContext ru = QueryContext.newBuilder()
            .lang("ru")
            .build();

    private static final QueryContext en = QueryContext.newBuilder()
            .lang("en")
            .build();

    private static final TypeConverter<TString> converter = new LocalizedNullConverter<>(identityConverter, nullValueByLang);

    @Test
    public void testIsValid() {
        assertThat(converter.isValid(ФЕЙХОА, ru), equalTo(true));
    }

    @Test
    public void testToInternalOrdinary() {
        final CHLiteral<TString> actualInternal = converter.toInternal(ФЕЙХОА, ru);
        assertThat(actualInternal.asString(), equalTo(ФЕЙХОА));
    }

    @Test
    public void testToInternalNull() {
        final CHLiteral<TString> nullInternal = converter.toInternal(НАЛЛ, ru);
        assertThat(nullInternal.asString(), equalTo(""));
    }

    @Test
    public void testToExternalOrdinary() {
        final CHLiteral<TString> ordinaryInternal = s(ФЕЙХОА);
        assertThat(converter.toExternal(ordinaryInternal, en), equalTo(ФЕЙХОА));
    }

    @Test
    public void testToExternalNull() {
        final CHLiteral<TString> nullInternal = s("");
        assertThat(converter.toExternal(nullInternal, en), equalTo(NULL));
    }

    @Test
    public void testInternalNull() {
        assertThat(converter.getNullValue().get().asString(), equalTo(""));
    }

    @Test
    public void testRusNull() {
        assertThat(converter.getExternalNullValue(ru), equalTo(НАЛЛ));
    }

    @Test
    public void testEnNull() {
        assertThat(converter.getExternalNullValue(en), equalTo(NULL));
    }
}
