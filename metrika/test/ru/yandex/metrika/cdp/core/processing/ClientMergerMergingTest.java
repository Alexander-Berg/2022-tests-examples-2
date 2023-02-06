package ru.yandex.metrika.cdp.core.processing;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import org.junit.Test;

import ru.yandex.metrika.cdp.core.merge.LocalDateFieldChange;
import ru.yandex.metrika.cdp.core.merge.LongSetFieldChange;
import ru.yandex.metrika.cdp.core.merge.StringFieldChange;
import ru.yandex.metrika.cdp.core.merge.StringSetFieldChange;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.hamcrest.Matchers.hasEntry;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.BIRTH_DATE;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.CLIENT_IDS;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.EMAILS;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.EMAILS_MD5;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.NAME;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.PHONES;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.PHONES_MD5;

public class ClientMergerMergingTest extends AbstractClientMergerTest{

    @Test
    public void simpleMerge() {
        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setName(OLD_CLIENT_NAME);

        var newClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);

        var result = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var client = result.getEntity();
        var changedFields = result.getChangesMeta().getFieldsChanges();
        assertEquals(client.getName(), NEW_CLIENT_NAME);
        assertThat(changedFields, hasEntry(NAME, new StringFieldChange(OLD_CLIENT_NAME, NEW_CLIENT_NAME)));
    }

    @Test
    public void complexMergeSave() {
        Client oldClient = getOldClient();
        Client newClient = getNewClient();

        var result = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var client = result.getEntity();
        var changedFields = result.getChangesMeta().getFieldsChanges();

        assertEquals(client.getName(), NEW_CLIENT_NAME);
        assertEquals(client.getBirthDate(), LocalDate.now().minusDays(10));
        assertEquals(client.getClientIds(), Set.of(2L, 3L, 4L));
        assertEquals(client.getEmails(), Set.of(NEW_EMAIL));
        assertEquals(client.getPhones(), Set.of(NEW_PHONE));
        assertEquals(client.getEmailsMd5(), Set.of(NEW_EMAIL_MD5));
        assertEquals(client.getPhonesMd5(), Set.of(NEW_PHONE_MD5));
        assertEquals(client.getAttributes(), Map.of(
                MULTIVALUE_ATTRIBUTE, Set.of(STRING_VALUE_2, STRING_VALUE_3)
        ));

        assertThat(changedFields, hasEntry(NAME, new StringFieldChange(OLD_CLIENT_NAME, NEW_CLIENT_NAME)));
        assertThat(changedFields, hasEntry(BIRTH_DATE, new LocalDateFieldChange(null, LocalDate.now().minusDays(10))));
        assertThat(changedFields, hasEntry(CLIENT_IDS, new LongSetFieldChange(Set.of(1L, 2L, 3L), Set.of(2L, 3L, 4L))));
        assertThat(changedFields, hasEntry(EMAILS, new StringSetFieldChange(Set.of(OLD_EMAIL), Set.of(NEW_EMAIL))));
        assertThat(changedFields, hasEntry(PHONES, new StringSetFieldChange(Set.of(OLD_PHONE), Set.of(NEW_PHONE))));
        assertThat(changedFields, hasEntry(EMAILS_MD5, new StringSetFieldChange(Set.of(OLD_EMAIL_MD5), Set.of(NEW_EMAIL_MD5))));
        assertThat(changedFields, hasEntry(PHONES_MD5, new StringSetFieldChange(Set.of(OLD_PHONE_MD5), Set.of(NEW_PHONE_MD5))));
        assertThat(changedFields, hasEntry(CUSTOM_ATTRIBUTE, new StringSetFieldChange(Set.of(CUSTOM_STRING_VALUE), Set.of())));
        assertThat(changedFields, hasEntry(MULTIVALUE_ATTRIBUTE, new StringSetFieldChange(Set.of(STRING_VALUE_1), Set.of(STRING_VALUE_2, STRING_VALUE_3))));
    }

    @Test
    public void complexMergeUpdate() {
        var oldClient = getOldClient();

        var newClient = getNewClient();

        var result = clientMerger.merge(newClient, oldClient, UpdateType.UPDATE, Set.of(), UPLOADING_ID_1);
        var client = result.getEntity();
        var changedFields = result.getChangesMeta().getFieldsChanges();

        assertEquals(client.getName(), NEW_CLIENT_NAME);
        assertEquals(client.getBirthDate(), LocalDate.now().minusDays(10));
        assertEquals(client.getParentCdpUid(), (Long) 2L);
        assertEquals(client.getClientIds(), Set.of(2L, 3L, 4L));
        assertEquals(client.getEmails(), Set.of(NEW_EMAIL));
        assertEquals(client.getPhones(), Set.of(NEW_PHONE));
        assertEquals(client.getEmailsMd5(), Set.of(NEW_EMAIL_MD5));
        assertEquals(client.getPhonesMd5(), Set.of(NEW_PHONE_MD5));
        assertEquals(client.getAttributes(), Map.of(
                CUSTOM_ATTRIBUTE, Set.of(CUSTOM_STRING_VALUE),
                MULTIVALUE_ATTRIBUTE, Set.of(STRING_VALUE_2, STRING_VALUE_3)
        ));

        assertThat(changedFields, hasEntry(NAME, new StringFieldChange(OLD_CLIENT_NAME, NEW_CLIENT_NAME)));
        assertThat(changedFields, hasEntry(BIRTH_DATE, new LocalDateFieldChange(null, LocalDate.now().minusDays(10))));
        assertThat(changedFields, hasEntry(CLIENT_IDS, new LongSetFieldChange(Set.of(1L, 2L, 3L), Set.of(2L, 3L, 4L))));
        assertThat(changedFields, hasEntry(EMAILS, new StringSetFieldChange(Set.of(OLD_EMAIL), Set.of(NEW_EMAIL))));
        assertThat(changedFields, hasEntry(PHONES, new StringSetFieldChange(Set.of(OLD_PHONE), Set.of(NEW_PHONE))));
        assertThat(changedFields, hasEntry(EMAILS_MD5, new StringSetFieldChange(Set.of(OLD_EMAIL_MD5), Set.of(NEW_EMAIL_MD5))));
        assertThat(changedFields, hasEntry(PHONES_MD5, new StringSetFieldChange(Set.of(OLD_PHONE_MD5), Set.of(NEW_PHONE_MD5))));
        assertThat(changedFields, hasEntry(MULTIVALUE_ATTRIBUTE, new StringSetFieldChange(Set.of(STRING_VALUE_1), Set.of(STRING_VALUE_2, STRING_VALUE_3))));
    }

    @Test
    public void complexMergeAppend() {
        var oldClient = getOldClient();

        var newClient = getNewClient();

        var result = clientMerger.merge(newClient, oldClient, UpdateType.APPEND, Set.of(), UPLOADING_ID_1);
        var client = result.getEntity();
        var changedFields = result.getChangesMeta().getFieldsChanges();

        assertEquals(client.getName(), NEW_CLIENT_NAME);
        assertEquals(client.getBirthDate(), LocalDate.now().minusDays(10));
        assertEquals(client.getParentCdpUid(), (Long) 2L);
        assertEquals(client.getClientIds(), Set.of(1L, 2L, 3L, 4L));
        assertEquals(client.getEmails(), Set.of(NEW_EMAIL, OLD_EMAIL));
        assertEquals(client.getPhones(), Set.of(OLD_PHONE, NEW_PHONE));
        assertEquals(client.getEmailsMd5(), Set.of(NEW_EMAIL_MD5, OLD_EMAIL_MD5));
        assertEquals(client.getPhonesMd5(), Set.of(OLD_PHONE_MD5, NEW_PHONE_MD5));
        assertEquals(client.getAttributes(), Map.of(
                CUSTOM_ATTRIBUTE, Set.of(CUSTOM_STRING_VALUE),
                MULTIVALUE_ATTRIBUTE, Set.of(STRING_VALUE_1, STRING_VALUE_2, STRING_VALUE_3)
        ));

        assertThat(changedFields, hasEntry(NAME, new StringFieldChange(OLD_CLIENT_NAME, NEW_CLIENT_NAME)));
        assertThat(changedFields, hasEntry(BIRTH_DATE, new LocalDateFieldChange(null, LocalDate.now().minusDays(10))));
        assertThat(changedFields, hasEntry(CLIENT_IDS, new LongSetFieldChange(Set.of(1L, 2L, 3L), Set.of(1L, 2L, 3L, 4L))));
        assertThat(changedFields, hasEntry(EMAILS, new StringSetFieldChange(Set.of(OLD_EMAIL), Set.of(NEW_EMAIL, OLD_EMAIL))));
        assertThat(changedFields, hasEntry(PHONES, new StringSetFieldChange(Set.of(OLD_PHONE), Set.of(NEW_PHONE, OLD_PHONE))));
        assertThat(changedFields, hasEntry(EMAILS_MD5, new StringSetFieldChange(Set.of(OLD_EMAIL_MD5), Set.of(NEW_EMAIL_MD5, OLD_EMAIL_MD5))));
        assertThat(changedFields, hasEntry(PHONES_MD5, new StringSetFieldChange(Set.of(OLD_PHONE_MD5), Set.of(NEW_PHONE_MD5, OLD_PHONE_MD5))));
        assertThat(changedFields, hasEntry(MULTIVALUE_ATTRIBUTE, new StringSetFieldChange(Set.of(STRING_VALUE_1), Set.of(STRING_VALUE_1, STRING_VALUE_2, STRING_VALUE_3))));
    }

    @Test
    public void mergeBatchTest() {
        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setName(OLD_CLIENT_NAME);

        var newClientV1 = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClientV1.setName(NEW_CLIENT_NAME);

        var newBirthDate = LocalDate.now().minusDays(10);
        var newClientV2 = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClientV2.setBirthDate(newBirthDate);
        newClientV2.getAttributes().put(CUSTOM_ATTRIBUTE, Set.of(CUSTOM_STRING_VALUE));


        var uuid = UUID.randomUUID();
        var mergeResult = clientMerger.mergeBatch(
                List.of(
                        new ClientUpdate(newClientV1, UpdateType.SAVE, uuid, 1),
                        new ClientUpdate(newClientV2, UpdateType.UPDATE, uuid, 2)
                ),
                List.of(oldClient)
        ).get(oldClient.getKey());

        var client = mergeResult.getEntity();
        assertEquals(NEW_CLIENT_NAME, client.getName());
        assertEquals(newBirthDate, client.getBirthDate());
        assertEquals(Map.of(CUSTOM_ATTRIBUTE, Set.of(CUSTOM_STRING_VALUE)), client.getAttributes());

        var fieldsChanges = mergeResult.getChangesMeta().getFieldsChanges();
        assertThat(fieldsChanges, hasEntry(NAME, new StringFieldChange(OLD_CLIENT_NAME, NEW_CLIENT_NAME)));
        assertThat(fieldsChanges, hasEntry(BIRTH_DATE, new LocalDateFieldChange(null, newBirthDate)));
        assertThat(fieldsChanges, hasEntry(CUSTOM_ATTRIBUTE, new StringSetFieldChange(Set.of(), Set.of(CUSTOM_STRING_VALUE))));

    }
}
