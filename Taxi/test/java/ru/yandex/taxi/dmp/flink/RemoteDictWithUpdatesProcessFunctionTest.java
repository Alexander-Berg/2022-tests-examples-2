package ru.yandex.taxi.dmp.flink;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import lombok.Data;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.streaming.api.operators.co.KeyedCoProcessOperator;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.KeyedTwoInputStreamOperatorTestHarness;
import org.apache.flink.util.Collector;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.connectors.yt.common.YtClientConfig;
import ru.yandex.taxi.dmp.flink.connectors.yt.common.YtSerializationSchema;
import ru.yandex.taxi.dmp.flink.connectors.yt.consumer.YtRemoteDictWithUpdatesProcessFunction;
import ru.yandex.taxi.dmp.flink.utils.RemoteDictWithUpdatesProcessFunction;
import ru.yandex.yt.ytclient.tables.ColumnValueType;
import ru.yandex.yt.ytclient.tables.TableSchema;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;


class RemoteDictWithUpdatesProcessFunctionTest {
    @Data
    static class TestData {
        private final String key;
        private final String value;

    }

    @Data
    static class TestData2 {
        private final String key;
        private final long value;

    }

    @Test
    public void test() throws Exception {
        var func = new RemoteDictWithUpdatesProcessFunction<String, TestData, TestData, TestData>(
                TestData.class, Duration.ofSeconds(10)) {
            @Override
            protected void connect(TestData value1, TestData value2, Collector<TestData> out) {
                out.collect(new TestData(value1.key, value1.value + value2.value));
            }

            @Override
            protected CompletableFuture<TestData> requestDictValue(String key) {
                return CompletableFuture.completedFuture(new TestData(key, "C"));
            }
        };
        var keySelector = new KeySelector<TestData, String>() {
            @Override
            public String getKey(TestData value) throws Exception {
                return value.key;
            }
        };
        KeyedTwoInputStreamOperatorTestHarness<String, TestData, TestData, TestData> testHarness =
                new KeyedTwoInputStreamOperatorTestHarness<>(new KeyedCoProcessOperator<>(func),
                        keySelector, keySelector, Types.STRING);

        testHarness.open();

        testHarness.processElement1(new StreamRecord<>(new TestData("a", "A")));
        testHarness.processElement2(new StreamRecord<>(new TestData("a", "B")));

        testHarness.processElement2(new StreamRecord<>(new TestData("b", "B")));
        testHarness.processElement1(new StreamRecord<>(new TestData("b", "A")));

        testHarness.snapshot(1, 1);

        checkOutput(
                testHarness.extractOutputValues(),
                Arrays.asList(
                        new TestData("a", "AC"),
                        new TestData("b", "AB")
                )
        );
    }


    @Test
    public void test2() throws Exception {
        var ytClientConfig = new YtClientConfig.Builder().setProxy("hume").build();
        var tableSchema = new TableSchema.Builder()
                .addKey("key", ColumnValueType.STRING)
                .addValue("value", ColumnValueType.INT64)
                .build();
        var ytSerializationSchema = new YtSerializationSchema<>(
                row -> {
                    var values = row.getValues();
                    return new TestData2(values.get(0).stringValue(), values.get(1).longValue());
                },
                new String[]{"key", "value"},
                tableSchema,
                TestData2.class
        );

        var func = new YtRemoteDictWithUpdatesProcessFunction<String, TestData, TestData2, TestData>(
                "//home/sashbel/data/test_dyn_5", new YtClientConfig.Builder().setProxy("hume").build(),
                ytSerializationSchema, TestData2.class, Duration.ofSeconds(10)
        ) {
            @Override
            protected void connect(TestData value1, TestData2 value2, Collector<TestData> out) {
                out.collect(new TestData(value1.key, value1.value + value2.value));
            }
        };
        var keySelector = new KeySelector<TestData, String>() {
            @Override
            public String getKey(TestData value) throws Exception {
                return value.key;
            }
        };
        var keySelector2 = new KeySelector<TestData2, String>() {
            @Override
            public String getKey(TestData2 value) throws Exception {
                return value.key;
            }
        };
        KeyedTwoInputStreamOperatorTestHarness<String, TestData, TestData2, TestData> testHarness =
                new KeyedTwoInputStreamOperatorTestHarness<>(new KeyedCoProcessOperator<>(func),
                        keySelector, keySelector2, Types.STRING);

        testHarness.open();

        testHarness.processElement1(new StreamRecord<>(new TestData("a", "A")));
        testHarness.processElement2(new StreamRecord<>(new TestData2("a", 1)));

        testHarness.processElement2(new StreamRecord<>(new TestData2("b", 1)));
        testHarness.processElement1(new StreamRecord<>(new TestData("b", "A")));

        testHarness.snapshot(1, 1);

        checkOutput(
                testHarness.extractOutputValues(),
                Arrays.asList(
                        // new TestData("a", "A64")
                        new TestData("b", "A1")
                )
        );
    }

    private void checkOutput(List<TestData> output, List<TestData> expected) {
        assertArrayEquals(
                expected.toArray(TestData[]::new),
                output.toArray(TestData[]::new)
        );
    }
}
