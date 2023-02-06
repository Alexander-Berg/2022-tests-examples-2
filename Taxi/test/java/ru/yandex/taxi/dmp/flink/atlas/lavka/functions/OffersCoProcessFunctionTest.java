package ru.yandex.taxi.dmp.flink.atlas.lavka.functions;

import java.time.Duration;
import java.util.Collections;
import java.util.List;

import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.operators.co.KeyedCoProcessOperator;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.KeyedTwoInputStreamOperatorTestHarness;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.dmp.flink.atlas.lavka.model.Offer;
import ru.yandex.taxi.dmp.flink.atlas.lavka.model.ShownOffer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.OFFER_1;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.START_DT;
import static ru.yandex.taxi.dmp.flink.atlas.lavka.TestUtils.ts;

public class OffersCoProcessFunctionTest {
    private KeyedTwoInputStreamOperatorTestHarness<String, Offer, ShownOffer, Offer> testHarness;

    private static final Duration STATE_TTL = Duration.ofHours(1);

    @BeforeEach
    public void setupTestHarness() throws Exception {
        var offersCoProcessFunction = new OffersCoProcessFunction(STATE_TTL);
        testHarness = new KeyedTwoInputStreamOperatorTestHarness<>(
                new KeyedCoProcessOperator<>(offersCoProcessFunction),
                Offer::getOfferId,
                ShownOffer::getOfferId,
                Types.STRING
        );
        testHarness.open();
    }

    @Test
    public void shouldSetSameCreatedAtForAllEventsFromFirstSeenEvent() throws Exception {
        var firstCreatedAt = ts(START_DT.plusSeconds(10));
        var firstOffer = OFFER_1.toBuilder()
                .isShown(true)
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();

        var secondOffer = firstOffer
                .withCreatedAt(ts(START_DT.plusSeconds(20)))
                .withUpdatedAt(ts(START_DT.plusSeconds(20)));

        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(secondOffer, secondOffer.getEventTimestamp()));

