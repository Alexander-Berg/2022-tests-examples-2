package ru.yandex.metrika.cdp.core.tests.medium.ydb;

import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.core.spring.CdpCoreTestConfig;
import ru.yandex.metrika.cdp.core.tests.medium.AbstractCdpCoreTest;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;

import static org.assertj.core.api.Assertions.assertThat;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CdpCoreTestConfig.class)
public class ClientUpdateYdbTest extends AbstractCdpCoreTest {

    @Test
    public void correctlyProcessSingleClientSaveAndWriteToYdb() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        testSteps.writeClientUpdatesAndCheckYdb(clientUpdates);
    }

    @Test
    public void correctlyUpdatesSingleClientUpdateAndWriteToYdb() throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(List.of(CLIENT_SAVE));

        var clientUpdates = List.of(CLIENT_UPDATE);

        testSteps.writeClientUpdatesAndCheckYdb(clientUpdates);
    }

    @Test
    public void correctlySavesLastUploading() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = clientUpdates.stream().map(clientUpdate -> clientUpdate.getClient().getKey()).collect(Collectors.toList());

        var clientsFromYdb = dataSteps.readClientsFromYdb(clientKeys);

        var expected = clientUpdates.stream().map(ClientUpdate::getUploadingId).collect(Collectors.toList()).get(0);

        assertThat(clientsFromYdb).hasSize(1);
        assertThat(clientsFromYdb.get(0).getLastUploadings()).containsExactly(expected);
    }

    @Test
    public void correctlyUpdatesLastUploading() throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(List.of(CLIENT_SAVE));

        var clientUpdates = List.of(CLIENT_UPDATE);

        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = clientUpdates.stream().map(clientUpdate -> clientUpdate.getClient().getKey()).collect(Collectors.toList());

        var clientsFromYdb = dataSteps.readClientsFromYdb(clientKeys);

        assertThat(clientsFromYdb).hasSize(1);
        assertThat(clientsFromYdb.get(0).getLastUploadings()).hasSize(2);
        assertThat(clientsFromYdb.get(0).getLastUploadings()).containsExactly(CLIENT_SAVE.getUploadingId(), CLIENT_UPDATE.getUploadingId());
    }

    @Test
    public void correctlySavesSystemLastUploading() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        var someTimestampBeforeUploading = Instant.now();

        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = clientUpdates.stream().map(clientUpdate -> clientUpdate.getClient().getKey()).collect(Collectors.toList());

        var clientsFromYdb = dataSteps.readClientsFromYdb(clientKeys);

        assertThat(clientsFromYdb).hasSize(1);
        assertThat(clientsFromYdb.get(0).getSystemLastUpdate()).isAfterOrEqualTo(someTimestampBeforeUploading);
    }

    @Test
    public void correctlyUpdatesSystemLastUploading() throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(List.of(CLIENT_SAVE));

        var someTimestempAfterSaveAndBeforeUpdate = Instant.now();
        var clientUpdates = List.of(CLIENT_UPDATE);

        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = clientUpdates.stream().map(clientUpdate -> clientUpdate.getClient().getKey()).collect(Collectors.toList());

        var clientsFromYdb = dataSteps.readClientsFromYdb(clientKeys);

        assertThat(clientsFromYdb).hasSize(1);
        assertThat(clientsFromYdb.get(0).getSystemLastUpdate()).isAfterOrEqualTo(someTimestempAfterSaveAndBeforeUpdate);
    }
}
