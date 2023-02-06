package ru.yandex.taxi.dmp.flink.clickhouse;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.With;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.operators.StreamFlatMap;
import org.apache.flink.streaming.util.KeyedOneInputStreamOperatorTestHarness;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.clickhouse.cmt.CMTJsonRowSerializer;
import ru.yandex.taxi.dmp.flink.clickhouse.cmt.CMTMapFunction;
import ru.yandex.taxi.dmp.flink.clickhouse.vcmt.VCMTJsonRowSerializer;
import ru.yandex.taxi.dmp.flink.clickhouse.vcmt.VCMTMapFunction;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class CMTest {
    @RequiredArgsConstructor
    private static class Dummy {
        @Getter
        @With
        @JsonProperty("id")
        private final String id;

        @Getter
        @With
        @JsonProperty("name")
        private final String name;
    }

    private static final Dummy DUMMY_1 = new Dummy("a", "Vasya");
    private static final Dummy DUMMY_2 = new Dummy("a", "Petya");
    private static final Dummy DUMMY_3 = new Dummy("b", "Masha");
    private static final Dummy DUMMY_4 = new Dummy("b", "Michael");

    private static final String DUMMY_1_CMT_PLUS = "{\"id\":\"a\",\"name\":\"Vasya\",\"sign\":1}";
    private static final String DUMMY_1_CMT_MINUS = "{\"id\":\"a\",\"name\":\"Vasya\",\"sign\":-1}";
    private static final String DUMMY_2_CMT_PLUS = "{\"id\":\"a\",\"name\":\"Petya\",\"sign\":1}";
    private static final String DUMMY_2_CMT_MINUS = "{\"id\":\"a\",\"name\":\"Petya\",\"sign\":-1}";
    private static final String DUMMY_3_CMT_PLUS = "{\"id\":\"b\",\"name\":\"Masha\",\"sign\":1}";
    private static final String DUMMY_3_CMT_MINUS = "{\"id\":\"b\",\"name\":\"Masha\",\"sign\":-1}";
    private static final String DUMMY_4_CMT_PLUS = "{\"id\":\"b\",\"name\":\"Michael\",\"sign\":1}";
    private static final String DUMMY_4_CMT_MINUS = "{\"id\":\"b\",\"name\":\"Michael\",\"sign\":-1}";

    private static final String DUMMY_1_VCMT_PLUS = "{\"id\":\"a\",\"name\":\"Vasya\",\"sign\":1,\"version\":0}";
    private static final String DUMMY_1_VCMT_MINUS = "{\"id\":\"a\",\"name\":\"Vasya\",\"sign\":-1,\"version\":0}";
    private static final String DUMMY_2_VCMT_PLUS = "{\"id\":\"a\",\"name\":\"Petya\",\"sign\":1,\"version\":1}";
    private static final String DUMMY_2_VCMT_MINUS = "{\"id\":\"a\",\"name\":\"Petya\",\"sign\":-1,\"version\":1}";
    private static final String DUMMY_3_VCMT_PLUS = "{\"id\":\"b\",\"name\":\"Masha\",\"sign\":1,\"version\":0}";
    private static final String DUMMY_3_VCMT_MINUS = "{\"id\":\"b\",\"name\":\"Masha\",\"sign\":-1,\"version\":0}";
    private static final String DUMMY_4_VCMT_PLUS = "{\"id\":\"b\",\"name\":\"Michael\",\"sign\":1,\"version\":1}";
    private static final String DUMMY_4_VCMT_MINUS = "{\"id\":\"b\",\"name\":\"Michael\",\"sign\":-1,\"version\":1}";

    private static final Dummy[] DUMMIES = new Dummy[]{DUMMY_1, DUMMY_3, DUMMY_2, DUMMY_4};

    @Test
    public void testCMTMapFunction() throws Exception {
        var cmtMapFunction = new CMTMapFunction<>(new CMTJsonRowSerializer<>(Dummy.class));
        var testHarness = new KeyedOneInputStreamOperatorTestHarness<>(new StreamFlatMap<>(cmtMapFunction),
                Dummy::getId,
                Types.STRING);
        testHarness.open();
        var ts = 100L;
        for (var dummy : DUMMIES) {
            testHarness.processElement(dummy, ts);
            ts += 100;
        }
        var output = testHarness.extractOutputValues();
        assertEquals(List.of(DUMMY_1_CMT_PLUS, DUMMY_3_CMT_PLUS, DUMMY_1_CMT_MINUS, DUMMY_2_CMT_PLUS, DUMMY_3_CMT_MINUS,
                DUMMY_4_CMT_PLUS), output);
    }

    @Test
    public void testVCMTMapFunction() throws Exception {
        var vcmtMapFunction = new VCMTMapFunction<>(new VCMTJsonRowSerializer<>(Dummy.class));
        var testHarness = new KeyedOneInputStreamOperatorTestHarness<>(new StreamFlatMap<>(vcmtMapFunction),
                Dummy::getId,
                Types.STRING);
        testHarness.open();
        var ts = 100L;
        for (var dummy : DUMMIES) {
            testHarness.processElement(dummy, ts);
            ts += 100;
        }
        var output = testHarness.extractOutputValues();
        assertEquals(List.of(DUMMY_1_VCMT_PLUS, DUMMY_3_VCMT_PLUS, DUMMY_1_VCMT_MINUS, DUMMY_2_VCMT_PLUS,
                DUMMY_3_VCMT_MINUS, DUMMY_4_VCMT_PLUS), output);
    }

    @Test
    public void testCMTJsonSerializer() {
        var serializer = new CMTJsonRowSerializer<>(Dummy.class);
        serializer.open();
        assertEquals(DUMMY_1_CMT_PLUS, serializer.openRecord(DUMMY_1));
        assertEquals(DUMMY_1_CMT_MINUS, serializer.closeRecord(DUMMY_1));
    }

    @Test
    public void testVCMTJsonSerializer() {
        var serializer = new VCMTJsonRowSerializer<>(Dummy.class);
        serializer.open();
        assertEquals(DUMMY_1_VCMT_PLUS, serializer.openRecord(DUMMY_1, 0));
        assertEquals(DUMMY_1_VCMT_MINUS, serializer.closeRecord(DUMMY_1, 0));
    }
}