        var output = testHarness.extractOutputValues();
        var expected = List.of(firstOffer, secondOffer.withCreatedAt(firstCreatedAt));
        assertEquals(expected, output);
    }

    @Test
    public void shouldSetShownFlagForOffer1() throws Exception {
        var firstCreatedAt = ts(START_DT);
        var firstOffer = OFFER_1.toBuilder()
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();
        var secondOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(10)))
                .withUpdatedAt(ts(START_DT.plusSeconds(10)));
        var thirdOffer = OFFER_1
                .withShown(true)
                .withCreatedAt(ts(START_DT.plusSeconds(30)))
                .withUpdatedAt(ts(START_DT.plusSeconds(30)));
        var fourthOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(40)))
                .withUpdatedAt(ts(START_DT.plusSeconds(40)));

        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(secondOffer, secondOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(thirdOffer, thirdOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(fourthOffer, fourthOffer.getEventTimestamp()));

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                thirdOffer.withShown(true).withCreatedAt(firstCreatedAt),
                fourthOffer.withShown(true).withCreatedAt(firstCreatedAt)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldSetShownFlagForOffer2() throws Exception {
        var firstCreatedAt = ts(START_DT);
        var firstOffer = OFFER_1.toBuilder()
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();
        var secondOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(10)))
                .withUpdatedAt(ts(START_DT.plusSeconds(10)));
        var shownOfferEvent = ShownOffer.builder()
                .offerId(OFFER_1.getOfferId())
                .timestamp(ts(START_DT.plusSeconds(20)))
                .build();
        var thirdOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(30)))
                .withUpdatedAt(ts(START_DT.plusSeconds(30)));
        var fourthOffer = OFFER_1
                .withShown(true)
                .withCreatedAt(ts(START_DT.plusSeconds(40)))
                .withUpdatedAt(ts(START_DT.plusSeconds(40)));

        testHarness.processElement1(firstOffer, firstOffer.getEventTimestamp());
        testHarness.processElement1(secondOffer, secondOffer.getEventTimestamp());
        testHarness.processElement2(shownOfferEvent, shownOfferEvent.getEventTimestamp());
        testHarness.processElement1(thirdOffer, thirdOffer.getEventTimestamp());
        testHarness.processElement1(fourthOffer, fourthOffer.getEventTimestamp());

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                secondOffer.withShown(true).withCreatedAt(firstCreatedAt),
                thirdOffer.withShown(true).withCreatedAt(firstCreatedAt),
                fourthOffer.withShown(true).withCreatedAt(firstCreatedAt)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldNotUpdateOfferStateWithLateOffers1() throws Exception {
        var firstCreatedAt = ts(START_DT);
        var firstOffer = OFFER_1.toBuilder()
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();
        var secondOffer = OFFER_1
                .withIsSurge(true)
                .withCreatedAt(ts(START_DT.minusSeconds(10)))
                .withUpdatedAt(ts(START_DT.minusSeconds(10)));
        var thirdOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(30)))
                .withUpdatedAt(ts(START_DT.plusSeconds(30)));
        var fourthOffer = OFFER_1
                .withShown(true)
                .withCreatedAt(ts(START_DT.plusSeconds(15)))
                .withUpdatedAt(ts(START_DT.plusSeconds(15)));

        testHarness.processElement1(firstOffer, firstOffer.getEventTimestamp());
        testHarness.processElement1(secondOffer, secondOffer.getEventTimestamp());
        testHarness.processElement1(thirdOffer, thirdOffer.getEventTimestamp());
        testHarness.processElement1(fourthOffer, fourthOffer.getEventTimestamp());

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                thirdOffer.withShown(true).withCreatedAt(firstCreatedAt)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldNotUpdateOfferStateWithLateOffers2() throws Exception {
        var firstCreatedAt = ts(START_DT);
        var firstOffer = OFFER_1.toBuilder()
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();
        var secondOffer = OFFER_1
                .withIsSurge(true)
                .withCreatedAt(ts(START_DT.minusSeconds(10)))
                .withUpdatedAt(ts(START_DT.minusSeconds(10)));
        var shownOfferEvent = ShownOffer.builder()
                .offerId(OFFER_1.getOfferId())
                .timestamp(ts(START_DT.plusSeconds(20)))
                .build();
        var thirdOffer = OFFER_1
                .withCreatedAt(ts(START_DT.plusSeconds(30)))
                .withUpdatedAt(ts(START_DT.plusSeconds(30)));
        var fourthOffer = OFFER_1
                .withShown(true)
                .withCreatedAt(ts(START_DT.plusSeconds(15)))
                .withUpdatedAt(ts(START_DT.plusSeconds(15)));

        testHarness.processElement1(firstOffer, firstOffer.getEventTimestamp());
        testHarness.processElement1(secondOffer, secondOffer.getEventTimestamp());
        testHarness.processElement2(shownOfferEvent, shownOfferEvent.getEventTimestamp());
        testHarness.processElement1(thirdOffer, thirdOffer.getEventTimestamp());
        testHarness.processElement1(fourthOffer, fourthOffer.getEventTimestamp());

        System.out.println(OFFER_1);

        var output = testHarness.extractOutputValues();
        var expected = List.of(
                firstOffer.withShown(true).withCreatedAt(firstCreatedAt),
                thirdOffer.withShown(true).withCreatedAt(firstCreatedAt)
        );
        assertEquals(expected, output);
    }

    @Test
    public void shouldNotOutputNotShownOffers() throws Exception {
        var firstCreatedAt = ts(START_DT);
        var firstOffer = OFFER_1.toBuilder()
                .isShown(false)
                .createdAt(firstCreatedAt)
                .updatedAt(firstCreatedAt)
                .build();
        var secondOffer = OFFER_1.withUpdatedAt(ts(START_DT.plusSeconds(10)));
        var thirdOffer = OFFER_1.withUpdatedAt(ts(START_DT.plusSeconds(119)));

        testHarness.processElement1(new StreamRecord<>(firstOffer, firstOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(secondOffer, secondOffer.getEventTimestamp()));
        testHarness.processElement1(new StreamRecord<>(thirdOffer, thirdOffer.getEventTimestamp()));
        testHarness.processBothWatermarks(new Watermark(ts(START_DT) + STATE_TTL.toMillis()));

        var output = testHarness.extractOutputValues();
        var expected = Collections.<Offer>emptyList();
        assertEquals(expected, output);
    }
}
