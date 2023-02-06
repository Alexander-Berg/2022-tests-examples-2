package ru.yandex.taxi.dmp.flink.demand.session.window;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.apache.commons.collections.ListUtils;
import org.apache.flink.api.common.ExecutionConfig;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.operators.KeyedProcessOperator;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.KeyedOneInputStreamOperatorTestHarness;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.taxi.dmp.flink.demand.session.DemandSessionProcessFunction;
import ru.yandex.taxi.dmp.flink.demand.session.model.DemandSessionRecord;
import ru.yandex.taxi.dmp.flink.demand.session.model.SessionBreakReason;
import ru.yandex.taxi.dmp.flink.demand.session.model.internal.TaxiEvent;
import ru.yandex.taxi.dmp.flink.utils.DateTimeUtils;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_OFFER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_PIN;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION_WITHOUT_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.OTHER_POINT;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.START_DT;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.str;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.ts;

class DemandSessionProcessFunctionTest {
    private static final transient Logger log = LoggerFactory.getLogger(DemandSessionProcessFunctionTest.class);

    private KeyedOneInputStreamOperatorTestHarness<String, TaxiEvent, DemandSessionRecord> getTestHarness()
            throws Exception {
        var executionConfig = new ExecutionConfig();

        // executionConfig.registerTypeWithKryoSerializer(DemandSessionAggregators.class,
        //        DemandSessionAggregators.KryoSerializer.class);
        // executionConfig.registerTypeWithKryoSerializer(SortTuple.class, SortTuple.KryoSerializer.class);
        // var assigner = GlobalWindows.create();
        // var aggregateFunction = new DemandSessionAggregateFunctionGlobal();

        ValueStateDescriptor<DemandSessionAccumulatorGlobal> stateDesc = new ValueStateDescriptor<>("sessionState",
                DemandSessionAccumulatorGlobal.class);
        stateDesc.initializeSerializerUnlessSet(executionConfig);

        var processFunction = new DemandSessionProcessFunction();

        return new KeyedOneInputStreamOperatorTestHarness<>(
                new KeyedProcessOperator<>(processFunction),
                TaxiEvent::getPhonePdId,
                Types.STRING
        );
    }

    @SuppressWarnings("checkstyle:LineLength")
    @Test
    void successfulOrder() throws Exception {
        for (int i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var records = Arrays.asList(
                    DEFAULT_PIN,
                    DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusSeconds(10))),
                    DEFAULT_ORDER
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true)
                            .withCreatedAt(ts(START_DT.plusSeconds(40))),
                    DEFAULT_PIN.withCreatedAt(ts(START_DT.plusMinutes(1).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
            );

            Collections.shuffle(records);

            testHarness.open();

            testHarness.processWatermark(ts(START_DT.minusMinutes(10)));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
            }

            testHarness.processWatermark(ts(START_DT.plusMinutes(151)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            assertArrayEquals(
                    new DemandSessionRecord[]{
                            DEFAULT_SESSION
                                    .withUtcSessionEndDttm(str(START_DT.plusSeconds(40)))
                                    .withDurationH(40 / 3600.0)
                                    .withBreakReason("success_order")
                                    .withSuccessOrderCnt(1)
                                    .withFirstSuccessOrderAppPlatform("ios"),
                            DEFAULT_SESSION_WITHOUT_ORDER
                                    .withUtcSessionStartDttm(str(START_DT.plusMinutes(1).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
                                    .withLocalSessionStartDttm(str(START_DT.plusMinutes(1).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000).plusHours(3)))
                                    .withUtcSessionEndDttm(str(START_DT.plusMinutes(1).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
                                    .withDurationH(0 / 3600.0)
                                    .withBreakReason(SessionBreakReason.TIMEOUT.getName())
                                    .withPinCnt(1)
                                    .withOfferCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withOfferList(Collections.emptyList())
                    }, output
            );
        }
    }

    @Disabled
    @Test
    void pinsWithinnSameSecondShouldBeInTheSameSession() throws Exception {
        for (int i = 0; i < 1; i++) {
            var testHarness = getTestHarness();

            var records = Arrays.asList(
                    DEFAULT_PIN.withEventId("pin2").withCreatedAt(DateTimeUtils.getTimestampFromDateTime(
                                    "2021-10-08T10:50:05.738569179+03:00", DateTimeUtils.DATE_TIME_ISO_TZ))
                            .withSourceLat(48.967019900065566)
                            .withSourceLon(48.967019900065566),
                    DEFAULT_OFFER
                            .withCreatedAt(1633679405L * 1000),
                    DEFAULT_PIN.withCreatedAt(DateTimeUtils.getTimestampFromDateTime(
                            "2021-10-08T10:50:05.06454274+03:00", DateTimeUtils.DATE_TIME_ISO_TZ))
                            .withSourceLat(48.954302708914696)
                            .withSourceLon(48.954302708914696)
            );

            testHarness.open();

            testHarness.processWatermark(DateTimeUtils.getTimestampFromDateTime("2021-10-08T10:40:00.00000000+03:00",
                    DateTimeUtils.DATE_TIME_ISO_TZ));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp() - 10 * 1000 * 60);
            }

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-10-08T12:00:17").plusMinutes(10)
                    .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            fixOutputForTesting(output);

            System.out.println(Arrays.toString(output));

            assertArrayEquals(
                    new DemandSessionRecord[] {
                            DEFAULT_SESSION_WITHOUT_ORDER
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-10-08T07:50:05")))
                                    .withLocalSessionStartDttm(str(START_DT.plusMinutes(1)
                                            .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000).plusHours(3)))
                                    .withUtcSessionEndDttm(str(START_DT.plusMinutes(1)
                                            .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
                                    .withDurationH(0 / 3600.0)
                                    .withBreakReason(SessionBreakReason.DISTANCE.getName())
                                    .withPinCnt(2)
                                    .withOfferCnt(1)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withOfferList(Collections.emptyList())
                    }, output
            );
        }
    }

    @Test
    void waitOrder() throws Exception {
        for (int i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var records = Arrays.asList(
                    DEFAULT_PIN,
                    DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusSeconds(10))),
                    DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusSeconds(40)))
            );
            Collections.shuffle(records);

            testHarness.open();

