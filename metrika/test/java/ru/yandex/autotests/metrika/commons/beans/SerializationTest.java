package ru.yandex.autotests.metrika.commons.beans;

import org.joda.time.DateTime;
import org.junit.Test;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.List;

import static java.math.BigInteger.ZERO;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.apache.commons.lang3.ArrayUtils.*;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.commons.beans.Serialization.deserializeTskv;
import static ru.yandex.autotests.metrika.commons.beans.Serialization.serializeTabSeparated;
import static ru.yandex.autotests.metrika.commons.tabseparated.TabSeparatedKeyValue.TSKV_PREFIX;

/**
 * Created by okunev on 06.07.2017.
 */
public class SerializationTest {

    private static final byte[] EXPECTED = "[]\n".getBytes(StandardCharsets.UTF_8);

    @Test
    public void nullArray() {
        byte[] actual = serializeTabSeparated(TestObject.class, asList(new TestObject()));

        assertThat("объект с незаданным массивом корректно сериализуется", actual, beanEquivalent(EXPECTED));
    }

    @Test
    public void emptyArray() {
        byte[] actual = serializeTabSeparated(TestObject.class,
                asList(new TestObject().withTestField(new Integer[]{})));

        assertThat("объект с пустым массивом корректно сериализуется", actual, beanEquivalent(EXPECTED));
    }

    @Test
    public void deserializeEmptyTskv() {
        List<TestTskvObject> actual = deserializeTskv(TestTskvObject.class, TSKV_PREFIX, true);

        TestTskvObject expected = new TestTskvObject()
                .withBooleanValue(false)
                .withInt8Value(0)
                .withInt16Value(0)
                .withInt32Value(0)
                .withInt64Value(0L)
                .withUInt8Value(0)
                .withUInt16Value(0)
                .withUInt32Value(0L)
                .withUInt64Value(ZERO)
                .withStringValue(EMPTY)
                .withFloat32Value(0f)
                .withFloat64Value(0d)
                .withLocalDateValue(new DateTime(0))
                .withLocalDateTimeValue(new DateTime(0))
                .withVectorStringValue(EMPTY_STRING_ARRAY)
                .withVectorDoubleValue(EMPTY_DOUBLE_OBJECT_ARRAY)
                .withVectorUint16Value(EMPTY_INTEGER_OBJECT_ARRAY)
                .withVectorUint32Value(EMPTY_LONG_OBJECT_ARRAY)
                .withVectorUint64Value(new BigInteger[]{})
                .withByteArrayValue(EMPTY_BYTE_ARRAY);

        assertThat("отсутствующие ключи в tskv десериализуются в дефолтные значения, а не в null",
                actual, beanEquivalent(singletonList(expected)));
    }

    @Test
    public void deserializeSomeTskv() {
        List<TestTskvObject> actual = deserializeTskv(TestTskvObject.class,
                "tskv\tnon_existent_key=value".getBytes(StandardCharsets.UTF_8), true);

        TestTskvObject expected = new TestTskvObject()
                .withBooleanValue(false)
                .withInt8Value(0)
                .withInt16Value(0)
                .withInt32Value(0)
                .withInt64Value(0L)
                .withUInt8Value(0)
                .withUInt16Value(0)
                .withUInt32Value(0L)
                .withUInt64Value(ZERO)
                .withStringValue(EMPTY)
                .withFloat32Value(0f)
                .withFloat64Value(0d)
                .withLocalDateValue(new DateTime(0))
                .withLocalDateTimeValue(new DateTime(0))
                .withVectorStringValue(EMPTY_STRING_ARRAY)
                .withVectorDoubleValue(EMPTY_DOUBLE_OBJECT_ARRAY)
                .withVectorUint16Value(EMPTY_INTEGER_OBJECT_ARRAY)
                .withVectorUint32Value(EMPTY_LONG_OBJECT_ARRAY)
                .withVectorUint64Value(new BigInteger[]{})
                .withByteArrayValue(EMPTY_BYTE_ARRAY);

        assertThat("отсутствующие ключи в tskv десериализуются в дефолтные значения, а не в null",
                actual, beanEquivalent(singletonList(expected)));
    }
}
