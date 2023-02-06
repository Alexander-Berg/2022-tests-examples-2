package ru.yandex.metrika.cdp.api.validation;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.OrderStatusBuilder;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;

import static org.junit.Assert.assertThat;

public class OrderStatusValidationTest extends NamingValidationTest<OrderStatus, OrderStatusBuilder> {

    public OrderStatusValidationTest() {
        super("id");
    }

    @Test
    public void testAbsentOrderStatusType() {
        var orderStatus = minimalValidBuilder().withType(null).build();
        assertThat(orderStatus, notValidAtLocation("type"));
    }

    @Override
    protected OrderStatusBuilder minimalValidBuilder() {
        return OrderStatusBuilder.anOrderStatus().withId("id").withType(OrderStatusType.IN_PROGRESS);
    }
}
