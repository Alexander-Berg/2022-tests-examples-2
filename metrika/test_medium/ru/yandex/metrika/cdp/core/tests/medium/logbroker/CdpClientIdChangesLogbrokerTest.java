package ru.yandex.metrika.cdp.core.tests.medium.logbroker;

import java.util.List;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.core.spring.CdpCoreTestConfig;
import ru.yandex.metrika.cdp.core.tests.medium.AbstractCdpCoreTest;

import static ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange.add;


@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CdpCoreTestConfig.class)
public class CdpClientIdChangesLogbrokerTest extends AbstractCdpCoreTest {

    @Before
    public void cleanTopics() {
        dataSteps.clearClientIdChangeTopic();
    }

    @Test
    public void correctlyWritesCdpClientIdChangesAfterClientSave() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        var expected = CLIENT_SAVE.getClient().getClientIds().stream()
                .map(clientId -> add(clientId, CLIENT.getCounterId(), CLIENT.getCdpUid())).collect(Collectors.toList());

        testSteps.writeClientUpdatesAndCheckTopicWithChangedClientId(clientUpdates, expected);
    }

    @Test
    public void correctlyWritesCdpClientIdChangesAfterClientUpdate() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE, CLIENT_UPDATE);

        var expected = CLIENT_SAVE.getClient().getClientIds().stream()
                .map(clientId -> add(clientId, CLIENT.getCounterId(), CLIENT.getCdpUid())).collect(Collectors.toList());

        expected.addAll(List.of(ADD_CDP_CLIENT_ID, REMOVE_CDP_CLIENT_ID));

        testSteps.writeClientUpdatesAndCheckTopicWithChangedClientId(clientUpdates, expected);
    }
}
