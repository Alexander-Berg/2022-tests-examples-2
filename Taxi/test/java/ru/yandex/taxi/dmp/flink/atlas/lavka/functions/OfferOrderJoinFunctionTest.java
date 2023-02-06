package ru.yandex.taxi.dmp.flink.atlas.lavka.functions;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Collections;
import java.util.List;

import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.operators.co.KeyedCoProcessOperator;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.KeyedTwoInputStreamOperatorTestHarness;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.atlas.lavka.model.ChEnrichedOffer;
import ru.yandex.taxi.dmp.flink.atlas.lavka.model.Offer;
import ru.yandex.taxi.dmp.flink.atlas.lavka.model.Order;
import ru.yandex.taxi.dmp.flink.utils.geo.Quadkey;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.OFFER_1;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.ORDER_1;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.START_DT;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.ts;

public class OfferOrderJoinFunctionTest {

    private KeyedTwoInputStreamOperatorTestHarness<String, Offer, Order, ChEnrichedOffer> testHarness;

    private static final Duration STATE_TTL = Duration.ofHours(1);

    @BeforeEach
    public void setupTestHarness() throws Exception {
        var offerOrderCoProcessFunction = new OfferOrderJoinFunction(STATE_TTL);
        testHarness = new KeyedTwoInputStreamOperatorTestHarness<>(
                new KeyedCoProcessOperator<>(offerOrderCoProcessFunction),
                Offer::getOfferId,
                Order::getOfferId,
                Types.STRING
        );
        testHarness.open();
    }

    @Test
    public void shouldOutputOfferWoOrder() throws Exception {
        var firstOffer = OFFER_1.toBuilder().isShown(true).build();
        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        var output = testHarness.extractOutputValues();
        var expected = List.of(ChEnrichedOffer.by(firstOffer, null));
        assertEquals(expected, output);
    }

    @Test
    public void shouldOutputOfferWOrder() throws Exception {
        var firstOffer = OFFER_1.toBuilder().isShown(true).build();
        var secondOffer = firstOffer
                .withUpdatedAt(ts(START_DT.plusSeconds(10)))
                .withDeliveryCost(149.0);
        var order = ORDER_1.withUpdatedAt(ts(START_DT.plusSeconds(20)));
        var thirdOffer = firstOffer
                .withUpdatedAt(ts(START_DT.plusSeconds(30)))
                .withDeliveryCost(199.0);

        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(secondOffer, secondOffer.getEventTimestamp()));
        testHarness.processElement2(new StreamRecord<>(order, order.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(thirdOffer, thirdOffer.getEventTimestamp()));

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                ChEnrichedOffer.by(firstOffer, null),
                ChEnrichedOffer.by(secondOffer, null),
                ChEnrichedOffer.by(secondOffer, order),
                ChEnrichedOffer.by(thirdOffer, order)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldNotOutputOrderWoOffer() throws Exception {
        var order = ORDER_1.toBuilder().build();
        testHarness.processElement2(new StreamRecord<>(order, order.getEventTimestamp()));
        testHarness.processBothWatermarks(new Watermark(order.getEventTimestamp() + STATE_TTL.toMillis()));
        var output = testHarness.extractOutputValues();
        var expected = Collections.<ChEnrichedOffer>emptyList();
        assertEquals(expected, output);
    }

    @Test
    public void shouldOutputWOrderOnlyAfterOfferCame() throws Exception {
        var firstOffer = OFFER_1.toBuilder()
                .updatedAt(ts(START_DT.plusSeconds(10)))
                .isShown(true)
                .build();
        var secondOffer = firstOffer
                .withUpdatedAt(ts(START_DT.plusSeconds(20)));

        testHarness.processElement2(new StreamRecord<>(ORDER_1, ORDER_1.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(secondOffer, secondOffer.getEventTimestamp()));

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                ChEnrichedOffer.by(firstOffer, ORDER_1),
                ChEnrichedOffer.by(secondOffer, ORDER_1)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldOutputCorrectEnrichedOffer() throws Exception {
        var order = ORDER_1.toBuilder().build();
        var offer = OFFER_1.toBuilder().city("Москва").build();

        testHarness.processElement2(new StreamRecord<>(order, order.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(offer, offer.getEventTimestamp()));

        var utcMin = Instant.ofEpochSecond((int) (offer.getCreatedAt() / 1000))
                .truncatedTo(ChronoUnit.MINUTES)
                .getEpochSecond();

        var quadKey = Quadkey.ZOOM_18.latlon2quadkey(
                offer.getLat(),
                offer.getLon()
        );

        var expectedEnrichedOffer = ChEnrichedOffer.builder()
                .orderId(order.getOrderId())
                .orderStatus(order.getStatus())
                .offerId(offer.getOfferId())
                .activeZone(offer.getActiveZone())
                .isSurge(offer.getIsSurge() ? 1 : 0)
                .surgeMinOrder(offer.getSurgeMinOrder())
                .isManual(offer.getIsManual() ? 1 : 0)
                .deliveryCost(offer.getDeliveryCost())
                .maxEtaMinutes(offer.getMaxEtaMinutes())
                .minEtaMinutes(offer.getMinEtaMinutes())
                .nextDeliveryCost(offer.getNextDeliveryCost())
                .nextDeliveryThreshold(offer.getNextDeliveryThreshold())
                .deliveryCostArray(offer.getDeliveryCostArray())
                .orderCostArray(offer.getOrderCostArray())
                .userId(order.getTaxiUserId())
                .phonePdId(order.getPhonePdId())
                .depotId(offer.getDepotId())
                .regionId(order.getRegionId())
                .offerCreatedSec((int) (offer.getCreatedAt() / 1000))
                .offerUpdatedSec((int) (offer.getUpdatedAt() / 1000))
                .orderCreatedSec((int) (order.getCreatedAt() / 1000))
                .orderUpdatedSec((int) (order.getUpdatedAt() / 1000))
                .tsMin(utcMin)
                .utcMin(utcMin)
                .city(offer.getCity())
                .quadKey(quadKey).build();

        var output = testHarness.extractOutputValues();
        var expected = List.of(expectedEnrichedOffer);
        assertEquals(expected, output);
    }
}
