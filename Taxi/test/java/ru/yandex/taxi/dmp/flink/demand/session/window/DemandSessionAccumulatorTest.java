package ru.yandex.taxi.dmp.flink.demand.session.window;

import java.util.Arrays;

import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.demand.session.model.SessionBreakReason;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_OFFER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_ORDER;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_PIN;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.DEFAULT_SESSION;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.START_DT;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.str;
import static ru.yandex.taxi.dmp.flink.demand.session.window.DemandSessionTestUtils.ts;

class DemandSessionAccumulatorTest {

    @Test
    void aggregate() {
        var acc = new DemandSessionAccumulator(SessionBreakReason.TIMEOUT);

        acc.add(DEFAULT_PIN);
        acc.add(DEFAULT_OFFER.withCreatedAt(ts(START_DT.plusMinutes(1))));
        acc.add(DEFAULT_ORDER.withCreatedAt(ts(START_DT.plusMinutes(2))).withUpdatedAt(ts(START_DT.plusMinutes(2))));

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(2)))
                        .withLastEventTs(ts(START_DT.plusMinutes(2)))
                        .withUtcDt("2021-03-29")
                        .withDurationH(2.0 / 60),
                acc.getResult().withSessionId("session_id")
        );
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
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(1)
                        .withLastEventTs(ts(START_DT.plusMinutes(3)))
                        .withBreakReason("success_order")
                        .withUtcDt("2021-03-29"),
                acc.getResult().withSessionId("session_id")
        );
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
        );
        acc.add(
                DEFAULT_ORDER
                        .withCreatedAt(ts(START_DT.plusMinutes(2)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(3)))
                        .withSuccessOrderFlg(true)
                        .withApplication("android")
        );
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(4)))
                        .withSuccessOrderFlg(true)
        );

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(4)))
                        .withLastEventTs(ts(START_DT.plusMinutes(3)))
                        .withDurationH(4.0 / 60)
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("android")
                        .withSuccessOrderCnt(2)
                        .withOrderList(Arrays.asList("order_id", "order_id_2"))
                        .withBreakReason("success_order")
                        .withUtcDt("2021-03-29"),
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
        );
        acc.add(
                DEFAULT_ORDER
                        .withCreatedAt(ts(START_DT.plusMinutes(3)))
                        .withSuccessOrderFlg(true)
                        .withApplication("android")
        );
        acc.add(
                DEFAULT_ORDER
                        .withEventId("order_id_2")
                        .withCreatedAt(ts(START_DT.plusMinutes(3)))
                        .withUpdatedAt(ts(START_DT.plusMinutes(4)))
                        .withSuccessOrderFlg(true)
        );

        assertEquals(
                DEFAULT_SESSION
                        .withUtcSessionEndDttm(str(START_DT.plusMinutes(3)))
                        .withDurationH(3.0 / 60)
                        .withLastEventTs(ts(START_DT.plusMinutes(4)))
                        .withAppPlatformList(Arrays.asList("android", "ios"))
                        .withFirstSuccessOrderAppPlatform("android")
                        .withLastAppPlatform("ios")
                        .withSuccessOrderCnt(2)
                        .withUtcDt("2021-03-29")
                        .withOrderList(Arrays.asList("order_id", "order_id_2"))
                        .withBreakReason("success_order"),
                acc.getResult().withSessionId("session_id")
        );
    }
}
