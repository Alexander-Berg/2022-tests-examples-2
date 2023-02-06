package ru.yandex.metrika.cdp.chwriter.tests.medium.clickhouse;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.cdp.chwriter.spring.CdpChWriterTestConfig;
import ru.yandex.metrika.cdp.chwriter.tests.medium.AbstractCdpChWriterTest;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = CdpChWriterTestConfig.class)
public class CdpChWriterOrderClickhouseTest extends AbstractCdpChWriterTest {

    @Test
    public void orderVersionsInChCorrespondVersionsInYdb() throws InterruptedException {
        var testData = prepareSingleClient();

        testSteps.writeOrdersAndCheckVersionsInClickhouse(testData);
    }

    @Test
    public void correctlyProcessSingleOrderKey() throws InterruptedException {
        var testData = prepareSingleClient();

        testSteps.writeOrdersAndCheckClickhouse(testData);
    }

    @Test
    public void correctlyProcessCoupleOrderKeys() throws InterruptedException {
        var testData = prepareTwoClients();

        testSteps.writeOrdersAndCheckClickhouse(testData);
    }

    @Test
    public void correctlyUpdatesDataByOrderKey() throws InterruptedException {
        var initData = prepareSingleClient();

        dataSteps.writeOrderKeys(initData.getOrderKeys());

        dataSteps.waitOrdersProcessing();

        var update = updateSingleClient(initData);

        testSteps.writeOrdersAndCheckClickhouse(update);
    }

}
