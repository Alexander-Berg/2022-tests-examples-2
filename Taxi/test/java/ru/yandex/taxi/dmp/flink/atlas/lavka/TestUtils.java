package ru.yandex.taxi.dmp.flink.atlas.lavka;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

import ru.yandex.taxi.dmp.flink.atlas.lavka.model.Offer;
import ru.yandex.taxi.dmp.flink.atlas.lavka.model.Order;
import ru.yandex.taxi.dmp.flink.utils.DateTimeUtils;

public class TestUtils {
    public static final LocalDateTime START_DT = LocalDateTime.parse("2021-12-22T13:00:00");

    public static final Offer OFFER_1 = Offer.builder()
            .offerId("aaa")
            .activeZone("moscow")
            .depotId("1")
            .lat(59.83824943833668)
            .lon(30.114438865206907)
            .isSurge(false)
            .isManual(false)
            .isShown(false)
            .deliveryCostArray(new double[]{})
            .orderCostArray(new double[]{})
            .createdAt(ts(START_DT))
            .updatedAt(ts(START_DT))
            .build();

    public static final Order ORDER_1 = Order.builder()
            .orderId("order1")
            .offerId("aaa")
            .status("delivered")
            .lat(59.83824943833668)
            .lon(30.114438865206907)
            .depotId("1")
            .regionId(1)
            .eatsUserId("eatsId")
            .taxiUserId("taxiId")
            .phonePdId("phonePdId")
            .createdAt(ts(START_DT))
            .updatedAt(ts(START_DT))
            .build();

    private TestUtils() {
    }

    public static long ts(LocalDateTime dt) {
        return dt.toInstant(ZoneOffset.UTC).toEpochMilli();
    }

    public static String str(LocalDateTime dt) {
        return DateTimeUtils.DATE_TIME.format(dt);
    }
}
