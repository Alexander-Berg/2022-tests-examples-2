package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.List;

import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.cdp.frontend.data.wrappers.OrderRowsListWrapper;

public final class OrderRowsListWrapperBuilder implements Builder<OrderRowsListWrapper> {
    private List<OrderRow> orders;

    private OrderRowsListWrapperBuilder() {
    }

    public static OrderRowsListWrapperBuilder anOrderRowsListWrapper() {
        return new OrderRowsListWrapperBuilder();
    }

    public OrderRowsListWrapperBuilder withOrders(List<OrderRow> orders) {
        this.orders = orders;
        return this;
    }

    @Override
    public OrderRowsListWrapper build() {
        return new OrderRowsListWrapper(orders);
    }
}
