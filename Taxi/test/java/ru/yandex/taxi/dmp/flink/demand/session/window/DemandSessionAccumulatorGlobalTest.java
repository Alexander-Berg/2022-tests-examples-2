package ru.yandex.taxi.dmp.flink.demand.session.window;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.junit.Ignore;
import org.junit.jupiter.api.Test;
import org.opentest4j.AssertionFailedError;

import ru.yandex.taxi.dmp.flink.demand.session.model.DemandSessionRecord;
import ru.yandex.taxi.dmp.flink.demand.session.model.SessionBreakReason;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_OFFER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_PIN;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.START_DT;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.str;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.ts;

class DemandSessionAccumulatorGlobalTest {

    @Test
    void accumulatorWithUnfinishedSessionReturnsNull() {
        var acc = new DemandSessionAccumulatorGlobal();

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));

        var session = acc.getResult(ts(START_DT.plusMinutes(2)));

        assertNull(session);
    }

    @Test
    void accumulatorWithFinishedSessionReturnsNullWhenFinishedOrderButTimeLessThanGap() {
        var acc = new DemandSessionAccumulatorGlobal();

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(3))).withSuccessOrderFlg(true)
                .withFinishedOrderFlg(true));

        var session = acc.getResult(ts(START_DT.plusMinutes(2)));

        assertNull(session);
    }

    @Test
    void accumulatorWithFinishedSession() {
        var acc = new DemandSessionAccumulatorGlobal();

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(DEFAULT_ORDER
                .withCreatedAt(ts(START_DT.plusMinutes(2)))
                .withUpdatedAt(ts(START_DT.plusMinutes(3)))
                .withSuccessOrderFlg(true)
                .withFinishedOrderFlg(true));

        var session = acc.getResult(ts(START_DT.plusMinutes(16))).withSessionId(DEFAULT_SESSION.getSessionId());
        var expectedSession = DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                .withDurationH(2.0 / 60)
                .withUtcDt("2021-03-29")
                .withLastEventTs(ts(START_DT.plusMinutes(3)))
                .withUtcSessionEndDttm(str(START_DT.plusMinutes(2)));

        assertEquals(expectedSession, session);
    }

    @SuppressWarnings("checkstyle:LineLength")
    @Test
    void accumulatorWithFinishedSessionMultipleOrders() {
        var acc = new DemandSessionAccumulatorGlobal();

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(DEFAULT_PIN
                .withEventId("pin2")
                .withCreatedAt(ts(START_DT.plusMinutes(3))));
        acc.add(DEFAULT_ORDER
                .withEventId("order2")
                .withCreatedAt(ts(START_DT.plusMinutes(4))));
        acc.add(DEFAULT_PIN
                .withEventId("pin3")
                .withCreatedAt(ts(START_DT.plusMinutes(5))));
        acc.add(DEFAULT_ORDER
                .withCreatedAt(ts(START_DT.plusMinutes(2)))
                .withUpdatedAt(ts(START_DT.plusMinutes(7)))
                .withSuccessOrderFlg(true)
                .withFinishedOrderFlg(true));

        var session1 = acc.getResult(ts(START_DT.plusMinutes(DemandSession.TIMEOUT_MILLIS)))
                .withSessionId("session_id");
        // завершенная сессия должна вернуться, а незавершенная остаться
        var expectedSession1 = DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                .withDurationH(2.0 / 60)
                .withUtcDt("2021-03-29")
                .withLastEventTs(ts(START_DT.plusMinutes(7)))
                .withUtcSessionEndDttm(str(START_DT.plusMinutes(2)));

        assertEquals(expectedSession1, session1);

        acc.add(DEFAULT_ORDER
                .withEventId("order2")
                .withCreatedAt(ts(START_DT.plusMinutes(4)))
                .withUpdatedAt(ts(START_DT.plusMinutes(6)))
                .withSuccessOrderFlg(true)
                .withFinishedOrderFlg(true));

        var session2 = acc.getResult(ts(START_DT.plusMinutes(67))).withSessionId("session_id");
        var expectedSession2 = DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER
                .withDurationH(1.0 / 60)
                .withOfferList(Collections.emptyList())
                .withOfferCnt(0)
                .withOrderList(List.of("order2"))
                .withPinList(List.of("pin2"))
                .withUtcDt("2021-03-29")
                .withShownAltofferList(Collections.emptyList())
                .withLastEventTs(ts(START_DT.plusMinutes(6)))
                .withUtcSessionStartDttm(str(START_DT.plusMinutes(3)))
                .withLocalSessionStartDttm(str(START_DT.plusMinutes(3).plusHours(3)))
                .withUtcSessionEndDttm(str(START_DT.plusMinutes(4)));

        assertEquals(expectedSession2, session2);

        var session3events = acc.getSessions().get(0).getEvents();
        var expectedSession3Events = List.of(DEFAULT_PIN
                .withEventId("pin3")
                .withCreatedAt(ts(START_DT.plusMinutes(5))));

        assertEquals(expectedSession3Events, session3events);
    }

    @Test
    void aggregate2() {
        var acc = new DemandSessionAccumulator(SessionBreakReason.TIMEOUT);

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(
                DEFAULT_ORDER
                        .withCreatedAt(ts(START_DT.plusMinutes(2)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(3)))
                        .withSuccessOrderFlg(true)
                        .withApplication("android")
        );

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(2)))
                        .withDurationH(2.0 / 60)
                        .withUtcDt("2021-03-29")
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(1)
                        .withLastEventTs(ts(START_DT.plusMinutes(3)))
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        );
    }

    @Test
    void sessionsWithOnePinBreakByDistance() {
        var acc = new DemandSessionAccumulatorGlobal();

        acc.add(DEFAULT_PIN.withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                .withCreatedAt(1631837143185L));
        acc.add(DEFAULT_PIN.withEventId("pin2").withSourceLat(43.23695424731923).withSourceLon(76.88867853532702)
                .withCreatedAt(1631837143318L));

        var result = new ArrayList<DemandSessionRecord>(2);
        var s = acc.getResult(1631837143318L + 30 * 60 * 1000);

        while (s != null) {
            result.add(s);
            s = acc.getResult(1631837143318L + 30 * 60 * 1000);
        }

        // System.out.println(result);

        // [DemandSessionRecord(phonePdId=phone_pd_id, utcSessionStartDttm=2021-09-17 00:05:43,
        // sessionId=1c3b73d4d1bd9b1e480b80e93c81eeb5, appPlatformList=[ios], breakReason=timeout,
        // displacedSessionFlg=false, durationH=0.0, firstEventLat=43.26429147166759, firstEventLon=76
        // .93953105680157, firstSuccessOrderAppPlatform=null, firstSurgeValue=1.0, firstWaitingTimeSec=123.0,
        // lastAppPlatform=ios, lastEventLat=43.23695424731923, lastEventLon=76.88867853532702, lastOrderTariff=null,
        // lastSurgeValue=1.0, lastTariffZone=moscow, lastWaitingTimeSec=123.0, localSessionStartDttm=2021-09-17
        // 03:05:43, multiorderFlg=false, offerCnt=0, offerList=[], orderList=[], pinCnt=2, pinList=[pin2, pin_id],
        // pinWWaitTimeCnt=2, shownAltofferList=[], successOrderCnt=0, userIdList=[A], utcSessionEndDttm=2021-09-17
        // 00:05:43, utcDt=2021-09-17, lastEventTs=1631837143318)]

        /*assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(3)))
                        .withDurationH(3.0 / 60)
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(1)
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        ); */
    }

    @Test
    void eventsShouldNotBreakByDistanceWithinSameSecond() {
        for (var i = 0; i < 100; i++) {
            var events = new ArrayList<>(List.of(
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34")))
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34")) + 10)
                            .withEventId("pin2")
                            .withSourceLat(43.23695424731923).withSourceLon(76.88867853532702),
                    DEFAULT_OFFER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34")) + 15)
                            .withSourceLat(43.23695424731923).withSourceLon(76.88867853532702),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34"))).withEventId("pin3")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
            ));

             Collections.shuffle(events);

            var acc = new DemandSessionAccumulatorGlobal();

            System.out.println("EVENTS: " + events);

            events.forEach(acc::add);

            var s = acc.getResult(ts(LocalDateTime.parse("2021-10-02T19:44:23").plusMinutes(10)))
                    .withSessionId("session_id");

            assertEquals(DEFAULT_SESSION
                            .withSessionId("session_id")
                            .withUtcSessionStartDttm("2021-10-02 19:19:34")
                            .withUtcSessionEndDttm("2021-10-02 19:19:34")
                            .withFirstEventLat(43.26429147166759)
                            .withFirstEventLon(76.93953105680157)
                            .withLastEventLat(43.23695424731923)
                            .withLastEventLon(76.88867853532702)
                            .withBreakReason("timeout")
                            .withDurationH(0)
                            .withFirstSuccessOrderAppPlatform(null)
                            .withLocalSessionStartDttm("2021-10-02 22:19:34")
                            .withOfferCnt(1)
                            .withLastOrderTariff(null)
                            .withOfferList(List.of("offer_id"))
                            .withPinList(List.of("pin2", "pin3", "pin_id"))
                            .withOrderList(Collections.emptyList())
                            .withShownAltofferList(List.of("offer_id"))
                            .withSuccessOrderCnt(0)
                            .withPinWWaitTimeCnt(3)
                            .withPinCnt(3)
                            .withUtcDt("2021-10-02")
                            .withLastEventTs(1633202374015L),
                    s);
        }
    }

    @Test
    @Ignore
    void eventsWithSameTsShouldBeInTheSameSession() {
        for (var i = 0; i < 100; i++) {
            var events = new ArrayList<>(List.of(
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34")))
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:34")) + 10)
                            .withEventId("pin2")
                            .withSourceLat(43.23695424731923).withSourceLon(76.88867853532702),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:36"))).withEventId("pin3")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:47"))).withEventId("pin4")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:51"))).withEventId("pin5")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:19:56"))).withEventId("pin6")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_ORDER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:04"))),
                    DEFAULT_ORDER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:18"))),
                    DEFAULT_ORDER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                            .withUpdatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:20"))),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                            .withEventId("pin7").withPinOrderId("order_id")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157),
                    DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:18")))
                            .withEventId("pin8").withPinOrderId("order_id")
                            .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
            ));

            //Collections.shuffle(events);

            //System.out.println("events: " + events);

            var acc = new DemandSessionAccumulatorGlobal();

            events.forEach(acc::add);

            acc.add(DEFAULT_ORDER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-10-02T19:44:23")))
                    .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                    .withSuccessOrderFlg(true)
                    .withFinishedOrderFlg(true));
            acc.add(DEFAULT_ORDER.withCreatedAt(ts(LocalDateTime.parse("2021-10-02T19:20:03")))
                    .withSourceLat(43.26429147166759).withSourceLon(76.93953105680157)
                    .withUpdatedAt(ts(LocalDateTime.parse("2021-10-02T19:44:23")))
                    .withSuccessOrderFlg(true)
                    .withFinishedOrderFlg(true));

            var s = acc.getResult(ts(LocalDateTime.parse("2021-10-02T19:44:23").plusMinutes(10)))
                    .withSessionId("session_id");

            try {

                assertEquals(DEFAULT_SESSION
                                .withSessionId("session_id")
                                .withUtcSessionStartDttm("2021-10-02 19:19:34")
                                .withUtcSessionEndDttm("2021-10-02 19:20:18")
                                .withFirstEventLat(43.26429147166759)
                                .withFirstEventLon(76.93953105680157)
                                .withLastEventLat(43.26429147166759)
                                .withLastEventLon(76.93953105680157)
                                .withBreakReason("success_order")
                                .withDurationH(44.0 / 3600)
                                .withFirstSuccessOrderAppPlatform("ios")
                                .withLocalSessionStartDttm("2021-10-02 22:19:34")
                                .withOfferCnt(0)
                                .withOfferList(Collections.emptyList())
                                .withPinList(List.of("pin2", "pin3", "pin4", "pin5", "pin6", "pin7", "pin8", "pin_id"))
                                .withShownAltofferList(Collections.emptyList())
                                .withSuccessOrderCnt(1)
                                .withPinWWaitTimeCnt(8)
                                .withPinCnt(8)
                                .withUtcDt("2021-10-02")
                                .withLastEventTs(1633203863000L),
                        s);
            } catch (AssertionFailedError e) {
                System.out.println(events);
                throw e;
            }

            assertNull(acc.getResult(ts(LocalDateTime.parse("2021-10-02T19:44:23").plusMinutes(10))));

            // System.out.println(s);
        }

        /*assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(3)))
                        .withDurationH(3.0 / 60)
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(1)
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        ); */
    }

    @Test
    void sessionsWithUnfinishedOrderShouldNotBreak() {
        var acc = new DemandSessionAccumulatorGlobal();
        var order0 = DEFAULT_ORDER
                .withEventId("a218657154aed13ea0c6fa36e091e9e5")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:04")));

        var order1 = DEFAULT_ORDER
                .withEventId("ef878a6d25151db4a2f3796e73f95fd1")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:42")));

        // acc.add(DEFAULT_PIN.withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:31:41"))));
        acc.add(DEFAULT_PIN.withEventId("pin2").withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:31:46"))));
        acc.add(DEFAULT_PIN.withEventId("pin3").withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:01"))));
        acc.add(order0);
        acc.add(DEFAULT_PIN.withEventId("pin4")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:05")))
                .withPinOrderId("a218657154aed13ea0c6fa36e091e9e5")
        );
        acc.add(order0
                .withUpdatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:20")))
                .withSuccessOrderFlg(false)
                .withFinishedOrderFlg(true)
        );
        acc.add(order1);
        acc.add(DEFAULT_PIN.withEventId("pin6")
                .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:33:57")))
                .withPinOrderId("ef878a6d25151db4a2f3796e73f95fd1")
        );
        acc.add(order1
                .withUpdatedAt(ts(LocalDateTime.parse("2021-09-17T10:31:45")))
                .withSuccessOrderFlg(true)
                .withFinishedOrderFlg(true)
        );
        acc.add(DEFAULT_PIN.withEventId("pin5").withCreatedAt(ts(LocalDateTime.parse("2021-09-17T09:32:24"))));

        var result = new ArrayList<DemandSessionRecord>(2);
        var s = acc.getResult(ts(LocalDateTime.parse("2021-09-17T10:31:45").plusMinutes(10)));

        while (s != null) {
            result.add(s);
            s = acc.getResult(ts(LocalDateTime.parse("2021-09-17T10:31:45").plusMinutes(10)));
        }

        // System.out.println(result);
        // System.out.println(acc.getSessions());

        /*assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(3)))
                        .withDurationH(3.0 / 60)
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(1)
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        ); */
    }

    @Test
    void sessionsWithUnfinishedOrderShouldNotBreak2() {
        for (var i = 0; i < 100; i++) {
            var acc = new DemandSessionAccumulatorGlobal();
            var order0 = DEFAULT_ORDER
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T08:29:56")));

            var order1 = DEFAULT_ORDER
                    .withEventId("order2")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-17T08:29:57")));

            var events = new ArrayList<>(List.of(
                    order0,
                    order1,
                    order1.withUpdatedAt(ts(LocalDateTime.parse("2021-09-17T10:45:13")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true),
                    order0.withUpdatedAt(ts(LocalDateTime.parse("2021-09-17T10:08:45")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true)
            ));

            Collections.shuffle(events);

            events.forEach(acc::add);

            var result = new DemandSessionRecord[2];
            var j = 0;
            var s = acc.getResult(ts(LocalDateTime.parse("2021-09-17T10:45:13").plusMinutes(5)));

            while (s != null) {
                s.setSessionId("session_id");
                result[j] = s;
                s = acc.getResult(ts(LocalDateTime.parse("2021-09-17T10:45:13").plusMinutes(5)));
                j++;
            }

            Arrays.stream(result).forEach(ds -> ds.setLocalSessionStartDttm(ds.getUtcSessionStartDttm()));

            assertArrayEquals(new DemandSessionRecord[]{
                            DEFAULT_SESSION
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:56")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:56")))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-17T08:29:56")))
                                    .withDurationH(0)
                                    .withUtcDt("2021-09-17")
                                    .withFirstSuccessOrderAppPlatform("ios")
                                    .withFirstSurgeValue(null)
                                    .withFirstWaitingTimeSec(null)
                                    .withLastSurgeValue(null)
                                    .withLastWaitingTimeSec(null)
                                    .withSuccessOrderCnt(1)
                                    .withPinList(Collections.emptyList())
                                    .withOfferCnt(0)
                                    .withPinWWaitTimeCnt(0)
                                    .withPinCnt(0)
                                    .withShownAltofferList(Collections.emptyList())
                                    .withLastEventTs(ts(LocalDateTime.parse("2021-09-17T10:08:45")))
                                    .withOfferList(Collections.emptyList())
                                    .withBreakReason("success_order"),
                            DEFAULT_SESSION
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:57")))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-17T08:29:57")))
                                    .withLocalSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:57")))
                                    .withDurationH(0)
                                    .withUtcDt("2021-09-17")
                                    .withShownAltofferList(Collections.emptyList())
                                    .withFirstSuccessOrderAppPlatform("ios")
                                    .withLastSurgeValue(null)
                                    .withFirstWaitingTimeSec(null)
                                    .withLastWaitingTimeSec(null)
                                    .withSuccessOrderCnt(1)
                                    .withPinList(Collections.emptyList())
                                    .withPinCnt(0)
                                    .withPinWWaitTimeCnt(0)
                                    .withOfferCnt(0)
                                    .withLastEventTs(ts(LocalDateTime.parse("2021-09-17T10:45:13")))
                                    .withOrderList(List.of("order2"))
                                    .withOfferList(Collections.emptyList())
                                    .withFirstSurgeValue(null)
                                    .withBreakReason("success_order"),
                    },
                    result
            );
        }
    }

    @Test
    void sessionsWithUnfinishedOrderShouldNotBreak3() {
        for (var i = 0; i < 100; i++) {
            var acc = new DemandSessionAccumulatorGlobal();
            var order0 = DEFAULT_ORDER
                    .withEventId("496a901dfdf9cddf85542e660907baa8")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-21T06:14:16")));

            var order1 = DEFAULT_ORDER
                    .withEventId("9fa6653a6ab3df8095480921b2447299")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-21T06:06:01")));

            var order2 = DEFAULT_ORDER
                    .withEventId("9fa6653a6ab3df8095480921b2447299")
                    .withCreatedAt(ts(LocalDateTime.parse("2021-09-21T06:22:16")));

            var events = new ArrayList<>(List.of(
                    order0,
                    order1,
                    order2,
                    order0.withUpdatedAt(ts(LocalDateTime.parse("2021-09-21T10:42:42")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true),
                    order1.withUpdatedAt(ts(LocalDateTime.parse("2021-09-21T08:09:25")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true),
                    order2.withUpdatedAt(ts(LocalDateTime.parse("2021-09-21T07:28:20")))
                            .withSuccessOrderFlg(true)
                            .withFinishedOrderFlg(true)
            ));

            Collections.shuffle(events);

            events.forEach(acc::add);

            var result = new DemandSessionRecord[10];
            var j = 0;
            var s = acc.getResult(ts(LocalDateTime.parse("2021-09-21T10:42:42").plusMinutes(5)));

            while (s != null) {
                s.setSessionId("session_id");
                result[j] = s;
                s = acc.getResult(ts(LocalDateTime.parse("2021-09-21T10:42:42").plusMinutes(5)));
                j++;
            }

            // System.out.println(Arrays.toString(result));

            /*assertArrayEquals(new DemandSessionRecord[] {
                            DEFAULT_SESSION
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:56")))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-17T08:29:56")))
                                    .withDurationH(0)
                                    .withFirstSuccessOrderAppPlatform("ios")
                                    .withFirstSurgeValue(null)
                                    .withFirstWaitingTimeSec(null)
                                    .withLastSurgeValue(null)
                                    .withLastWaitingTimeSec(null)
                                    .withSuccessOrderCnt(1)
                                    .withOfferCnt(0)
                                    .withPinWWaitTimeCnt(0)
                                    .withPinCnt(0)
                                    .withOfferList(Collections.emptyList())
                                    .withBreakReason("success_order"),
                            DEFAULT_SESSION
                                    .withUtcSessionStartDttm(str(LocalDateTime.parse("2021-09-17T08:29:57")))
                                    .withUtcSessionEndDttm(str(LocalDateTime.parse("2021-09-17T08:29:57")))
                                    .withDurationH(0)
                                    .withFirstSuccessOrderAppPlatform("ios")
                                    .withLastSurgeValue(null)
                                    .withFirstWaitingTimeSec(null)
                                    .withLastWaitingTimeSec(null)
                                    .withSuccessOrderCnt(1)
                                    .withPinCnt(0)
                                    .withPinWWaitTimeCnt(0)
                                    .withOfferCnt(0)
                                    .withOrderList(List.of("order2"))
                                    .withOfferList(Collections.emptyList())
                                    .withFirstSurgeValue(null)
                                    .withBreakReason("success_order"),
                    },
                    result
            ); */
        }
    }

    @Test
    void aggregate3() {
        var acc = new DemandSessionAccumulator(SessionBreakReason.TIMEOUT);

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(2)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(2)))
        );
        acc.add(
                DEFAULT_ORDER
                        .withCreatedAt(ts(START_DT.plusMinutes(3)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(3)))
                        .withSuccessOrderFlg(true)
                        .withApplication("android")
        );
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(4)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(4)))
                        .withSuccessOrderFlg(true)
        );

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(4)))
                        .withDurationH(4.0 / 60)
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("ios")
                        .withSuccessOrderCnt(2)
                        .withUtcDt("2021-03-29")
                        .withOrderList(Arrays.asList("order_id", "order_id_2"))
                        .withLastEventTs(ts(START_DT.plusMinutes(4)))
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        );
    }

    @Test
    void aggregate4() {
        var acc = new DemandSessionAccumulator(SessionBreakReason.TIMEOUT);

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))));
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(2)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(2)))
        );
        acc.add(
                DEFAULT_ORDER
                        .withCreatedAt(ts(START_DT.plusMinutes(3)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(3)))
                        .withSuccessOrderFlg(true)
                        .withApplication("android")
        );
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(4)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(4)))
                        .withSuccessOrderFlg(true)
        );

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(4)))
                        .withLastEventTs(ts(START_DT.plusMinutes(4)))
                        .withDurationH(4.0 / 60)
                        .withUtcDt("2021-03-29")
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("ios")
                        .withSuccessOrderCnt(2)
                        .withOrderList(Arrays.asList("order_id", "order_id_2"))
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        );
    }
}
