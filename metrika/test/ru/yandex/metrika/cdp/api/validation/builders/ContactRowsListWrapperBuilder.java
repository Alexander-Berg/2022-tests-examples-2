package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.List;

import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;
import ru.yandex.metrika.cdp.frontend.data.wrappers.ContactRowsListWrapper;

public final class ContactRowsListWrapperBuilder implements Builder<ContactRowsListWrapper> {
    private List<ContactRow> contacts;

    private ContactRowsListWrapperBuilder() {
    }

    public static ContactRowsListWrapperBuilder aContactRowsListWrapper() {
        return new ContactRowsListWrapperBuilder();
    }

    public ContactRowsListWrapperBuilder withContacts(List<ContactRow> contacts) {
        this.contacts = contacts;
        return this;
    }

    @Override
    public ContactRowsListWrapper build() {
        return new ContactRowsListWrapper(contacts);
    }
}
