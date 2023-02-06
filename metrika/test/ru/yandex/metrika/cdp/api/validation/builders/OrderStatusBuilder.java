package ru.yandex.metrika.cdp.api.validation.builders;

import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;

public final class OrderStatusBuilder implements NameAwareBuilder<OrderStatus, OrderStatusBuilder> {
    String id;
    String humanized;
    OrderStatusType type;

    private OrderStatusBuilder() {
    }

    public static OrderStatusBuilder anOrderStatus() {
        return new OrderStatusBuilder();
    }

    public OrderStatusBuilder withId(String id) {
        this.id = id;
        return this;
    }

    @Override
    public OrderStatusBuilder withName(String name) {
        // compatibility
        return withId(name);
    }

    public OrderStatusBuilder withHumanized(String humanized) {
        this.humanized = humanized;
        return this;
    }

    public OrderStatusBuilder withType(OrderStatusType type) {
        this.type = type;
        return this;
    }

    public OrderStatus build() {
        OrderStatus orderStatus = new OrderStatus();
        orderStatus.setId(id);
        orderStatus.setHumanized(humanized);
        orderStatus.setType(type);
        return orderStatus;
    }
}
