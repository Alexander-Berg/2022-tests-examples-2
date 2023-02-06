package ru.yandex.metrika.cdp.api.validation;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Set;

import com.google.common.collect.Sets;
import com.google.common.primitives.UnsignedLong;
import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.ContactRowBuilder;
import ru.yandex.metrika.cdp.frontend.data.rows.ContactRow;

import static org.junit.Assert.assertThat;

public class ContactRowValidationTest extends AttributesContainerValidationTest<ContactRow, ContactRowBuilder> {
    private static final String NOT_AN_MD5 = "NOT_AN_MD5";
    private static final String AN_MD5 = "993a9c97fc1c7035a555f512504a84e3";

    @Test
    public void testBlankUniqId() {
        var contactRow = minimalValidBuilder().withUniqId("").build();
        assertThat(contactRow, notValidAtLocation("uniqId"));
    }

    @Test
    public void testBirthDateFromFuture() {
        var contactRow = minimalValidBuilder().withBirthDate(LocalDate.now().plusYears(1)).build();
        assertThat(contactRow, notValidAtLocation("birthDate"));
    }

    @Test
    public void testBirthDateBefore1970() {
        var contactRow = minimalValidBuilder().withBirthDate(LocalDate.of(1969, 1, 1)).build();
        assertThat(contactRow, notValidAtLocation("birthDate"));
    }

    @Test
    public void testCreateDateTimeBefore1970() {
        var contactRow = minimalValidBuilder().withCreateDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(contactRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testUpdateDateTimeBefore1970() {
        var contactRow = minimalValidBuilder().withUpdateDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(contactRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testCreateDateTimeFromFuture() {
        var contactRow = minimalValidBuilder().withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(contactRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testUpdateDateTimeFromFuture() {
        var contactRow = minimalValidBuilder().withUpdateDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(contactRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testUpdateDateTimeBeforeCreateDateTime() {
        var contactRow = minimalValidBuilder()
                .withCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10))
                .withUpdateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(30))
                .build();
        assertThat(contactRow, notValidAtLocation("updateDateTime"));
    }

    @Test
    public void testZeroClientId() {
        var contactRow = minimalValidBuilder().withClientIds(Set.of(0L)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("clientIds"));
    }

    @Test
    public void testNullClientId() {
        var contactRow = minimalValidBuilder().withClientIds(Sets.newHashSet(new Long[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("clientIds"));
    }

    @Test
    public void testBigClientId() {
        var contactRow = minimalValidBuilder().withClientIds(Set.of(UnsignedLong.MAX_VALUE.longValue())).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNullEmail() {
        var contactRow = minimalValidBuilder().withEmails(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emails"));
    }

    @Test
    public void testNotValidEmail() {
        var contactRow = minimalValidBuilder().withEmails(Set.of(NOT_AN_EMAIL)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emails"));
    }

    @Test
    public void testNotValidEmailsMd5() {
        var contactRow = minimalValidBuilder().withEmailsMd5(Set.of(NOT_AN_MD5)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emailsMd5"));
    }

    @Test
    public void testNullEmailMd5() {
        var contactRow = minimalValidBuilder().withEmailsMd5(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emailsMd5"));
    }

    @Test
    public void testValidEmailsMd5() {
        var contactRow = minimalValidBuilder().withEmailsMd5(Set.of(AN_MD5)).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNullPhone() {
        var contactRow = minimalValidBuilder().withPhones(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phones"));
    }

    @Test
    public void testBlankPhone() {
        var contactRow = minimalValidBuilder().withPhones(Sets.newHashSet("")).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phones"));
    }

    @Test
    public void testNotValidPhonesMd5() {
        var contactRow = minimalValidBuilder().withPhonesMd5(Set.of(NOT_AN_MD5)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phonesMd5"));
    }

    @Test
    public void testNullPhoneMd5() {
        var contactRow = minimalValidBuilder().withPhonesMd5(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phonesMd5"));
    }

    @Test
    public void testValidPhonesMd5() {
        var contactRow = minimalValidBuilder().withPhonesMd5(Set.of(AN_MD5)).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    protected ContactRowBuilder minimalValidBuilder() {
        return ContactRowBuilder.minimalValidBuilder();
    }
}
