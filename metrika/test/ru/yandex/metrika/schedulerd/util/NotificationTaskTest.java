package ru.yandex.metrika.schedulerd.util;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.mail.MessageQueue;
import ru.yandex.metrika.schedulerd.cron.task.NotificationTask;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

/**
 * Created by orantius on 3/19/15.
 */
@Ignore
public class NotificationTaskTest {
    NotificationTask target;

    @Before
    public void setUp() throws Exception {
        target = new NotificationTask();
        target.setSmtpHost("localhost");
        target.setSmtpPort(1027);
        MessageQueue messageQueue = new MessageQueue();
        messageQueue.setTemplate(AllDatabases.getTemplate("localhost", 3415, "metrica", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_new"), "monitoring"));
        messageQueue.afterPropertiesSet();
        target.setMessageQueue(messageQueue);

    }

    @Test
    public void testSend() throws Exception {
        target.send();
    }
}
