package ru.yandex.metrika.cdp.core.processing;

import java.time.LocalDate;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nonnull;

import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;

import static ru.yandex.metrika.util.StringUtil.stringMd5;

public abstract class AbstractClientMergerTest {

    protected static final String CLIENT_USER_ID_1 = "client_user_id_1";
    protected static final String CLIENT_USER_ID_2 = "client_user_id_2";

    protected static final String OLD_CLIENT_NAME = "Bob";
    protected static final String OLD_EMAIL = "example@example.com";
    protected static final String OLD_EMAIL_MD5 = stringMd5(OLD_EMAIL);
    protected static final String OLD_PHONE = "+78001234567";
    protected static final String OLD_PHONE_MD5 = stringMd5(OLD_PHONE);

    protected static final String NEW_CLIENT_NAME = "Jack";
    protected static final String NEW_EMAIL = "new-example@example.com";
    protected static final String NEW_EMAIL_MD5 = stringMd5(NEW_EMAIL);
    protected static final String NEW_PHONE = "+79001234567";
    protected static final String NEW_PHONE_MD5 = stringMd5(NEW_PHONE);

    protected static final String MULTIVALUE_ATTRIBUTE = "multivalue_custom_attribute";
    protected static final String CUSTOM_ATTRIBUTE = "custom_attribute";

    protected static final String STRING_VALUE_1 = "value1";
    protected static final String STRING_VALUE_2 = "value2";
    protected static final String STRING_VALUE_3 = "value3";
    protected static final String CUSTOM_STRING_VALUE = "custom_value";

    protected static final UUID UPLOADING_ID_1 = UUID.randomUUID();
    protected static final UUID UPLOADING_ID_2 = UUID.randomUUID();
    protected static final UUID UPLOADING_ID_3 = UUID.randomUUID();

    protected final ClientMerger clientMerger = new ClientMerger(
            (counterId, entityNamespace, attributeName) -> attributeName.equals(MULTIVALUE_ATTRIBUTE)
    );


    @Nonnull
    protected static Client getNewClient() {
        var newClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);
        newClient.setBirthDate(LocalDate.now().minusDays(10));
        newClient.setClientIds(Set.of(2L, 3L, 4L));
        newClient.setEmails(Set.of(NEW_EMAIL));
        newClient.setPhones(Set.of(NEW_PHONE));
        newClient.setEmailsMd5(Set.of(NEW_EMAIL_MD5));
        newClient.setPhonesMd5(Set.of(NEW_PHONE_MD5));
        newClient.setAttributes(Map.of(
                MULTIVALUE_ATTRIBUTE, Set.of(STRING_VALUE_2, STRING_VALUE_3)
        ));
        return newClient;
    }

    @Nonnull
    protected static Client getOldClient() {
        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setParentCdpUid(2L);
        oldClient.setName(OLD_CLIENT_NAME);
        oldClient.setClientIds(Set.of(1L, 2L, 3L));
        oldClient.setClientUserIds(Set.of(CLIENT_USER_ID_1, CLIENT_USER_ID_2));
        oldClient.setEmails(Set.of(OLD_EMAIL));
        oldClient.setPhones(Set.of(OLD_PHONE));
        oldClient.setEmailsMd5(Set.of(OLD_EMAIL_MD5));
        oldClient.setPhonesMd5(Set.of(OLD_PHONE_MD5));
        oldClient.setAttributes(Map.of(
                MULTIVALUE_ATTRIBUTE, Set.of(STRING_VALUE_1),
                CUSTOM_ATTRIBUTE, Set.of(CUSTOM_STRING_VALUE)
        ));
        return oldClient;
    }
}
