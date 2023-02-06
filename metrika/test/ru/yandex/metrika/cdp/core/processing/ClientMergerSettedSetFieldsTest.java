package ru.yandex.metrika.cdp.core.processing;

import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.core.merge.FieldInfo;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.CLIENT_IDS_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.CLIENT_USER_IDS_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.EMAILS_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.EMAILS_MD5_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.PHONES_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.PHONES_MD5_FIELD_INFO;

@RunWith(Parameterized.class)
public class ClientMergerSettedSetFieldsTest extends AbstractClientMergerTest {


    @Parameterized.Parameter(0)
    public FieldInfo<Client, Set<?>> fieldInfo;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> operatingSystems() {
        return List.of(
                CLIENT_IDS_FIELD_INFO, CLIENT_USER_IDS_FIELD_INFO, EMAILS_FIELD_INFO, PHONES_FIELD_INFO, EMAILS_MD5_FIELD_INFO, PHONES_MD5_FIELD_INFO
        ).stream().map(fi -> new Object[]{fi}).collect(Collectors.toList());

    }

    @Test
    public void testSaveMerge() {
        var oldClient = getOldClient();
        assertNotNull(fieldInfo.getter.apply(oldClient));

        var newClient = getNewClient();
        fieldInfo.setter.accept(newClient, null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(fieldInfo.fieldId), UPLOADING_ID_1);
        assertNull(fieldInfo.getter.apply(mergeResult.getEntity()));
    }

    @Test
    public void testUpdateMerge() {
        var oldClient = getOldClient();
        assertNotNull(fieldInfo.getter.apply(oldClient));

        var newClient = getNewClient();
        fieldInfo.setter.accept(newClient, null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.UPDATE, Set.of(fieldInfo.fieldId), UPLOADING_ID_1);
        assertNull(fieldInfo.getter.apply(mergeResult.getEntity()));
    }

    @Test
    public void testAppendMerge() {
        var oldClient = getOldClient();
        assertNotNull(fieldInfo.getter.apply(oldClient));

        var newClient = getNewClient();
        fieldInfo.setter.accept(newClient, null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.APPEND, Set.of(fieldInfo.fieldId), UPLOADING_ID_1);
        assertNotNull(fieldInfo.getter.apply(mergeResult.getEntity()));
        assertEquals(fieldInfo.getter.apply(oldClient), fieldInfo.getter.apply(mergeResult.getEntity()));
    }


}
