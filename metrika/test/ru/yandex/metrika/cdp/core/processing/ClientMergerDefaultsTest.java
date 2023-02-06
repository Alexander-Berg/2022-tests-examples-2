package ru.yandex.metrika.cdp.core.processing;

import java.time.Instant;
import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class ClientMergerDefaultsTest extends AbstractClientMergerTest{

    @Test
    public void setDefaultCreateDateTimeWhenOldIsNullTest() {

        var newClient = getNewClient();
        newClient.setCreateDateTime(null);

        var mergeResult = clientMerger.merge(newClient, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertNotNull(mergeResult.getEntity().getCreateDateTime());

    }

    @Test
    public void setDefaultCreateDateTimeWhenOldCreateDateTimeIsNullTest() {

        var oldClient = getOldClient();
        oldClient.setCreateDateTime(null);

        var newClient = getNewClient();
        newClient.setCreateDateTime(null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertNotNull(mergeResult.getEntity().getCreateDateTime());

    }

    @Test
    public void setDefaultCreateDateTimeFromOldCreateDateTimeTest() {

        var oldClient = getOldClient();
        oldClient.setCreateDateTime(Instant.now());

        var newClient = getNewClient();
        newClient.setCreateDateTime(null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertNotNull(mergeResult.getEntity().getCreateDateTime());

    }

    @Test
    public void setDefaultWhenCreateDateTimeIsNotNull() {

        var oldClient = getOldClient();

        var now = Instant.now();
        var newClient = getNewClient();
        newClient.setCreateDateTime(now);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertEquals(now, mergeResult.getEntity().getCreateDateTime());

    }

    @Test
    public void setDefaultUpdateDateTimeWhenOldIsNullTest() {

        var newClient = getNewClient();
        newClient.setUpdateDateTime(null);

        var mergeResult = clientMerger.merge(newClient, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertNotNull(mergeResult.getEntity().getUpdateDateTime());

    }

    @Test
    public void setDefaultUpdateDateTimeWhenOldCreateDateTimeIsNullTest() {

        var oldClient = getOldClient();
        oldClient.setUpdateDateTime(null);

        var newClient = getNewClient();
        newClient.setUpdateDateTime(null);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertNotNull(mergeResult.getEntity().getUpdateDateTime());

    }

    @Test
    public void setDefaultWhenUpdateDateTimeIsNotNull() {

        var createDateTime = Instant.now().minusSeconds(10);

        var oldClient = getOldClient();
        oldClient.setCreateDateTime(createDateTime);

        var now = Instant.now();
        var newClient = getNewClient();
        oldClient.setCreateDateTime(createDateTime);
        newClient.setUpdateDateTime(now);

        var mergeResult = clientMerger.merge(newClient, oldClient, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        assertEquals(now, mergeResult.getEntity().getUpdateDateTime());

    }
}
