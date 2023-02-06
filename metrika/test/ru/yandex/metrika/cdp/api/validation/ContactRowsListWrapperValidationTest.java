package ru.yandex.metrika.cdp.api.validation;

import java.time.LocalDateTime;
import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.ContactRowBuilder;
import ru.yandex.metrika.cdp.api.validation.builders.ContactRowsListWrapperBuilder;
import ru.yandex.metrika.cdp.frontend.data.wrappers.ContactRowsListWrapper;

import static org.junit.Assert.assertThat;

public class ContactRowsListWrapperValidationTest extends AbstractValidationTest<ContactRowsListWrapper, ContactRowsListWrapperBuilder> {


    @Test
    public void testNullContacts() {
        var contactRowsListWrapper = minimalValidBuilder().withContacts(null).build();
        assertThat(contactRowsListWrapper, notValidAtLocation("contacts"));
    }


    @Test
    public void testEmptyContacts() {
        var contactRowsListWrapper = minimalValidBuilder().withContacts(List.of()).build();
        assertThat(contactRowsListWrapper, notValidAtLocation("contacts"));
    }

    @Test
    public void testSeveralErrors() {
        var contactRowsListWrapper = ContactRowsListWrapperBuilder.aContactRowsListWrapper()
                .withContacts(
                        List.of(
                                ContactRowBuilder.minimalValidBuilder()
                                        .withUpdateDateTime(LocalDateTime.parse("1920-04-17T16:12:21"))
                                        .build(),
                                ContactRowBuilder.minimalValidBuilder()
                                        .withCreateDateTime(LocalDateTime.parse("1920-04-30T16:12:21"))
                                        .build()
                        )
                ).build();
        assertThat(contactRowsListWrapper, notValidAtLocations(List.of("contacts[0].updateDateTime", "contacts[1].createDateTime")));
    }

    @Override
    protected ContactRowsListWrapperBuilder minimalValidBuilder() {
        return ContactRowsListWrapperBuilder.aContactRowsListWrapper()
                .withContacts(List.of(
                        ContactRowBuilder.minimalValidBuilder().build()
                ));
    }
}
