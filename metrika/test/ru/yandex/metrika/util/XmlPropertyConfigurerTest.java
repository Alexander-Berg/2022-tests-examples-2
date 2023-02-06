package ru.yandex.metrika.util;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Properties;

import org.junit.Rule;
import org.junit.Test;
import org.junit.contrib.java.lang.system.EnvironmentVariables;

import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */
public class XmlPropertyConfigurerTest {

    @Rule
    public final EnvironmentVariables environmentVariables = new EnvironmentVariables();

    @Test
    public void testAttribute() {
        String config = "<?xml version=\"1.0\"?>\n" +
                "<yandex>\n" +
                "        <settings>\n" +
                "                <daemonRoot>/opt/yandex/filterd</daemonRoot>\n" +
                "        </settings>\n" +
                "        <mysql_counters>\n" +
                "                <host>mtacs01c</host>\n" +
                "                <port>3310</port>\n" +
               "                <user>metrika</user>\n" +
                "                <db>conv_main</db>\n" +
                "        </mysql_counters>\n" +
                "        <mysql_variables>\n" +
                "                <host>localhost</host>\n" +
                "                <port>3306</port>\n" +
                "                <user>metrika</user>\n" +
                "                <db>variables</db>\n" +
                "        </mysql_variables>\n" +
                "        <filterdSegmented>\n" +
                "                <layer index=\"1\">\n" +
                "                        <mysql_visor_events>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>webvisorlog_01</db>\n" +
                "                        </mysql_visor_events>\n" +
                "                        <mysql_visor_event_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_events_01</db>\n" +
                "                        </mysql_visor_event_filtered>\n" +
                "                        <mysql_visor_page_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_pages_01</db>\n" +
                "                        </mysql_visor_page_filtered>\n" +
                "                </layer>        " +
                "                <layer index=\"2\">\n" +
                "                        <mysql_visor_events>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>webvisorlog_01</db>\n" +
                "                        </mysql_visor_events>\n" +
                "                        <mysql_visor_event_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_events_01</db>\n" +
                "                        </mysql_visor_event_filtered>\n" +
                "                        <mysql_visor_page_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_pages_01</db>\n" +
                "                        </mysql_visor_page_filtered>\n" +
                "                </layer>        " +
                "        </filterdSegmented>\n" +
                "        <jmxServerConnector>\n" +
                "                <serviceUrl>service:jmx:jmxmp://localhost:9005</serviceUrl>\n" +
                "        </jmxServerConnector>\n" +
                "</yandex>\n";

        String config2 = "<?xml version=\"1.0\"?>\n" +
                "<yandex>\n" +
                "        <settings>\n" +
                "                <daemonRoot>/opt/yandex/filterd</daemonRoot>\n" +
                "        </settings>\n" +
                "        <mysql_counters>\n" +
                "                <host>mtacs01c</host>\n" +
                "                <port>3310</port>\n" +
                "                <user>metrika</user>\n" +
                "                <db>conv_main</db>\n" +
                "        </mysql_counters>\n" +
                "        <mysql_variables>\n" +
                "                <host>localhost</host>\n" +
                "                <port>3306</port>\n" +
                "                <user>metrika</user>\n" +
                "                <db>variables</db>\n" +
                "        </mysql_variables>\n" +
                "        <filterdSegmented>\n" +
                "                <layer>\n" +
                "                        <index>1</index>" +
                "                        <mysql_visor_events>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>webvisorlog_01</db>\n" +
                "                        </mysql_visor_events>\n" +
                "                        <mysql_visor_event_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_events_01</db>\n" +
                "                        </mysql_visor_event_filtered>\n" +
                "                        <mysql_visor_page_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_pages_01</db>\n" +
                "                        </mysql_visor_page_filtered>\n" +
                "                </layer>        " +
                "                <layer>\n" +
                "                        <index>2</index>" +
                "                        <mysql_visor_events>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>webvisorlog_01</db>\n" +
                "                        </mysql_visor_events>\n" +
                "                        <mysql_visor_event_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_events_01</db>\n" +
                "                        </mysql_visor_event_filtered>\n" +
                "                        <mysql_visor_page_filtered>\n" +
                "                                <host>localhost</host>\n" +
                "                                <port>3306</port>\n" +
                "                                <user>metrika</user>\n" +
                "                                <db>visor_pages_01</db>\n" +
                "                        </mysql_visor_page_filtered>\n" +
                "                </layer>        " +
                "        </filterdSegmented>\n" +
                "        <jmxServerConnector>\n" +
                "                <serviceUrl>service:jmx:jmxmp://localhost:9005</serviceUrl>\n" +
                "        </jmxServerConnector>\n" +
                "</yandex>\n";

        Properties properties = XmlPropertyConfigurer.readXml(new ByteArrayInputStream(config.getBytes(StandardCharsets.UTF_8)));
        Properties properties2 = XmlPropertyConfigurer.readXml(new ByteArrayInputStream(config2.getBytes(StandardCharsets.UTF_8)), Collections.singletonList("index"));
        assertEquals(properties, properties2);
        System.out.println(properties);
        System.out.println(properties2);
    }
}
