package ru.yandex.metrika.cdp.api.validation.builders;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.frontend.data.rows.OrderRow;
import ru.yandex.metrika.cdp.frontend.rows.RowsTestUtils;

public final class OrderRowBuilder implements AttributesContainerBuilder<OrderRow, OrderRowBuilder> {
    private String id;
    private String clientUniqId;
    private ClientType clientType;
    private LocalDateTime createDateTime;
    private LocalDateTime updateDateTime;
    private LocalDateTime finishDateTime;
    private BigDecimal revenue = new BigDecimal(0);
    private BigDecimal cost = new BigDecimal(0);
    private String orderStatus;
    private Map<String, Integer> products;
    private int counterId;
    private long recordNumber;
    private Map<Attribute, Set<String>> attributeValues = new HashMap<>();

    private OrderRowBuilder() {
    }

    public static OrderRowBuilder anOrderRow() {
        return new OrderRowBuilder();
    }

    public static OrderRowBuilder minimalValidBuilder() {
        return OrderRowBuilder.anOrderRow()
                .withId("id")
                .withClientUniqId("uniqId")
                .withClientType(ClientType.CONTACT)
                .withOrderStatus("done")
                .withCounterId(1)
                .withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10));
    }

    public OrderRowBuilder withId(String id) {
        this.id = id;
        return this;
    }

    public OrderRowBuilder withClientUniqId(String clientUniqId) {
        this.clientUniqId = clientUniqId;
        return this;
    }

    public OrderRowBuilder withClientType(ClientType clientType) {
        this.clientType = clientType;
        return this;
    }

    public OrderRowBuilder withCreateDateTime(LocalDateTime createDateTime) {
        this.createDateTime = createDateTime;
        return this;
    }

    public OrderRowBuilder withUpdateDateTime(LocalDateTime updateDateTime) {
        this.updateDateTime = updateDateTime;
        return this;
    }

    public OrderRowBuilder withFinishDateTime(LocalDateTime finishDateTime) {
        this.finishDateTime = finishDateTime;
        return this;
    }

    public OrderRowBuilder withRevenue(BigDecimal revenue) {
        this.revenue = revenue;
        return this;
    }

    public OrderRowBuilder withCost(BigDecimal cost) {
        this.cost = cost;
        return this;
    }

    public OrderRowBuilder withOrderStatus(String orderStatus) {
        this.orderStatus = orderStatus;
        return this;
    }

    public OrderRowBuilder withProducts(Map<String, Integer> products) {
        this.products = products;
        return this;
    }

    public OrderRowBuilder withCounterId(int counterId) {
        this.counterId = counterId;
        return this;
    }

    public OrderRowBuilder withRecordNumber(long recordNumber) {
        this.recordNumber = recordNumber;
        return this;
    }

    @Override
    public OrderRowBuilder withAttributeValues(Map<Attribute, Set<String>> attributeValues) {
        this.attributeValues = attributeValues;
        return this;
    }

    @Override
    public OrderRowBuilder withAttribute(Attribute attribute, Set<String> values) {
        this.attributeValues.put(attribute, values);
        return this;
    }

    @Override
    public OrderRowBuilder withAttribute(Attribute attribute, String value) {
        this.attributeValues.put(attribute, Set.of(value));
        return this;
    }

    @Override
    public OrderRow build() {
        OrderRow orderRow = new OrderRow();

        RowsTestUtils.setCounterId(orderRow, counterId);

        orderRow.setId(id);
        orderRow.setClientUniqId(clientUniqId);
        orderRow.setClientType(clientType);
        orderRow.setCreateDateTime(createDateTime);
        orderRow.setUpdateDateTime(updateDateTime);
        orderRow.setFinishDateTime(finishDateTime);
        orderRow.setRevenue(revenue);
        orderRow.setCost(cost);
        orderRow.setOrderStatus(orderStatus);
        orderRow.setProducts(products);
        orderRow.setRecordNumber(recordNumber);
        orderRow.setAttributeValues(attributeValues);
        return orderRow;
    }
}
