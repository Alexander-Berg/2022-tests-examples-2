package ru.yandex.metrika.cdp.core.processing;

import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.UpdateType;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;

public class ClientMergerLastUploadingsTest extends AbstractClientMergerTest {
    @Test
    public void savesHistoryOfNewClient() {
        var newClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);

        var result = clientMerger.merge(newClient, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);

        var lastUploadings = result.getEntity().getLastUploadings();
        assertThat(lastUploadings, hasSize(1));
        assertThat(lastUploadings, hasItem(equalTo(UPLOADING_ID_1)));
    }

    @Test
    public void correctlySavesUploadingsHistory() {

        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setName(OLD_CLIENT_NAME);

        var newClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);

        var firstMerge = clientMerger.merge(oldClient, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var secondMerge = clientMerger.merge(newClient, firstMerge.getEntity(), UpdateType.SAVE, Set.of(), UPLOADING_ID_2);

        var lastUploadings = secondMerge.getEntity().getLastUploadings();
        assertThat(lastUploadings, hasSize(2));
        assertThat(lastUploadings, contains(equalTo(UPLOADING_ID_1), equalTo(UPLOADING_ID_2)));
    }

    @Test
    public void keepsOnlyLastUploadingsWhenReachMaxSize() {
        Client.setLastUploadingsSize(2);

        var oldClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        oldClient.setName(OLD_CLIENT_NAME);

        var newClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);

        var theNewestClient = new Client(1L, 1, "", EntityStatus.ACTIVE, ClientType.CONTACT);
        newClient.setName(NEW_CLIENT_NAME);

        var firstMerge = clientMerger.merge(oldClient, null, UpdateType.SAVE, Set.of(), UPLOADING_ID_1);
        var secondMerge = clientMerger.merge(newClient, firstMerge.getEntity(), UpdateType.SAVE, Set.of(), UPLOADING_ID_2);
        var thirdMerge = clientMerger.merge(theNewestClient, secondMerge.getEntity(), UpdateType.SAVE, Set.of(), UPLOADING_ID_3);


        var lastUploadings = thirdMerge.getEntity().getLastUploadings();
        assertThat(lastUploadings, hasSize(2));
        assertThat(lastUploadings, contains(equalTo(UPLOADING_ID_2), equalTo(UPLOADING_ID_3)));
    }

}
