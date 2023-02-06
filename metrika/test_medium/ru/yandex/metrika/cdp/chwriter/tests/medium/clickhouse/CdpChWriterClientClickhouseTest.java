package ru.yandex.metrika.cdp.chwriter.tests.medium.clickhouse;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.cdp.chwriter.spring.CdpChWriterTestConfig;
import ru.yandex.metrika.cdp.chwriter.tests.medium.AbstractCdpChWriterTest;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = CdpChWriterTestConfig.class)
public class CdpChWriterClientClickhouseTest extends AbstractCdpChWriterTest {

    @Test
    public void correctlyUpdatesDataByClientKey() throws InterruptedException {
        var initData = prepareSingleClient();
        dataSteps.writeClientKeys(initData.getClientKeys());

        dataSteps.waitClientsProcessing();

        var update = updateSingleClient(initData);

        testSteps.writeClientsAndCheckClickhouse(update);
    }

    @Test
    public void clientVersionsInChCorrespondVersionsInYdb() throws InterruptedException {
        var testData = prepareSingleClient();

        testSteps.writeClientsAndCheckVersionsInClickhouse(testData);
    }

    @Test
    public void correctlyProcessSingleClientKey() throws InterruptedException {
        var testData = prepareSingleClient();

        testSteps.writeClientsAndCheckClickhouse(testData);
    }

    @Test
    public void correctlyProcessCoupleClientKeys() throws InterruptedException {
        var testData = prepareTwoClients();

        testSteps.writeClientsAndCheckClickhouse(testData);
    }

}
