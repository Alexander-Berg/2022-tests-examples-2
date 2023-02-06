package ru.yandex.metrika.cdp.chwriter.tests.medium.ydb;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import ru.yandex.metrika.cdp.chwriter.spring.CdpChWriterTestConfig;
import ru.yandex.metrika.cdp.chwriter.tests.medium.AbstractCdpChWriterTest;

@RunWith(SpringRunner.class)
@WebAppConfiguration
@ContextConfiguration(classes = CdpChWriterTestConfig.class)
public class YdbVersionsTest extends AbstractCdpChWriterTest {

    @Test
    public void correctlyIncrementsOrderVersionInYdb() {
        var testData = prepareSingleClient();

        testSteps.writeOrdersAndCheckYdb(testData);
    }

    @Test
    public void correctlyIncrementsClientVersionInYdb() {
        var testData = prepareSingleClient();

        testSteps.writeClientsAndCheckYdb(testData);
    }
}
