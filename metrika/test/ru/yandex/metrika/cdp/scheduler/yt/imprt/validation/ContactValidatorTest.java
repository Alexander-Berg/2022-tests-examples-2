package ru.yandex.metrika.cdp.scheduler.yt.imprt.validation;

import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

import javax.annotation.Nonnull;

import org.jetbrains.annotations.NotNull;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.scheduler.yt.dto.ContactYt;
import ru.yandex.metrika.cdp.validation.ValidationHelper;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

/**
 * {@link ContactValidator}.
 */
public class ContactValidatorTest {

    private static final String defaultLogGroup = "Not identified client";

    @NotNull
    static ContactYt buildEmptyClient() {
        return new ContactYt();
    }

    @NotNull
    static ContactYt buildValidClient() {
        ContactYt client = buildEmptyClient();
        client.setHardId("some_hard_id_1000073054882334461");
        client.setStatus("ACTIVE");
        client.setParentHardId("some_hard_id_8035624153770042711");
        client.setName("Kyle");
        client.setBirthDate("2006-09-18");
        client.setCreateDateTime("2009-02-09T15:08:08.111610Z");
        client.setUpdateDateTime("2015-12-14T15:08:08.111611Z");
        client.setClientIds(Set.of(4033321451825775116L, 676579692421060932L, 5805798462966467521L,
                8478297260868512830L, 7330503598689227105L, 4667403041853443789L));
        client.setClientUserIds(Set.of("some-client-user-id-7153840417260699588", "some-client-user-id-627576136236124475",
                "some-client-user-id-5225735471987652780", "some-client-user-id-8410834078843973869",
                "some-client-user-id-309520724592368700", "some-client-user-id-1452350238472431830"));
        client.setEmails(Set.of("some-email-7842851550995462666@example.com", "some-email-1169929807331893249@example.com",
                "some-email-6426549810883937799@example.com", "some-email-3105088065704982527@example.com",
                "some-email-1103077418081656612@example.com", "some-email-2193777038880106062@example.com",
                "some-email-7298918825053830155@example.com", "some-email-5641380120333897742@example.com"));
        client.setPhones(Set.of("+79555335167", "+7922393754", "+79701502205", "+79821439227", "+79954212171", "+79629366989"));
        client.setAttributes(Map.of(
                "idf", Set.of("2982044856427171932", "8749449181851346267", "6210720761493431838", "6092351152210794892",
                        "5216990128670138680", "7322343946078383297", "6879547904312982086", "7670980175006398716",
                        "4086907218188855161", "6573407605688345372", "5499826766378587618", "6874878934330998429")));
        return client;
    }

    @Nonnull
    static String getLogGroup(ContactYt contactYt) {
        return Objects.requireNonNullElse(contactYt.getHardId(), defaultLogGroup);
    }

    ContactValidator validator;

    private void setUpValidator() throws Exception {
        setUpValidator(List.of(new Attribute("idf", "idf", AttributeType.NUMERIC, true)));
    }

    private void setUpValidator(List<Attribute> attributes) throws Exception {
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        validator = new ContactValidator(
                attributes,
                new ValidationHelper(null, counterId -> ZoneOffset.UTC, localeDictionaries)
        );
    }


    @Before
    public void setUp() throws Exception {
        setUpValidator();
    }

