package ru.yandex.taxi.ququmber;

import org.junit.jupiter.api.Assertions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.taxi.ququmber.tickets.ChatterboxTransmitEventConfig;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class}
)
public class ChatterboxTransmitEventConfigTest {

    @Autowired
    ChatterboxTransmitEventConfig chatterboxTransmitEventConfig;

    public void testConfig() {
        Assertions.assertTrue(chatterboxTransmitEventConfig.isB2bInvoiceRemindEnabled());
        Assertions.assertTrue(chatterboxTransmitEventConfig.isB2bPreorderEnabled());
    }
}
