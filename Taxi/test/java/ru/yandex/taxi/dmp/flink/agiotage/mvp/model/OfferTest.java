package ru.yandex.taxi.dmp.flink.agiotage.mvp.model;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.flink.util.Collector;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class OfferTest {
    private static final double EPS = 0.00001;

    @Test
    void parse() {
        final var list = new ArrayList<Offer>();
        var collector = new Collector<Offer>() {
            @Override
            public void collect(Offer record) {
                list.add(record);
            }

            @Override
            public void close() {
            }
        };

        try (var stream = getClass().getResourceAsStream("offer")) {
            var text = new String(stream.readAllBytes());
            Offer.parse(text, collector);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        assertEquals(list.size(), 1);
        var offer = list.get(0);
        assertEquals(offer.offerId, "eacf1317a36818499807ad631e9bfc38");
        assertEquals(offer.createdAt, 1608582797000L);
        assertEquals(offer.route.size(), 2);
        assertEquals(offer.route.get(0).size(), 2);
        assertEquals(offer.route.get(1).size(), 2);
        assertEquals(offer.route.get(0).get(0), 34.88831013409035, EPS);
        assertEquals(offer.route.get(0).get(1), 32.07628020862218, EPS);
        assertEquals(offer.route.get(1).get(0), 34.846802, EPS);
        assertEquals(offer.route.get(1).get(1), 32.058235, EPS);
    }
}
