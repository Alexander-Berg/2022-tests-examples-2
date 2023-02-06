package ru.yandex.metrika.cdp.core.processing;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import javax.annotation.Nonnull;

import com.google.common.collect.Lists;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.core.merge.FieldInfo;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.util.collections.F;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.CREATE_DATE_TIME_FIELD_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.SIMPLE_FIELDS_INFO;
import static ru.yandex.metrika.cdp.core.processing.ClientMerger.UPDATE_DATE_TIME_FIELD_INFO;

@RunWith(Parameterized.class)
public class ClientMergerSettedSimpleFieldsTest extends AbstractClientMergerTest {

    @Parameterized.Parameter(0)
    public UpdateType updateType;

    @Parameterized.Parameter(1)
    public FieldInfo<Client, ?> fieldInfo;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> operatingSystems() {
        return Lists.cartesianProduct(
                Arrays.asList(UpdateType.values()),
                // для create_date_time и update_date_time мы выставляем дефолты в Merger-e так что они всегда не null
                F.filter(SIMPLE_FIELDS_INFO, fi -> !Set.of(CREATE_DATE_TIME_FIELD_INFO, UPDATE_DATE_TIME_FIELD_INFO).contains(fi))
        ).stream().map(List::toArray).collect(Collectors.toList());
    }

    @Test
    public void testMerge() {
        var oldClient = getOldClient();
        assertNotNull(fieldInfo.getter.apply(oldClient));

        var newClient = getNewClient();
        fieldInfo.setter.accept(newClient, null);

        var mergeResult = clientMerger.merge(newClient, oldClient, updateType, Set.of(fieldInfo.fieldId), UPLOADING_ID_1);
        assertNull(fieldInfo.getter.apply(mergeResult.getEntity()));
    }

    @Nonnull
    protected static Client getNewClient() {
        return new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
    }

    @Nonnull
    protected static Client getOldClient() {
        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setParentCdpUid(2L);
        oldClient.setName(OLD_CLIENT_NAME);
        oldClient.setBirthDate(LocalDate.now().minusDays(10));
        oldClient.setCreateDateTime(Instant.now());
        oldClient.setUpdateDateTime(Instant.now());
        return oldClient;
    }


}