            testHarness.processWatermark(ts(START_DT.minusMinutes(10)));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp() - Duration.ofMinutes(10).toMillis());
            }
            var successOrder = DEFAULT_ORDER
                    .withCreatedAt(ts(START_DT.plusSeconds(40)))
                    .withUpdatedAt(ts(START_DT.plusMinutes(5)))
                    .withFinishedOrderFlg(true)
                    .withSuccessOrderFlg(true);
            testHarness.processElement(new StreamRecord<>(successOrder, successOrder.getEventTimestamp()));
            testHarness.processWatermark(ts(START_DT.plusHours(3)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            assertArrayEquals(
                    new DemandSessionRecord[]{
                            DEFAULT_SESSION
                                    .withUtcSessionEndDttm(str(START_DT.plusSeconds(40)))
                                    .withLocalSessionStartDttm(str(START_DT.plusHours(3)))
                                    .withDurationH(40 / 3600.0)
                                    .withBreakReason("success_order")
                                    .withSuccessOrderCnt(1)
                                    .withUtcDt("2021-03-29")
                                    .withFirstSuccessOrderAppPlatform("ios")
                    },
                    output
            );
        }
    }

    @Test
    void timeout() throws Exception {
        var testHarness = getTestHarness();

        var records = Arrays.asList(
                DEFAULT_PIN,
                DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusSeconds(10))),
                DEFAULT_PIN.withCreatedAt(ts(START_DT.plusMinutes(1)
                        .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
        );

        testHarness.open();

        System.out.println(records);

        testHarness.processWatermark(ts(START_DT.minusMinutes(10)));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
            testHarness.processWatermark(record.getEventTimestamp() - Duration.ofMinutes(10).toMillis());
        }

        testHarness.processWatermark(ts(START_DT.plusHours(4)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> {
            ds.setSessionId("session_id");
            ds.setLastEventTs(0);
        });

        var session2endTs = str(START_DT.plusMinutes(1).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000));
        var session2endTsLocal = str(START_DT.plusMinutes(1)
                .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000).plusHours(3));


        assertArrayEquals(
                new DemandSessionRecord[] {
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionEndDttm(str(START_DT.plusSeconds(10)))
                                .withDurationH(10 / 3600.0)
                                .withUtcDt("2021-03-29"),
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionStartDttm(session2endTs)
                                .withUtcSessionEndDttm(session2endTs)
                                .withLocalSessionStartDttm(session2endTsLocal)
                                .withOfferList(Collections.emptyList())
                                .withShownAltofferList(Collections.emptyList())
                                .withDurationH(0.0)
                                .withOfferCnt(0)
                                .withUtcDt("2021-03-29")
                },
                output
        );
    }

    @Test
    void distance() throws Exception {
        var testHarness = getTestHarness();

        var records = Arrays.asList(
                DEFAULT_PIN,
                DEFAULT_PIN.withEventId("pin_3").withCreatedAt(ts(START_DT.plusSeconds(20))),
                DEFAULT_PIN
                        .withEventId("pin_2")
                        .withSourceLon(OTHER_POINT.getLon())
                        .withSourceLat(OTHER_POINT.getLat())
                        .withCreatedAt(ts(START_DT.plusSeconds(10)))
        );

        testHarness.open();

        testHarness.processWatermark(ts(START_DT.minusSeconds(1)));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(START_DT.plusHours(2)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> {
            ds.setSessionId("session_id");
            ds.setLastEventTs(0);
        });

        assertArrayEquals(
                new DemandSessionRecord[]{
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withDurationH(0.0)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withPinList(List.of("pin_id"))
                                .withDisplacedSessionFlg(true)
                                .withShownAltofferList(Collections.emptyList())
                                .withBreakReason(SessionBreakReason.DISTANCE.getName()),
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionStartDttm(str(START_DT.plusSeconds(10)))
                                .withUtcSessionEndDttm(str(START_DT.plusSeconds(10)))
                                .withLocalSessionStartDttm(str(START_DT.plusSeconds(10).plusHours(3)))
                                .withDurationH(0.0)
                                .withShownAltofferList(Collections.emptyList())
                                .withDisplacedSessionFlg(true)
                                .withPinList(List.of("pin_2"))
                                .withFirstEventLon(OTHER_POINT.getLon())
                                .withFirstEventLat(OTHER_POINT.getLat())
                                .withLastEventLon(OTHER_POINT.getLon())
                                .withLastEventLat(OTHER_POINT.getLat())
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withBreakReason(SessionBreakReason.DISTANCE.getName()),
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionStartDttm(str(START_DT.plusSeconds(20)))
                                .withLocalSessionStartDttm(str(START_DT.plusSeconds(20).plusHours(3)))
                                .withUtcSessionEndDttm(str(START_DT.plusSeconds(20)))
                                .withPinList(List.of("pin_3"))
                                .withDurationH(0.0)
                                .withShownAltofferList(Collections.emptyList())
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                },
                output
        );
    }

    @Test
    void merge() throws Exception {
        var testHarness = getTestHarness();

        var records = Arrays.asList(
                DEFAULT_PIN,
                DEFAULT_PIN
                        .withEventId("pin_3")
                        .withCreatedAt(ts(START_DT.plusMinutes(35))),
                DEFAULT_PIN
                        .withEventId("pin_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(20)))
        );

        testHarness.open();

        testHarness.processWatermark(ts(START_DT.minusSeconds(1)));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(START_DT.plusHours(2)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> {
            ds.setSessionId("session_id");
            ds.setLastEventTs(0);
        });

        System.out.println(Arrays.toString(output));

        assertArrayEquals(
                new DemandSessionRecord[]{
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionEndDttm(str(START_DT.plusMinutes(35)))
                                .withDurationH(35 / 60.0)
                                .withPinCnt(3)
                                .withPinWWaitTimeCnt(3)
                                .withOfferList(Collections.emptyList())
                                .withShownAltofferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withPinList(List.of("pin_2", "pin_3", "pin_id"))
                },
                output
        );
    }

    @Test
    void waitAllOrders() throws Exception {
        for (int i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var records = Arrays.asList(
                    DEFAULT_PIN,
                    DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusSeconds(10))),
                    DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(1))),
                    DEFAULT_PIN.withEventId("pin_2").withCreatedAt(ts(START_DT.plusMinutes(2))),
                    DEFAULT_ORDER
                            .withEventId("order_id_2")
                            .withCreatedAt(ts(START_DT.plusMinutes(3)))
            );
            Collections.shuffle(records);

            testHarness.open();

            testHarness.processWatermark(ts(START_DT.minusSeconds(1)));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
            }
            testHarness.processWatermark(ts(START_DT.plusHours(1)));

            var successOrder = DEFAULT_ORDER
                    .withCreatedAt(ts(START_DT.plusMinutes(1)))
                    .withUpdatedAt(ts(START_DT.plusMinutes(90)))
                    .withFinishedOrderFlg(true)
                    .withSuccessOrderFlg(true);

            var successOrder2 = DEFAULT_ORDER
                    .withEventId("order_id_2")
                    .withCreatedAt(ts(START_DT.plusMinutes(3)))
                    .withUpdatedAt(ts(START_DT.plusMinutes(40)))
                    .withSuccessOrderFlg(true);
            //.withFinishedOrderFlg(true);

            testHarness.processElement(new StreamRecord<>(successOrder, successOrder.getEventTimestamp()));
            testHarness.processElement(new StreamRecord<>(successOrder2, successOrder2.getEventTimestamp()));

            testHarness.processWatermark(ts(START_DT.plusHours(7)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            assertArrayEquals(new DemandSessionRecord[]{
                    DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                            .withUtcSessionEndDttm(str(START_DT.plusMinutes(1)))
                            .withDurationH(1.0 / 60)
            }, output);
        }
    }

    private void fixOutputForTesting(DemandSessionRecord[] sessions) {
        Arrays.stream(sessions).forEach(ds -> {
            ds.setSessionId("session_id");
            ds.setUtcDt(DEFAULT_SESSION.getUtcDt());
        });
    }

    @Test
    void waitAllOrdersFinished() throws Exception {
        for (int i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var records = Arrays.asList(
                    DEFAULT_PIN,
                    DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusSeconds(10))),
                    DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusSeconds(40))),
                    DEFAULT_ORDER
                            .withEventId("order_id_2")
                            .withCreatedAt(ts(START_DT.plusSeconds(41))),
                    DEFAULT_PIN.withEventId("pin2").withCreatedAt(ts(START_DT.plusMinutes(5).plusSeconds(41)))
            );
            Collections.shuffle(records);

            testHarness.open();

            testHarness.processWatermark(ts(START_DT.minusMinutes(10)));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp() - Duration.ofMinutes(10).toMillis());
            }
            // testHarness.processWatermark(ts(START_DT.plusHours(1)));
            var successOrder = DEFAULT_ORDER
                    .withCreatedAt(ts(START_DT.plusSeconds(40)))
                    .withUpdatedAt(ts(START_DT.plusMinutes(90)))
                    .withFinishedOrderFlg(true)
                    .withSuccessOrderFlg(true);

            var finishedOrder2 = DEFAULT_ORDER
                    .withCreatedAt(ts(START_DT.plusSeconds(41)))
                    .withEventId("order_id_2")
                    .withUpdatedAt(ts(START_DT.plusMinutes(100)))
                    .withFinishedOrderFlg(true);

            testHarness.processElement(new StreamRecord<>(successOrder, successOrder.getEventTimestamp()));
            testHarness.processElement(new StreamRecord<>(finishedOrder2, finishedOrder2.getEventTimestamp()));
            testHarness.processWatermark(ts(START_DT.plusHours(2)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

            fixOutputForTesting(output);

            assertArrayEquals(
                    new DemandSessionRecord[]{
                            DEFAULT_SESSION
                                    .withUtcSessionEndDttm(str(START_DT.plusSeconds(40)))
                                    .withDurationH(40 / 3600.0)
                                    .withBreakReason("success_order")
                                    .withSuccessOrderCnt(1)
                                    .withFirstSuccessOrderAppPlatform("ios")
                                    .withLastEventTs(ts(START_DT.plusMinutes(90)))
                                    .withOrderList(List.of("order_id")),
                            DEFAULT_SESSION
                                    .withUtcSessionStartDttm(str(START_DT.plusSeconds(41)))
                                    .withUtcSessionEndDttm(str(START_DT.plusMinutes(5).plusSeconds(41)))
                                    .withLocalSessionStartDttm(str(START_DT.plusSeconds(41).plusHours(3)))
                                    .withDurationH(5.0 / 60)
                                    .withOfferCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withPinList(List.of("pin2"))
                                    .withOrderList(List.of("order_id_2"))
                                    .withLastEventTs(ts(START_DT.plusMinutes(100)))
                                    .withOfferList(Collections.emptyList())
                    },
                    output
            );
        }
    }

    @Test
    void maxDuration() throws Exception {
        var testHarness = getTestHarness();

        var records = Arrays.asList(
                DEFAULT_PIN,
                DEFAULT_OFFER
                        .withCreatedAt(ts(START_DT.plusMinutes(20))),
                DEFAULT_PIN
                        .withEventId("pin_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(40))),
                DEFAULT_PIN
                        .withEventId("pin_id_3")
                        .withCreatedAt(ts(START_DT.plusMinutes(60))),
                DEFAULT_PIN
                        .withEventId("pin_id_4")
                        .withCreatedAt(ts(START_DT.plusMinutes(80))),
                DEFAULT_PIN
                        .withEventId("pin_id_5")
                        .withCreatedAt(ts(START_DT.plusMinutes(100))),
                DEFAULT_PIN
                        .withEventId("pin_id_6")
                        .withCreatedAt(ts(START_DT.plusMinutes(115))),
                DEFAULT_PIN
                        .withEventId("pin_id_7")
                        .withCreatedAt(ts(START_DT.plusMinutes(115).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)))
        );

        var session2EndTs = START_DT.plusMinutes(115).plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000);
        var session2End = str(session2EndTs);
        var session2EndLocal = str(session2EndTs.plusHours(3));

        testHarness.open();

        testHarness.processWatermark(ts(START_DT.minusSeconds(1)));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(START_DT.plusMinutes(115)
                .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)
                .plusSeconds(DemandSession.TIMEOUT_MILLIS / 1000)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        fixOutputForTesting(output);

        assertArrayEquals(
                new DemandSessionRecord[]{
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionEndDttm(str(START_DT.plusMinutes(115)))
                                .withDurationH(115 / 60.0)
                                .withLastEventTs(ts(START_DT.plusMinutes(115)))
                                .withPinCnt(6)
                                .withPinWWaitTimeCnt(6)
                                .withPinList(List.of("pin_id", "pin_id_2", "pin_id_3", "pin_id_4", "pin_id_5",
                                        "pin_id_6"))
                                .withBreakReason(SessionBreakReason.SESSION_DURATION.getName()),
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionStartDttm(session2End)
                                .withLocalSessionStartDttm(session2EndLocal)
                                .withUtcSessionEndDttm(session2End)
                                .withLastEventTs(ts(session2EndTs))
                                .withDurationH(0.0)
                                .withPinList(List.of("pin_id_7"))
                                .withOfferList(Collections.emptyList())
                                .withShownAltofferList(Collections.emptyList())
                                .withOfferCnt(0)
                },
                output
        );
    }

    @SuppressWarnings("checkstyle:LineLength")
    @Test
    void seriesOfOrdersSuccessfulSequential() throws Exception {
        var testHarness = getTestHarness();

        var order1 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T06:40:18")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:40:18")))
                .withEventId("4423e444cbe02a06a8eec2b7de91baa2");

        var order2 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T06:50:47")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:50:47")))
                .withEventId("bf4bd5e5dd9f3d4191e70510bd427bb5");

        var order3 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T07:32:04")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:32:04")))
                .withEventId("0391000b371dd75ba2438db68eb3ba99");

        var order4 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T07:51:29")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:51:29")))
                .withEventId("e60d12db52fd1c089b8b775775ec9e99");

        var records = Arrays.asList(
                order1,
                DEFAULT_PIN
                        .withEventId("c9629620738c5a69fdd1f9723fe96a6c")
                        .withPinOrderId("4423e444cbe02a06a8eec2b7de91baa2")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T06:40:28"))),
                order1.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:40:28"))),
                order1.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:40:33"))),
                order2.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:50:49"))),
                DEFAULT_PIN
                        .withEventId("2e29aa5886f774b38e01bb65fa69e053")
                        .withPinOrderId("bf4bd5e5dd9f3d4191e70510bd427bb5")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T06:50:56"))),
                order2.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:50:56"))),
                order1.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T06:55:25"))),
                order1.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:04:47")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true),
                order2.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:11:44"))),
                order2.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:26:00"))),
                order3,
                DEFAULT_PIN
                        .withEventId("7a19411ed515e1b55341bd54ce79ebfa")
                        .withPinOrderId("0391000b371dd75ba2438db68eb3ba99")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T07:32:14"))),
                order3.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:32:14"))),
                order3.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:38:37"))),
                order2.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:39:11")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                order3.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:43:11"))),
                order4,
                DEFAULT_PIN
                        .withEventId("d6e7a67d40e3b6041ddb3f1c8f36e39e")
                        .withPinOrderId("e60d12db52fd1c089b8b775775ec9e99")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T07:51:56"))),
                order3.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T07:52:38")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true),
                DEFAULT_PIN
                        .withEventId("17975efd5d59d9db9fc00d1e9deda911")
                        .withPinOrderId("2f9848e775eed0928b5bac72eeb5b317")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T07:53:49"))),
                DEFAULT_PIN
                        .withPinOrderId("2f744a6e10f0c420ac8273f936ba0932")
                        .withEventId("0204f8a5898b548c2b485fcd160b95ea")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-26T08:06:07"))),
                order4.withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T08:15:36"))),
                order4
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-26T08:26:08")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true)
        );

        testHarness.open();

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-08-26T05:40:18")));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
            testHarness.processWatermark(record.getEventTimestamp());
        }

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-08-26T07:52:38").plusMinutes(30)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> {
            ds.setSessionId("session_id");
            ds.setLastEventTs(0);
        });

        fixOutputForTesting(output);

        assertArrayEquals(
                new DemandSessionRecord[]{
                        DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                .withOrderList(List.of("4423e444cbe02a06a8eec2b7de91baa2"))
                                .withDurationH(10.0 / 3600)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withShownAltofferList(Collections.emptyList())
                                .withPinList(List.of("c9629620738c5a69fdd1f9723fe96a6c"))
                                .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-08-26T06:40:18")))
                                .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-08-26T06:40:18").plusHours(3)))
                                .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-08-26T06:40:28"))),
                        DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                .withOrderList(List.of("bf4bd5e5dd9f3d4191e70510bd427bb5"))
                                .withDurationH(9.0 / 3600)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withShownAltofferList(Collections.emptyList())
                                .withPinList(List.of("2e29aa5886f774b38e01bb65fa69e053"))
                                .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-08-26T06:50:47")))
                                .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-08-26T06:50:47").plusHours(3)))
                                .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-08-26T06:50:56"))),
                        DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                .withOrderList(List.of("0391000b371dd75ba2438db68eb3ba99"))
                                .withDurationH(10.0 / 3600)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withShownAltofferList(Collections.emptyList())
                                .withPinList(List.of("7a19411ed515e1b55341bd54ce79ebfa"))
                                .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-08-26T07:32:04")))
                                .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-08-26T07:32:04").plusHours(3)))
                                .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-08-26T07:32:14"))),
                        DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                .withOrderList(List.of("e60d12db52fd1c089b8b775775ec9e99"))
                                .withDurationH(27.0 / 3600)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withShownAltofferList(Collections.emptyList())
                                .withPinList(List.of("d6e7a67d40e3b6041ddb3f1c8f36e39e"))
                                .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-08-26T07:51:29")))
                                .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-08-26T07:51:29").plusHours(3)))
                                .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-08-26T07:51:56")))
                },
                output
        );
    }

    @Test
    void ordersWithMultiorderFlagBelongToTheSameSession() throws Exception {
        var testHarness = getTestHarness();

        var order1 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:46")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:46")))
                .withEventId("520406facd87129d9af8bb414635bffd")
                .withMultiorderFlg(true);

        var order2 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:50")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:50")))
                .withEventId("3e29c8cc75c51ca58440c629464af647")
                .withMultiorderFlg(true);

        var order3 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:49")))
                .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:49")))
                .withEventId("398efbabb2df1ae3bafb565d5fcc692f");

        var records = Arrays.asList(
                DEFAULT_PIN
                        .withEventId("49886d578ee7fd8f8aa438cf724b932c")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:17"))),
                DEFAULT_PIN
                        .withEventId("21c355108218d4f03a4c2e7de4e9fcba")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:25"))),
                DEFAULT_PIN
                        .withEventId("9fa550f503d32ff1ac67abb8b1797efa")
                        .withPinOrderId("520406facd87129d9af8bb414635bffd")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:46"))),
                order1,
                DEFAULT_PIN
                        .withEventId("e6cdc3fe20f8c4cbbf9d7496c7bd0e1b")
                        .withPinOrderId("520406facd87129d9af8bb414635bffd")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:19:12"))),
                DEFAULT_PIN
                        .withEventId("306adb0475bf6b8d6689e38307485423")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:31"))),
                DEFAULT_PIN
                        .withEventId("0294c7e03f1aa25524fbadfc41b45ec8")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:39"))),
                DEFAULT_PIN
                        .withEventId("efec553d0cf28d4f6077874aed78c11f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:44"))),
                order2,
                order1
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:33:10")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true),
                order2
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:37:29")))
                        .withFinishedOrderFlg(true),
                DEFAULT_PIN
                        .withEventId("d7d24313ad1780ba812972cdd427a758")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:41"))),
                order3,
                DEFAULT_PIN
                        .withEventId("38d9846296a2d3a69ad206c963d71e08")
                        .withPinOrderId("398efbabb2df1ae3bafb565d5fcc692f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:50"))),
                DEFAULT_PIN
                        .withEventId("460647e7021ce3d1a7a996df63c8d4bd")
                        .withPinOrderId("398efbabb2df1ae3bafb565d5fcc692f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:44:03"))),
                order3
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T07:01:04")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true)
        );

        testHarness.open();

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-08-12T06:18:00")));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getCreatedAt()));
        }

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-08-12T07:01:04").plusMinutes(30)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> {
            ds.setSessionId("session_id");
            ds.setLastEventTs(0);
        });

        fixOutputForTesting(output);

        assertArrayEquals(
                new DemandSessionRecord[]{
                        DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                .withOrderList(List.of("398efbabb2df1ae3bafb565d5fcc692f",
                                        "3e29c8cc75c51ca58440c629464af647", "520406facd87129d9af8bb414635bffd"))
                                .withDurationH((25.0 * 60 + 46) / 3600)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                                .withPinCnt(10)
                                .withPinList(List.of("0294c7e03f1aa25524fbadfc41b45ec8",
                                        "21c355108218d4f03a4c2e7de4e9fcba",
                                        "306adb0475bf6b8d6689e38307485423", "38d9846296a2d3a69ad206c963d71e08",
                                        "460647e7021ce3d1a7a996df63c8d4bd", "49886d578ee7fd8f8aa438cf724b932c",
                                        "9fa550f503d32ff1ac67abb8b1797efa", "d7d24313ad1780ba812972cdd427a758",
                                        "e6cdc3fe20f8c4cbbf9d7496c7bd0e1b", "efec553d0cf28d4f6077874aed78c11f"))
                                .withPinWWaitTimeCnt(10)
                                .withSuccessOrderCnt(2)
                                .withMultiorderFlg(true)
                                .withShownAltofferList(Collections.emptyList())
                                .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-08-12T06:18:17")))
                                .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-08-12T06:18:17").plusHours(3)))
                                .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-08-12T06:44:03")))
                }, output);
    }

    @Test
    void stuff() throws Exception {
        var testHarness = getTestHarness();

        var order1 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:46")))
                .withEventId("3f23521367d4c209a623c64d02c63476")
                .withMultiorderFlg(true);

        var order2 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:50")))
                .withEventId("3e29c8cc75c51ca58440c629464af647")
                .withMultiorderFlg(true);

        var order3 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:49")))
                .withEventId("398efbabb2df1ae3bafb565d5fcc692f");

        var records = Arrays.asList(
                DEFAULT_PIN
                        .withEventId("49886d578ee7fd8f8aa438cf724b932c")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:17"))),
                DEFAULT_PIN
                        .withEventId("21c355108218d4f03a4c2e7de4e9fcba")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:25"))),
                DEFAULT_PIN
                        .withEventId("9fa550f503d32ff1ac67abb8b1797efa")
                        .withPinOrderId("520406facd87129d9af8bb414635bffd")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:18:46"))),
                order1,
                DEFAULT_PIN
                        .withEventId("e6cdc3fe20f8c4cbbf9d7496c7bd0e1b")
                        .withPinOrderId("520406facd87129d9af8bb414635bffd")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:19:12"))),
                DEFAULT_PIN
                        .withEventId("306adb0475bf6b8d6689e38307485423")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:31"))),
                DEFAULT_PIN
                        .withEventId("0294c7e03f1aa25524fbadfc41b45ec8")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:39"))),
                DEFAULT_PIN
                        .withEventId("efec553d0cf28d4f6077874aed78c11f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:24:44"))),
                order2,
                order1
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:33:10")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true),
                order2
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T06:37:29")))
                        .withFinishedOrderFlg(true),
                DEFAULT_PIN
                        .withEventId("d7d24313ad1780ba812972cdd427a758")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:41"))),
                order3,
                DEFAULT_PIN
                        .withEventId("38d9846296a2d3a69ad206c963d71e08")
                        .withPinOrderId("398efbabb2df1ae3bafb565d5fcc692f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:43:50"))),
                DEFAULT_PIN
                        .withEventId("460647e7021ce3d1a7a996df63c8d4bd")
                        .withPinOrderId("398efbabb2df1ae3bafb565d5fcc692f")
                        .withCreatedAt(ts(LocalDateTime.parse("2021-08-12T06:44:03"))),
                order3
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-08-12T07:01:04")))
                        .withFinishedOrderFlg(true)
                        .withSuccessOrderFlg(true)
        );

        testHarness.open();

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-08-12T07:01:04").plusMinutes(5)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> ds.setSessionId("session_id"));

        System.out.println(Arrays.toString(output));

        // [DemandSessionRecord(phonePdId=phone_pd_id, utcSessionStartDttm=2021-08-12 06:18:17, sessionId=session_id,
        // appPlatformList=[ios], breakReason=success_order, durationH=0.4255555555555556, firstEventLat=55.75,
        // firstEventLon=37.61, firstSuccessOrderAppPlatform=ios, firstSurgeValue=1.0, firstWaitingTimeSec=123.0,
        // lastAppPlatform=ios, lastEventLat=55.75, lastEventLon=37.61, lastOrderTariff=econom, lastSurgeValue=1.0,
        // lastTariffZone=moscow, lastWaitingTimeSec=123.0, offerCnt=0, offerList=[],
        // orderList=[398efbabb2df1ae3bafb565d5fcc692f, 3e29c8cc75c51ca58440c629464af647,
        // 520406facd87129d9af8bb414635bffd], pinCnt=8, pinWWaitTimeCnt=8, successOrderCnt=2, userIdList=[A],
        // utcSessionEndDttm=2021-08-12 06:43:49),
        //
        // DemandSessionRecord(phonePdId=phone_pd_id,
        // utcSessionStartDttm=2021-08-12 06:43:50, sessionId=session_id, appPlatformList=[ios], breakReason=timeout,
        // durationH=0.003611111111111111, firstEventLat=55.75, firstEventLon=37.61,
        // firstSuccessOrderAppPlatform=null, firstSurgeValue=1.0, firstWaitingTimeSec=123.0, lastAppPlatform=ios,
        // lastEventLat=55.75, lastEventLon=37.61, lastOrderTariff=null, lastSurgeValue=1.0, lastTariffZone=moscow,
        // lastWaitingTimeSec=123.0, offerCnt=0, offerList=[], orderList=[], pinCnt=2, pinWWaitTimeCnt=2,
        // successOrderCnt=0, userIdList=[A], utcSessionEndDttm=2021-08-12 06:44:03)]

        /*

        assertArrayEquals(
                new DemandSessionRecord[] {
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionEndDttm(str(START_DT.plusMinutes(115)))
                                .withDurationH(115 / 60.0)
                                .withPinCnt(6)
                                .withPinWWaitTimeCnt(6)
                                .withBreakReason(SessionBreakReason.SESSION_DURATION.getName()),
                        DEFAULT_SESSION_WITHOUT_ORDER
                                .withUtcSessionStartDttm(str(START_DT.plusMinutes(125)))
                                .withUtcSessionEndDttm(str(START_DT.plusMinutes(125)))
                                .withDurationH(0.0)
                                .withOfferList(Collections.emptyList())
                                .withOfferCnt(0)
                },
                output
        ); */
    }

    @Test
    void stuff2() throws Exception {
        var testHarness = getTestHarness();

        var order1 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T05:50:18")))
                .withEventId("dce560c9bed6dddf97d1ece4a025c94a");

        var order2 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T05:54:16")))
                .withEventId("12f445e6b56fddff936475e5a036eedb");

        var order3 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T05:56:08")))
                .withEventId("972ce37f817bc5259e7986f663efe814");

        var order4 = DEFAULT_ORDER
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T05:57:19")))
                .withEventId("ef7003da1f69d294a1a7833708776ab7");

        var records = Arrays.asList(
                order1,
                order2,
                order3,
                order4,
                order1
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T06:03:24")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                order4
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T06:05:25")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                order2
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T06:16:04")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                order3
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T06:16:55")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true)


        );

        testHarness.open();

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-14T06:16:55").plusMinutes(5)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);
        Arrays.stream(output).iterator().forEachRemaining(ds -> ds.setSessionId("session_id"));

        System.out.println(Arrays.toString(output));

    }

    @Test
    void stuff3() throws Exception {
        var testHarness = getTestHarness();

        var order1 = DEFAULT_ORDER
                .withEventId("2aa4d128bec5ddec94d2631dffce0cdc")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T18:02:02")));

        var order2 = DEFAULT_ORDER
                .withEventId("c2a0bff7f40dc811802939b5b6330954")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T18:16:05")));

        var order3 = DEFAULT_ORDER
                .withEventId("1575e507c1bf305aa52f334ce95968e2")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T19:38:04")));

        var order4 = DEFAULT_ORDER
                .withEventId("afb2151433063ee1bc48f200d5899e4b")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T19:38:13")));

        var records = Arrays.asList(
                order1,
                order2,
                order1
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T18:45:38")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                order3,
                order4,
                order3
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T19:43:04")))
                        .withFinishedOrderFlg(true),
                order4
                        .withCreatedAt(ts(LocalDateTime.parse("2021-09-14T20:05:36")))
                        .withFinishedOrderFlg(true),
                order2
                        .withUpdatedAt(ts(LocalDateTime.parse("2021-09-14T20:50:16")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true)
        );

        testHarness.open();

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-14T18:00:00")));

        for (TaxiEvent record : records) {
            testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
        }

        testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-14T21:00:55").plusMinutes(5)));

        var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

        ValueStateDescriptor<DemandSessionAccumulatorGlobal> stateDesc = new ValueStateDescriptor<>("sessionState",
                DemandSessionAccumulatorGlobal.class);

        var state = testHarness.getOperator().getKeyedStateStore().getState(stateDesc);

        Arrays.stream(output).iterator().forEachRemaining(ds -> ds.setSessionId("session_id"));

        fixOutputForTesting(output);

        System.out.println(Arrays.toString(output));
        System.out.println(state.value());

        // [DemandSessionRecord(phonePdId=phone_pd_id, utcSessionStartDttm=2021-09-14 18:02:02, sessionId=session_id,
        // appPlatformList=[ios], breakReason=success_order, durationH=0.0, firstEventLat=55.75, firstEventLon=37.61,
        // firstSuccessOrderAppPlatform=ios, firstSurgeValue=null, firstWaitingTimeSec=null, lastAppPlatform=ios,
        // lastEventLat=55.75, lastEventLon=37.61, lastOrderTariff=econom, lastSurgeValue=null,
        // lastTariffZone=moscow, lastWaitingTimeSec=null, multiorderFlg=false, offerCnt=0, offerList=[],
        // orderList=[2aa4d128bec5ddec94d2631dffce0cdc], pinCnt=0, pinList=[], pinWWaitTimeCnt=0, successOrderCnt=1,
        // userIdList=[A], utcSessionEndDttm=2021-09-14 18:02:02),
        //
        // DemandSessionRecord(phonePdId=phone_pd_id,
        // utcSessionStartDttm=2021-09-14 18:16:05, sessionId=session_id, appPlatformList=[ios],
        // breakReason=success_order, durationH=0.0, firstEventLat=55.75, firstEventLon=37.61,
        // firstSuccessOrderAppPlatform=ios, firstSurgeValue=null, firstWaitingTimeSec=null, lastAppPlatform=ios,
        // lastEventLat=55.75, lastEventLon=37.61, lastOrderTariff=econom, lastSurgeValue=null,
        // lastTariffZone=moscow, lastWaitingTimeSec=null, multiorderFlg=false, offerCnt=0, offerList=[],
        // orderList=[c2a0bff7f40dc811802939b5b6330954], pinCnt=0, pinList=[], pinWWaitTimeCnt=0, successOrderCnt=1,
        // userIdList=[A], utcSessionEndDttm=2021-09-14 18:16:05),
        //
        // DemandSessionRecord(phonePdId=phone_pd_id,
        // utcSessionStartDttm=2021-09-14 19:38:04, sessionId=session_id, appPlatformList=[ios], breakReason=timeout,
        // durationH=0.0, firstEventLat=55.75, firstEventLon=37.61, firstSuccessOrderAppPlatform=null,
        // firstSurgeValue=null, firstWaitingTimeSec=null, lastAppPlatform=ios, lastEventLat=55.75, lastEventLon=37
        // .61, lastOrderTariff=econom, lastSurgeValue=null, lastTariffZone=moscow, lastWaitingTimeSec=null,
        // multiorderFlg=false, offerCnt=0, offerList=[], orderList=[1575e507c1bf305aa52f334ce95968e2], pinCnt=0,
        // pinList=[], pinWWaitTimeCnt=0, successOrderCnt=0, userIdList=[A], utcSessionEndDttm=2021-09-14 19:38:04)]
    }

    /*
    * [order(id=1a75bc8aabca1d07b867b2fb3b472bd0, success=false, finished=false,updated=2021-10-18T13:04:08, created=1634550728000),
    * pin(id=e1add148cce5a3d28ce035539b0bc89a, ts=2021-10-18T12:52:16.693, isFake=false),
    * order(id=31dd9af9a6d335a28551eec78355b4cb, success=true, finished=true,updated=2021-10-18T13:53:34, created=1634550834000),
    * pin(id=593a1c7b334b9e076db948e389b14864, ts=2021-10-18T13:01:24.646, isFake=false),
    * order(id=8fb3fb03b86d1b97a61dcd4f466b42c8, success=true, finished=true,updated=2021-10-18T13:43:58, created=1634551321000),
    * pin(id=818d15b12709976d9b5e2c09d1be75e4, ts=2021-10-18T13:02:15.022, isFake=false)],
    *
    * */
    @Test
    void stuff4() throws Exception {
        // успешные события приходят после DemandSession.MAX_ORDER_WAIT_MILLIS
        for (var i = 0; i < 1; i++) {
            var testHarness = getTestHarness();

            var order0 = DEFAULT_ORDER
                    .withEventId("1a75bc8aabca1d07b867b2fb3b472bd0")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-10-18T13:04:08")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T12:52:08")));

            var pin0 = DEFAULT_PIN
                    .withEventId("e1add148cce5a3d28ce035539b0bc89a")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T12:52:16")));

            var order1 = DEFAULT_ORDER
                    .withEventId("31dd9af9a6d335a28551eec78355b4cb")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T12:53:54")));

            var pin1 = DEFAULT_PIN
                    .withEventId("593a1c7b334b9e076db948e389b14864")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T13:02:15")));

            var order2 = DEFAULT_ORDER
                    .withEventId("8fb3fb03b86d1b97a61dcd4f466b42c8")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T12:53:54")));

            var pin2 = DEFAULT_PIN
                    .withEventId("818d15b12709976d9b5e2c09d1be75e4")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-10-18T13:02:15")));


            var records = Arrays.asList(
                    order0,
                    order1,
                    order1.withUpdatedAt(ts(LocalDateTime.parse("2021-10-18T13:53:34")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true),
                    order2.withUpdatedAt(ts(LocalDateTime.parse("2021-10-18T13:02:01")))
                        .withSuccessOrderFlg(true)
                        .withFinishedOrderFlg(true),
                    pin0,
                    pin1,
                    pin2,
                    order0
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-10-18T13:31:10")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true)
            );

            testHarness.open();

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-10-18T11:00:00")));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp());
            }

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-10-18T14:27:00").plusMinutes(40)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

            System.out.println(Arrays.toString(output));
        }
    }


    @Disabled
    @Test
    void seriesOfOrdersSuccessfulMixedWithGap() throws Exception {
        // успешные события приходят после DemandSession.MAX_ORDER_WAIT_MILLIS
        for (var i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var order0 = DEFAULT_ORDER
                    .withEventId("60a3ef6abe79c73686496d7fded0d859")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:00:53")))
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:00:53")));

            var order1 = DEFAULT_ORDER
                    .withEventId("f0de04c7eb4f1905b08b2809bd5b4ed6")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:05:58")))
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:05:58")));

            var order2 = DEFAULT_ORDER
                    .withEventId("76ba7c0ce6acdf609b5824385834d3e6")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:15:01")))
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:15:01")));

            var records1 = Arrays.asList(
                    order0,
                    DEFAULT_PIN
                            .withEventId("124a66c66b756310a1e9f43a9782b1ef")
                            .withPinOrderId(order0.getEventId())
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:01:08"))),
                    order1,
                    DEFAULT_PIN
                            .withEventId("302a17fff7a34e66431fdaee8888c628")
                            .withPinOrderId(order1.getEventId())
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:10:18"))),
                    order2,
                    DEFAULT_PIN
                            .withEventId("10915d82dac6f549ff1444fe104f6aca")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:16:21")))
                            .withPinOrderId(order2.getEventId()),
                    DEFAULT_PIN
                            .withEventId("pin4")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:16:48")))
                            .withPinOrderId("fe9afdd8cf163ae78b9dbf7d83024601")
            );

            var records2 = Arrays.asList(
                    order0
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:20:55")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    DEFAULT_PIN
                            .withEventId("37d2b6b16cdaa4075641b9788a95292b")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:26:23"))),
                    order2
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:32:21")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    DEFAULT_PIN
                            .withEventId("434b0380a16fe2429b8e98f40b733f97")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:38:07"))),
                    order1
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:45:38")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true)
            );

            Collections.shuffle(records1);
            Collections.shuffle(records2);

            List<TaxiEvent> records = ListUtils.union(records1, records2);

            var eventIds = records.stream().map(e -> {
                String s;
                if (e.isOrder()) {
                    s = "Order(" + e.getEventId() + "=" + e.isFinishedOrder() + ")";
                } else if (e.isPin()) {
                    s = "Pin(" + e.getEventId() + ")";
                } else {
                    s = "Offer(" + e.getEventId() + ")";
                }
                return s;
            }).toArray();

            testHarness.open();

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-15T08:00:00")));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp());
            }

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-15T08:45:38").plusMinutes(10)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            fixOutputForTesting(output);

            assertArrayEquals(
                    new DemandSessionRecord[]{
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("60a3ef6abe79c73686496d7fded0d859"))
                                    .withDurationH(15.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withOfferCnt(0)
                                    .withPinCnt(1)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withPinList(List.of("124a66c66b756310a1e9f43a9782b1ef"))
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:00:53")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:00:53")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:01:08"))),
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("f0de04c7eb4f1905b08b2809bd5b4ed6"))
                                    .withDurationH(260.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withOfferCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withPinList(List.of("302a17fff7a34e66431fdaee8888c628"))
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:05:58")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:05:58")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:10:18"))),
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("76ba7c0ce6acdf609b5824385834d3e6"))
                                    .withDurationH(80.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withOfferCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withPinList(List.of("10915d82dac6f549ff1444fe104f6aca"))
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:15:01")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:15:01")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:16:21")))
                    },
                    output
            );
        }
    }

    @SuppressWarnings("checkstyle:MethodLength")
    @Test
    void seriesOfOrdersSuccessfulMixedWithoutGap() throws Exception {
        // все события происхоят в интервале DemandSession.MAX_ORDER_WAIT_MILLIS
        for (var i = 0; i < 100; i++) {
            var testHarness = getTestHarness();

            var order1 = DEFAULT_ORDER
                    .withEventId("order1")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:00:53")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:00:53")));

            var order2 = DEFAULT_ORDER
                    .withEventId("order2")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:03:58")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:03:58")));

            var order3 = DEFAULT_ORDER
                    .withEventId("order3")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:01")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:01")));

            var order4 = DEFAULT_ORDER
                    .withEventId("order4")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:01")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:01")))
                    .withMultiorderFlg(true);

            var order5 = DEFAULT_ORDER
                    .withEventId("order5")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:30")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:30")))
                    .withMultiorderFlg(true);

            var order6 = DEFAULT_ORDER
                    .withEventId("order6")
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:40")))
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:40")));

            var records = Arrays.asList(
                    order2,
                    order3,
                    order4,
                    order5,
                    order6,
                    order3
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:56")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    DEFAULT_PIN
                            .withEventId("pin1")
                            .withPinOrderId(order1.getEventId())
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:01:08"))),
                    order2
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:47")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    DEFAULT_PIN
                            .withEventId("pin4")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:48")))
                            .withPinOrderId(order3.getEventId()),
                    DEFAULT_PIN
                            .withEventId("pin2")
                            .withPinOrderId(order2.getEventId())
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:03:59"))),
                    order1
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:04:55")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    order1,
                    DEFAULT_PIN
                            .withEventId("pin3")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:03:21"))),
                    DEFAULT_PIN // late pin
                            .withEventId("pin5")
                            .withCreatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:02"))),
                    order4
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:45")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true),
                    order5
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:43")))
                            .withFinishedOrderFlg(true),
                    order6
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-09-15T08:02:43")))
                            .withFinishedOrderFlg(true)
                            .withSuccessOrderFlg(true)
            );

            testHarness.open();

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-15T08:00:00").minusMinutes(10)));

            for (TaxiEvent record : records) {
                testHarness.processElement(new StreamRecord<>(record, record.getEventTimestamp()));
                testHarness.processWatermark(record.getEventTimestamp() - 10 * 60 * 1000);
            }

            testHarness.processWatermark(ts(LocalDateTime.parse("2021-09-15T08:45:38").plusMinutes(15)));

            var output = testHarness.extractOutputValues().toArray(DemandSessionRecord[]::new);

            Arrays.stream(output).iterator().forEachRemaining(ds -> {
                ds.setSessionId("session_id");
                ds.setLastEventTs(0);
            });

            fixOutputForTesting(output);

            assertArrayEquals(
                    new DemandSessionRecord[]{
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("order1"))
                                    .withDurationH(15.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withOfferCnt(0)
                                    .withPinCnt(1)
                                    .withPinList(List.of("pin1"))
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:00:53")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:00:53")
                                            .plusHours(3)))
                                    .withShownAltofferList(Collections.emptyList())
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:01:08"))),
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("order4", "order5", "order6"))
                                    .withDurationH(39.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withPinList(List.of("pin5"))
                                    .withSuccessOrderCnt(2)
                                    .withOfferCnt(0)
                                    .withMultiorderFlg(true)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:02:01")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:02:01")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:02:40"))),
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("order2"))
                                    .withDurationH(38.0 / 3600)
                                    .withOfferList(Collections.emptyList())
                                    .withPinCnt(2)
                                    .withPinList(List.of("pin2", "pin3"))
                                    .withPinWWaitTimeCnt(2)
                                    .withOfferCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:03:21")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:03:21")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:03:59"))),
                            DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                                    .withOrderList(List.of("order3"))
                                    .withDurationH(47.0 / 3600)
                                    .withOfferCnt(0)
                                    .withPinList(List.of("pin4"))
                                    .withOfferList(Collections.emptyList())
                                    .withShownAltofferList(Collections.emptyList())
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:04:01")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-15T08:04:01")
                                            .plusHours(3)))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-15T08:04:48")))
                    },
                    output
            );
        }
    }
}
