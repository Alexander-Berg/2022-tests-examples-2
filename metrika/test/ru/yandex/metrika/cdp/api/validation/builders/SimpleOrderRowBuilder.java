package ru.yandex.metrika.cdp.api.validation.builders;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Set;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;
import ru.yandex.metrika.cdp.frontend.validation.NotZero;
import ru.yandex.metrika.spring.params.Md5;

public class SimpleOrderRowBuilder implements AttributesContainerBuilder<SimpleOrderRow, SimpleOrderRowBuilder> {
    private String id;
    private String clientUniqId;
    private Set<@NotNull @NotZero Long> clientIds;
    private Set<@NotBlank @Email String> emails;
    private Set<@NotBlank String> phones;
    private Set<@NotBlank @Md5 String> emailsMd5;
    private Set<@NotBlank @Md5 String> phonesMd5;
    private LocalDateTime createDateTime;
    private BigDecimal revenue;
    private BigDecimal cost;
    private String orderStatus;

    @Override
    public SimpleOrderRowBuilder withAttributeValues(Map<Attribute, Set<String>> attributeValues) {
        return this;
    }

    @Override
    public SimpleOrderRowBuilder withAttribute(Attribute attribute, Set<String> values) {
        return this;
    }

    @Override
    public SimpleOrderRowBuilder withAttribute(Attribute attribute, String value) {
        return this;
    }

    public SimpleOrderRowBuilder setId(String id) {
        this.id = id;
        return this;
    }

    public SimpleOrderRowBuilder setClientUniqId(String clientUniqId) {
        this.clientUniqId = clientUniqId;
        return this;
    }

    public SimpleOrderRowBuilder setClientIds(Set<Long> clientIds) {
        this.clientIds = clientIds;
        return this;
    }

    public SimpleOrderRowBuilder setEmails(Set<String> emails) {
        this.emails = emails;
        return this;
    }

    public SimpleOrderRowBuilder setPhones(Set<String> phones) {
        this.phones = phones;
        return this;
    }

    public SimpleOrderRowBuilder setEmailsMd5(Set<String> emailsMd5) {
        this.emailsMd5 = emailsMd5;
        return this;
    }

    public SimpleOrderRowBuilder setPhonesMd5(Set<String> phonesMd5) {
        this.phonesMd5 = phonesMd5;
        return this;
    }

    public SimpleOrderRowBuilder setCreateDateTime(LocalDateTime createDateTime) {
        this.createDateTime = createDateTime;
        return this;
    }

    public SimpleOrderRowBuilder setRevenue(BigDecimal revenue) {
        this.revenue = revenue;
        return this;
    }

    public SimpleOrderRowBuilder setCost(BigDecimal cost) {
        this.cost = cost;
        return this;
    }

    public SimpleOrderRowBuilder setOrderStatus(String orderStatus) {
        this.orderStatus = orderStatus;
        return this;
    }

    @Override
    public SimpleOrderRow build() {
        var row = new SimpleOrderRow();
        row.setId(id);
        row.setClientUniqId(clientUniqId);
        row.setClientIds(clientIds);
        row.setEmails(emails);
        row.setPhones(phones);
        row.setEmailsMd5(emailsMd5);
        row.setPhonesMd5(phonesMd5);
        row.setCreateDateTime(createDateTime);
        row.setRevenue(revenue);
        row.setCost(cost);
        row.setOrderStatus(orderStatus);
        return row;
    }
}
