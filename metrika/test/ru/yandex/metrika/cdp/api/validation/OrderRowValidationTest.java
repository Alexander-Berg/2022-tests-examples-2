package ru.yandex.metrika.cdp.api.validation;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Map;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.OrderRowBuilder;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;

import static org.junit.Assert.assertThat;


public class OrderRowValidationTest extends AttributesContainerValidationTest<OrderRow, OrderRowBuilder> {
    @Test
    public void testBlankId() {
        var orderRow = minimalValidBuilder().withId(" ").build();
        assertThat(orderRow, notValidAtLocation("id"));
    }

    @Test
    public void testBlankClientUniqId() {
        var orderRow = minimalValidBuilder().withClientUniqId(" ").build();
        assertThat(orderRow, notValidAtLocation("clientUniqId"));
    }

    @Test
    public void testBlankOrderStatus() {
        var orderRow = minimalValidBuilder().withOrderStatus(" ").build();
        assertThat(orderRow, notValidAtLocation("orderStatus"));
    }

    @Test
    public void testEmptyCreateDateTime() {
        var orderRow = minimalValidBuilder().withCreateDateTime(null).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testCreateDateTimeBefore1970() {
        var orderRow = minimalValidBuilder().withCreateDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testUpdateDateTimeBefore1970() {
        var orderRow = minimalValidBuilder().withUpdateDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(orderRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testFinishDateTimeBefore1970() {
        var orderRow = minimalValidBuilder().withFinishDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(orderRow, notValidAtLocation("finishDateTime"));
    }

    @Test
    public void testCreateDateTimeFromFuture() {
        var orderRow = minimalValidBuilder().withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testUpdateDateTimeFromFuture() {
        var orderRow = minimalValidBuilder().withUpdateDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(orderRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testFinishDateTimeFromFuture() {
        var orderRow = minimalValidBuilder().withFinishDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(orderRow, notValidAtLocation("finishDateTime"));
    }

    @Test
    public void testUpdateDateTimeBeforeCreateDateTime() {
        var orderRow = minimalValidBuilder()
                .withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10))
                .withUpdateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(30))
                .build();
        assertThat(orderRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testFinishDateTimeBeforeCreateDateTime() {
        var orderRow = minimalValidBuilder()
                .withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10))
                .withFinishDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(30))
                .build();
        assertThat(orderRow, notValidAtLocation("finishDateTime"));
    }

    @Test
    public void testNegativeRevenue() {
        var orderRow = minimalValidBuilder().withRevenue(new BigDecimal(-1L)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("revenue"));
    }

    @Test
    public void testTooBigRevenue() {
        var orderRow = minimalValidBuilder().withRevenue(new BigDecimal(Long.MAX_VALUE)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("revenue"));
    }

    @Test
    public void testNegativeCost() {
        var orderRow = minimalValidBuilder().withCost(new BigDecimal(-1L)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("cost"));
    }

    @Test
    public void testTooBigCost() {
        var orderRow = minimalValidBuilder().withCost(new BigDecimal(Long.MAX_VALUE)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("cost"));
    }

    @Test
    public void testBlankProductName() {
        var orderRow = minimalValidBuilder().withProducts(Map.of("   ", 1)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("products"));
    }

    @Test
    public void testNegativeProductCount() {
        var orderRow = minimalValidBuilder().withProducts(Map.of("Яндекс.Станция", -10)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("products"));
    }

    public OrderRowBuilder minimalValidBuilder() {
        return OrderRowBuilder.minimalValidBuilder();
    }
}
