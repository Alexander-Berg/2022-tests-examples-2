package ru.yandex.taxi.dmp.flink.demand.session.window;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Collections;
import java.util.List;

import ru.yandex.taxi.dmp.flink.demand.session.model.DemandSessionRecord;
import ru.yandex.taxi.dmp.flink.demand.session.model.Offer;
import ru.yandex.taxi.dmp.flink.demand.session.model.Order;
import ru.yandex.taxi.dmp.flink.demand.session.model.Pin;
import ru.yandex.taxi.dmp.flink.demand.session.model.SessionBreakReason;
import ru.yandex.taxi.dmp.flink.demand.session.model.internal.Point;
import ru.yandex.taxi.dmp.flink.utils.DateTimeUtils;

public class DemandSessionTestUtils {
    public static final LocalDateTime START_DT = LocalDateTime.parse("2021-03-29T00:00:00");
    public static final Point SOME_POINT = new Point(37.61, 55.75);
    public static final Point OTHER_POINT = new Point(30.30, 59.93);
    public static final String USER_ID = "A";
    public static final String PHONE_PD_ID = "phone_pd_id";
    public static final Pin DEFAULT_PIN;
    public static final Offer DEFAULT_OFFER;
    public static final Order DEFAULT_ORDER;
    public static final DemandSessionRecord DEFAULT_SESSION = new DemandSessionRecord(
            "phone_pd_id",
            str(START_DT),
            "session_id",
            Collections.singletonList("ios"),
            "timeout",
            false,
            1.1,
            55.75,
            37.61,
            null,
            1.0,
            123.0,
            "ios",
            55.75,
            37.61,
            "econom",
            1.0,
            "moscow",
            123.0,
            str(START_DT.plusHours(3)),
            false,
            1,
            Collections.singletonList("offer_id"),
            Collections.singletonList("order_id"),
            1,
            Collections.singletonList("pin_id"),
            1,
            Collections.singletonList("offer_id"),
            0,
            Collections.singletonList("A"),
            str(START_DT),
            "2021-03-29",
            0
    );
    public static final DemandSessionRecord DEFAULT_SESSION_WITHOUT_ORDER = DEFAULT_SESSION
            .withAppPlatformList(Collections.singletonList("ios"))
            .withLastAppPlatform("ios")
            .withLastOrderTariff(null)
            .withOrderList(Collections.emptyList());

    public static final DemandSessionRecord DEFAULT_SESSION_WITH_SUCCESSFUL_ORDER = DEFAULT_SESSION
            .withAppPlatformList(Collections.singletonList("ios"))
            .withFirstSuccessOrderAppPlatform("ios")
            .withBreakReason(SessionBreakReason.SUCCESS_ORDER.getName())
            .withLastAppPlatform("ios")
            .withLastOrderTariff("econom")
            .withSuccessOrderCnt(1)
            .withOrderList(List.of("order_id"));

    static {
        DEFAULT_PIN = new Pin(USER_ID, "pin_id", PHONE_PD_ID, ts(START_DT), SOME_POINT.getLon(),
                SOME_POINT.getLat(), "moscow", "offer_id", "altpin_offer_id", null, 123.0, 1.0, false);
        DEFAULT_PIN.setApplication("ios");
        DEFAULT_PIN.setUserApplicationPlatform("ios");

        DEFAULT_ORDER = new Order(USER_ID, "order_id", ts(START_DT), SOME_POINT.getLon(), SOME_POINT.getLat(),

                "moscow", ts(START_DT), false, false, false, "econom", "econom", "ios", USER_ID, PHONE_PD_ID);

        DEFAULT_OFFER = new Offer(USER_ID, "offer_id", ts(START_DT), SOME_POINT.getLon(), SOME_POINT.getLat());
        DEFAULT_OFFER.setPhonePdId(PHONE_PD_ID);
        DEFAULT_OFFER.setApplication("ios");
        DEFAULT_OFFER.setUserApplicationPlatform("ios");
    }

    private DemandSessionTestUtils() {
    }

    public static long ts(LocalDateTime dt) {
        return dt.toInstant(ZoneOffset.UTC).toEpochMilli();
    }

    public static String str(LocalDateTime dt) {
        return DateTimeUtils.DATE_TIME.format(dt);
    }
}
