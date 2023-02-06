package ru.yandex.metrika.api.management.tests.medium.client;

import java.util.List;

import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.MessengerService;
import ru.yandex.metrika.api.management.client.external.Messenger;
import ru.yandex.metrika.api.management.config.MessengerServiceConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class MessengerServiceTest {

    @Autowired
    public MessengerService messengerService;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Test
    public void checkThatReloadMethodGetsDataFromDb() {
        messengerService.reload();
        List<Messenger> messengers = messengerService.getMessengers();

        Assert.assertNotNull(messengers);
        Assert.assertTrue(messengers.size() > 0);
    }

    @Configuration
    @Import(MessengerServiceConfig.class)
    static class Config {}
}
