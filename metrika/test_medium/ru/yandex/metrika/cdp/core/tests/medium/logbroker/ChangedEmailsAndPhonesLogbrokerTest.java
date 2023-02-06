package ru.yandex.metrika.cdp.core.tests.medium.logbroker;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.core.spring.CdpCoreTestConfig;
import ru.yandex.metrika.cdp.core.tests.medium.AbstractCdpCoreTest;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CdpCoreTestConfig.class)
public class ChangedEmailsAndPhonesLogbrokerTest extends AbstractCdpCoreTest {

    @Before
    public void cleanTopics() {
        dataSteps.clearChangedEmailsAndPhonesClientKeysTopic();
    }

    @Test
    public void correctlyWritesChangedClientIdAfterClientSave() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        testSteps.writeClientUpdatesAndCheckTopicWithChangedEmailsAndPhones(clientUpdates, List.of(CLIENT_SAVE.getClient().getKey()));
    }

    @Test
    public void correctrlyWirtesChangedClientIdAfterClientUpdate() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE, CLIENT_UPDATE);

        testSteps.writeClientUpdatesAndCheckTopicWithChangedEmailsAndPhones(clientUpdates, List.of(CLIENT_SAVE.getClient().getKey(), CLIENT_UPDATE.getClient().getKey()));
    }
}
