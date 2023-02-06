package ru.yandex.metrika.cdp.chwriter.tests.medium;

import java.time.Instant;
import java.util.Objects;

import javax.annotation.Nullable;

import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;


// заказ и его статус
public class OrderJoinedWithOrderStatus {
    private final Order order;
    private final OrderStatus orderStatus;

    public OrderJoinedWithOrderStatus(Order order, OrderStatus orderStatus) {
        this.order = order;
        this.orderStatus = orderStatus;
    }

    public long getRevenue() {
        return order.getRevenue();
    }

    public long getLtv() {
        return order.getRevenue() - order.getCost();
    }

    public Order getOrder() {
        return order;
    }

    public OrderStatus getOrderStatus() {
        return orderStatus;
    }

    public Instant getCreateDateTime() {
        return order.getCreateDateTime();
    }

    public boolean isPaid() {
        return orderStatus.getType() == OrderStatusType.PAID
                || orderStatus.getType() == null && order.getFinishDateTime() != null;
    }

    public boolean isCompleted() {
        return orderStatus.getType() == OrderStatusType.PAID
                || orderStatus.getType() == OrderStatusType.CANCELLED
                || orderStatus.getType() == null && order.getFinishDateTime() != null;
    }

    public boolean isSpam() {
        return orderStatus.getType() == OrderStatusType.SPAM;
    }

    public boolean isPaidAndHasNonNullTime() {
        return isPaid() && (order.getFinishDateTime() != null || order.getUpdateDateTime() != null || order.getSystemLastUpdate() != null);
    }

    @Nullable
    public Instant getFinishTimeIfPaid() {
        if (isPaid()) {
            if (order.getFinishDateTime() != null) {
                return order.getFinishDateTime();
            } else if (order.getUpdateDateTime() != null) {
                return order.getUpdateDateTime();
            } else if (order.getSystemLastUpdate() != null) {
                return order.getSystemLastUpdate();
            }
        }
        return null;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        OrderJoinedWithOrderStatus that = (OrderJoinedWithOrderStatus) o;
        return Objects.equals(order, that.order) && Objects.equals(orderStatus, that.orderStatus);
    }

    @Override
    public int hashCode() {
        return Objects.hash(order, orderStatus);
    }

    @Override
    public String toString() {
        return "OrderJoinedWithOrderStatus{" +
                "order=" + order +
                ", orderStatus=" + orderStatus +
                '}';
    }
}
