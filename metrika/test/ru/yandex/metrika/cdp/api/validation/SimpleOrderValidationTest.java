package ru.yandex.metrika.cdp.api.validation;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Set;

import com.google.common.collect.Sets;
import com.google.common.primitives.UnsignedLong;
import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.SimpleOrderRowBuilder;
import ru.yandex.metrika.cdp.frontend.data.rows.SimpleOrderRow;

import static org.junit.Assert.assertThat;

public class SimpleOrderValidationTest
        extends AbstractValidationTest<SimpleOrderRow, SimpleOrderRowBuilder> {

    private static final String NOT_AN_MD5 = "NOT_AN_MD5";
    private static final String AN_MD5 = "993a9c97fc1c7035a555f512504a84e3";
    private static final String NOT_AN_EMAIL = "some_thing_that_is_clearly_not_an_email!!! XD@@@@";

    @Test
    public void testNullUser() {
        var contactRow = minimalValidBuilder().setClientUniqId(null).build();
        assertThat(contactRow, notValidAtLocation("userDefined"));
    }

    @Test
    public void testNullUserUniqueIdButWithEmails() {
        var contactRow = minimalValidBuilder().setClientUniqId(null).setEmails(Set.of("a@b.c")).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testZeroClientId() {
        var contactRow = minimalValidBuilder().setClientIds(Set.of(0L)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("clientIds"));
    }

    @Test
    public void testNullClientId() {
        var contactRow = minimalValidBuilder().setClientIds(Sets.newHashSet(new Long[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("clientIds"));
    }

    @Test
    public void testBigClientId() {
        var contactRow = minimalValidBuilder().setClientIds(Set.of(UnsignedLong.MAX_VALUE.longValue())).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNullEmail() {
        var contactRow = minimalValidBuilder().setEmails(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emails"));
    }

    @Test
    public void testNotValidEmail() {
        var contactRow = minimalValidBuilder().setEmails(Set.of(NOT_AN_EMAIL)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emails"));
    }

    @Test
    public void testNotValidEmailsMd5() {
        var contactRow = minimalValidBuilder().setEmailsMd5(Set.of(NOT_AN_MD5)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emailsMd5"));
    }

    @Test
    public void testNullEmailMd5() {
        var contactRow = minimalValidBuilder().setEmailsMd5(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("emailsMd5"));
    }

    @Test
    public void testValidEmailsMd5() {
        var contactRow = minimalValidBuilder().setEmailsMd5(Set.of(AN_MD5)).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNullPhone() {
        var contactRow = minimalValidBuilder().setPhones(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phones"));
    }

    @Test
    public void testBlankPhone() {
        var contactRow = minimalValidBuilder().setPhones(Sets.newHashSet("")).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phones"));
    }

    @Test
    public void testNotValidPhonesMd5() {
        var contactRow = minimalValidBuilder().setPhonesMd5(Set.of(NOT_AN_MD5)).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phonesMd5"));
    }

    @Test
    public void testNullPhoneMd5() {
        var contactRow = minimalValidBuilder().setPhonesMd5(Sets.newHashSet(new String[]{null})).build();
        assertThat(contactRow, notValidAtLocationStartingWith("phonesMd5"));
    }

    @Test
    public void testValidPhonesMd5() {
        var contactRow = minimalValidBuilder().setPhonesMd5(Set.of(AN_MD5)).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNullId() {
        var orderRow = minimalValidBuilder().setId(null).build();
        assertThat(orderRow, validationMatchers.valid());
    }

    @Test
    public void testEmptyCreateDateTime() {
        var orderRow = minimalValidBuilder().setCreateDateTime(null).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testCreateDateTimeBefore1970() {
        var orderRow = minimalValidBuilder().setCreateDateTime(LocalDate.of(1969, 1, 1).atStartOfDay()).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testCreateDateTimeFromFuture() {
        var orderRow = minimalValidBuilder().setCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).plusMinutes(30)).build();
        assertThat(orderRow, notValidAtLocation("createDateTime"));
    }

    @Test
    public void testNegativeRevenue() {
        var orderRow = minimalValidBuilder().setRevenue(new BigDecimal(-1L)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("revenue"));
    }

    @Test
    public void testTooBigRevenue() {
        var orderRow = minimalValidBuilder().setRevenue(new BigDecimal(Long.MAX_VALUE)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("revenue"));
    }

    @Test
    public void testNegativeCost() {
        var orderRow = minimalValidBuilder().setCost(new BigDecimal(-1L)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("cost"));
    }

    @Test
    public void testTooBigCost() {
        var orderRow = minimalValidBuilder().setCost(new BigDecimal(Long.MAX_VALUE)).build();
        assertThat(orderRow, notValidAtLocationStartingWith("cost"));
    }

    @Override
    protected SimpleOrderRowBuilder minimalValidBuilder() {
        return new SimpleOrderRowBuilder()
                .setCreateDateTime(LocalDateTime.now(ZoneOffset.UTC).minusMinutes(10))
                .setClientUniqId("some_unique_id");
    }
}