    @Test
    public void validClient() {
        Assert.assertTrue(validator.isValid(buildValidClient()));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void withoutRequiredField() {
        ContactYt client = buildValidClient();
        client.setHardId(null);
        Assert.assertFalse(validator.isValid(client));
        assertSingleClientErrorDescriptionSize(1);
    }

    @Test
    public void withIllegalEnumField() {
        ContactYt client = buildValidClient();
        client.setStatus("active");
        Assert.assertFalse(validator.isValid(client));
        assertSingleClientErrorDescriptionSize(1);
    }

    @Test
    public void withIllegalDateField() {
        ContactYt client = buildValidClient();
        client.setCreateDateTime("2015-12-14T 15:08:08.111611Z");
        Assert.assertFalse(validator.isValid(client));
        assertSingleClientErrorDescriptionSize(1);
    }

    @Test
    public void withIllegalEmail() {
        ContactYt client = buildValidClient();
        client.setEmails(Set.of("some-email-7842851550995462666example.com", "some-email-1169929807331893249@example.com",
                "some-email-6426549810883937799@example."));
        Assert.assertFalse(validator.isValid(client));
        assertSingleClientErrorDescriptionSize(2);
    }

    @Test
    public void requiredFieldsArePresent() {
        ContactYt client = buildEmptyClient();
        client.setHardId("a");
        client.setStatus("b");
        Assert.assertTrue(validator.requiredFieldsArePresent(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void requiredFieldsIncorrectCombinations() {
        ContactYt client = buildEmptyClient();
        for (int combination = 0; combination < Math.pow(2, 3) - 1; combination++) {
            client.setHardId((combination & 1) == 1 ? "d" : null);
            client.setStatus(((combination << 1) & 1) == 1 ? "e" : null);
            Assert.assertFalse(validator.requiredFieldsArePresent(client, getLogGroup(client)));
        }
    }

    @Test
    public void validStatusValidClientTypeIsCorrect() {
        ContactYt client = buildEmptyClient();
        client.setStatus("DELETED");
        Assert.assertTrue(validator.enumFieldsAreLegal(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void nullDatesAreCorrect() {
        var contactYt = buildEmptyClient();
        Assert.assertTrue(validator.dateFieldsAreNullOrValid(contactYt, getLogGroup(contactYt)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void validDatesAreCorrect() {
        ContactYt client = buildEmptyClient();
        client.setBirthDate("2006-09-18");
        client.setCreateDateTime("2011-05-26T15:08:08.105714Z");
        client.setUpdateDateTime("2017-05-03T15:08:08.105716Z");
        Assert.assertTrue(validator.dateFieldsAreNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void partiallyValidDatesAreNotCorrect() {
        ContactYt client = buildEmptyClient();
        String[] validDates = {"2006-09-18", "2011-05-26T15:08:08.105714Z", "2017-05-03T15:08:08.105716Z"};
        String[] invalidDates = {"2006-9-18", "2011-05-26T15:0:08.105714Z", "2017-05-03T15:08:08.105716"};
        for (int description = 0; description < Math.pow(2, validDates.length) - 1; description++) {
            client.setBirthDate((description & 1) == 1 ? validDates[0] : invalidDates[0]);
            client.setCreateDateTime(((description >> 1) & 1) == 1 ? validDates[1] : invalidDates[1]);
            client.setUpdateDateTime(((description >> 2) & 1) == 1 ? validDates[2] : invalidDates[2]);
            Assert.assertFalse(validator.dateFieldsAreNullOrValid(client, getLogGroup(client)));
        }
    }

    @Test
    public void nullPhoneSetIsCorrect() {
        var contactYt = buildEmptyClient();
        Assert.assertTrue(validator.phoneSetIsNullOrValid(contactYt, getLogGroup(contactYt)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void emptyPhoneSetIsCorrect() {
        ContactYt client = buildEmptyClient();
        client.setPhones(Set.of());
        Assert.assertTrue(validator.phoneSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void anyPhoneSetIsCorrect() {
        ContactYt client = buildEmptyClient();
        client.setEmails(Set.of("phone1", "phone2"));
        Assert.assertTrue(validator.phoneSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void nullEmailSetIsCorrect() {
        ContactYt client = buildEmptyClient();
        Assert.assertTrue(validator.emailSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void emptyEmailSetIsCorrect() {
        ContactYt client = buildEmptyClient();
        client.setEmails(Set.of());
        Assert.assertTrue(validator.emailSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void validEmailSetIsCorrect() {
        ContactYt client = buildEmptyClient();
        client.setEmails(Set.of("some-email-7842851550995462666@example.com", "some-email-1169929807331893249@example.com",
                "some-email-6426549810883937799@example.com", "some-email-3105088065704982527@example.com"));
        Assert.assertTrue(validator.emailSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void partiallyInvalidEmailSetIsNotCorrect() {
        ContactYt client = buildEmptyClient();
        client.setEmails(Set.of("some-email-7842851550995462666@example.com", "some-email-1169929807331893249example.com",
                "some-email-6426549810883937799@.com", "some-email-3105088065704982527@example.com"));
        Assert.assertFalse(validator.emailSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(2);
    }

    @Test
    public void invalidEmailSetIsNotCorrect() {
        ContactYt client = buildEmptyClient();
        client.setEmails(Set.of("some-email-7842851550995462666@example.", "some-email-1169929807331893249example.com",
                "@example.com", "some-email-3105088065704982527@.com"));
        Assert.assertFalse(validator.emailSetIsNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(4);
    }

    @Test
    public void nullAttributesAreCorrect() {
        ContactYt client = buildEmptyClient();
        Assert.assertTrue(validator.attributesAreNullOrValid(client, getLogGroup(client)));
        assertSingleClientErrorDescriptionSize(0);
    }

    @Test
    public void notNullAttributesAreCorrect() throws Exception {
        ContactYt client = buildEmptyClient();
        client.setAttributes(Map.of(
                "key1", Set.of("value11", "value12"),
                "key2", Set.of("value21", "value22")));
        setUpValidator(List.of(
                new Attribute("key1", "key1", AttributeType.TEXT, true),
                new Attribute("key2", "key2", AttributeType.TEXT, true)
        ));
        Assert.assertTrue(
                validator.attributesAreNullOrValid(client, getLogGroup(client))
        );
        assertSingleClientErrorDescriptionSize(0);
    }

    void assertSingleClientErrorDescriptionSize(int expectedSize) {
        // Предполагается, что данные об ошибках передавались для единственного объекта.
        if (expectedSize == 0) {
            Assert.assertEquals(0, validator.getErrorsById().size());
        } else {
            Assert.assertEquals(1, validator.getErrorsById().size());
            Assert.assertEquals(expectedSize, validator.getErrorsById().values().iterator().next().size());
        }
    }


}
