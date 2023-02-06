package ru.yandex.taxi.dmp.flink.atlas.lavka.model;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.functions.util.ListCollector;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class ParsingTest {
    private static final Offer OFFER_1 = Offer.builder()
            .offerId("7032d80a1a754e92a7a2a85fa914a105")
            .activeZone("foot")
            .isSurge(false)
            .surgeMinOrder(0.0)
            .isManual(false)
            .deliveryCost(69.0)
            .maxEtaMinutes(50)
            .minEtaMinutes(40)
            .nextDeliveryCost(29.0)
            .nextDeliveryThreshold(600.0)
            .isShown(false)
            .deliveryCostArray(new double[]{69.0, 29.0, 0.0})
            .orderCostArray(new double[]{0.0, 600.0, 1200.0})
            .depotId("194163")
            .lat(59.83824943833668)
            .lon(30.114438865206907)
            .userId("398ebe9ebcee6f33ee40d0b752e9c6d3")
            .createdAt(1639422157291L)
            .updatedAt(1639422157291L).build();

    private static final Offer OFFER_2 = Offer.builder()
            .offerId("3657fef0d8c841ceb79857858d468e3a")
            .activeZone("foot")
            .isSurge(false)
            .surgeMinOrder(100.0)
            .isManual(false)
            .deliveryCost(null)
            .maxEtaMinutes(60)
            .minEtaMinutes(50)
            .nextDeliveryCost(null)
            .nextDeliveryThreshold(null)
            .isShown(false)
            .deliveryCostArray(new double[]{0.0})
            .orderCostArray(new double[]{100.0})
            .depotId("106347")
            .lat(55.845016)
            .lon(37.639249)
            .userId(null)
            .createdAt(1639422157319L)
            .updatedAt(1639422157319L).build();

    private static final Order ORDER_1 = Order.builder()
            .orderId("747a603217d74907b1e2490b56f9ee64-grocery")
            .offerId("33795398ac2c44e6b177ba7f587cc783")
            .status("closed")
            .lat(55.728393)
            .lon(37.612695)
            .depotId("169093")
            .regionId(213)
            .eatsUserId("16509624")
            .taxiUserId("dd7aba300df60f173f79252dd365114a")
            .phonePdId("ce3de5c072174536afc6aaa282941a06")
            .createdAt(1638808401342L)
            .updatedAt(1638809676301L).build();

    private static final ShownOffer SHOWN_OFFER_1 = ShownOffer.builder()
            .offerId("33795398ac2c44e6b177ba7f587cc783")
            .timestamp(1639256106132L).build();

    private static final ShownOffer SHOWN_OFFER_2 = ShownOffer.builder()
            .offerId("33795398ac2c44e6b177ba7f587cc785")
            .timestamp(1639256166132L).build();

    @Test
    void offerDeserializesFromJson() throws IOException {
        var offersStr = Files.readString(Paths.get("src/test/resources/test_offer_lb"));
        var out = new ArrayList<Offer>(2);
        var listCollector = new ListCollector<>(out);
        Offer.parse(offersStr, listCollector);
        assertEquals(List.of(OFFER_1, OFFER_2), out);
    }

    @Test
    void orderDeserializesFromJson() throws IOException {
        var mapper = new ObjectMapper();
        var jsonOrder = Files.readString(Paths.get("src/test/resources/test_order_lb"));
        InputStream stream = new ByteArrayInputStream(jsonOrder.getBytes(StandardCharsets.UTF_8));
        JsonParser parser = mapper.getFactory().createParser(stream);
        DeserializationContext ctx = mapper.getDeserializationContext();
        var order = new Order.Deserializer().deserialize(parser, ctx);
        assertEquals(ORDER_1, order);
    }

    @Test
    void shownOfferDeserializesFromJson() throws IOException {
        var offersStr = Files.readString(Paths.get("src/test/resources/test_shown_offer_lb"));
        var out = new ArrayList<ShownOffer>(2);
        var listCollector = new ListCollector<>(out);
        ShownOffer.parse(offersStr, listCollector);
        assertEquals(List.of(SHOWN_OFFER_1, SHOWN_OFFER_2), out);
    }
}
