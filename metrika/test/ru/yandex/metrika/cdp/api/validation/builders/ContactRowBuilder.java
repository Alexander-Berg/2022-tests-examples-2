package ru.yandex.metrika.cdp.api.validation.builders;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import javax.validation.constraints.Email;
import javax.validation.constraints.Positive;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.cdp.frontend.rows.RowsTestUtils;
import ru.yandex.metrika.spring.params.Md5;

public final class ContactRowBuilder implements AttributesContainerBuilder<ContactRow, ContactRowBuilder> {
    private String uniqId;
    private String name;
    private LocalDate birthDate;
    private LocalDateTime createDateTime;
    private LocalDateTime updateDateTime;
    private Set<@Positive Long> clientIds;
    private Set<String> userIds;
    private Set<@Email String> emails;
    private Set<String> phones;
    private Set<@Md5 String> emailsMd5;
    private Set<@Md5 String> phonesMd5;
    private String companyUniqId;
    private int counterId;
    private long recordNumber;
    private Map<Attribute, Set<String>> attributeValues = new HashMap<>();

    private ContactRowBuilder() {
    }

    public static ContactRowBuilder aContactRow() {
        return new ContactRowBuilder();
    }

    public static ContactRowBuilder minimalValidBuilder() {
        return ContactRowBuilder.aContactRow().withUniqId("uniqId").withCounterId(1);
    }

    public ContactRowBuilder withUniqId(String uniqId) {
        this.uniqId = uniqId;
        return this;
    }

    public ContactRowBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public ContactRowBuilder withBirthDate(LocalDate birthDate) {
        this.birthDate = birthDate;
        return this;
    }

    public ContactRowBuilder withCreateDateTime(LocalDateTime createDateTime) {
        this.createDateTime = createDateTime;
        return this;
    }

    public ContactRowBuilder withUpdateDateTime(LocalDateTime updateDateTime) {
        this.updateDateTime = updateDateTime;
        return this;
    }

    public ContactRowBuilder withClientIds(Set<Long> clientIds) {
        this.clientIds = clientIds;
        return this;
    }

    public ContactRowBuilder withUserIds(Set<String> userIds) {
        this.userIds = userIds;
        return this;
    }

    public ContactRowBuilder withEmails(Set<String> emails) {
        this.emails = emails;
        return this;
    }

    public ContactRowBuilder withEmailsMd5(Set<String> emailsMd5) {
        this.emailsMd5 = emailsMd5;
        return this;
    }

    public ContactRowBuilder withPhones(Set<String> phones) {
        this.phones = phones;
        return this;
    }

    public ContactRowBuilder withPhonesMd5(Set<String> phonesMd5) {
        this.phonesMd5 = phonesMd5;
        return this;
    }

    public ContactRowBuilder withCompanyUniqId(String companyUniqId) {
        this.companyUniqId = companyUniqId;
        return this;
    }

    public ContactRowBuilder withCounterId(int counterId) {
        this.counterId = counterId;
        return this;
    }

    public ContactRowBuilder withRecordNumber(long recordNumber) {
        this.recordNumber = recordNumber;
        return this;
    }

    @Override
    public ContactRowBuilder withAttributeValues(Map<Attribute, Set<String>> attributeValues) {
        this.attributeValues = attributeValues;
        return this;
    }

    @Override
    public ContactRowBuilder withAttribute(Attribute attribute, Set<String> values) {
        this.attributeValues.put(attribute, values);
        return this;
    }

    @Override
    public ContactRowBuilder withAttribute(Attribute attribute, String value) {
        this.attributeValues.put(attribute, Set.of(value));
        return this;
    }

    @Override
    public ContactRow build() {
        ContactRow contactRow = new ContactRow();

        RowsTestUtils.setCounterId(contactRow, counterId);

        contactRow.setUniqId(uniqId);
        contactRow.setName(name);
        contactRow.setBirthDate(birthDate);
        contactRow.setCreateDateTime(createDateTime);
        contactRow.setUpdateDateTime(updateDateTime);
        contactRow.setClientIds(clientIds);
        contactRow.setUserIds(userIds);
        contactRow.setEmails(emails);
        contactRow.setPhones(phones);
        contactRow.setCompanyUniqId(companyUniqId);
        contactRow.setRecordNumber(recordNumber);
        contactRow.setAttributeValues(attributeValues);
        contactRow.setEmailsMd5(emailsMd5);
        contactRow.setPhonesMd5(phonesMd5);

        return contactRow;
    }
}
