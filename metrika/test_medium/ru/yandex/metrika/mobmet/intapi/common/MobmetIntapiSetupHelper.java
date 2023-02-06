package ru.yandex.metrika.mobmet.intapi.common;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.io.UncheckedIOException;

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;
import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.common.test.medium.FreemarkerUtils.renderTemplate;

/**
 * Инициализиция ресурсов поднятых с помощью рецептов, конфигов нужно сделать один раз.
 * Поэтому делаем всё на статике как в старые добрые времена.
 * В junit5 можно было бы использовать ExtendWith
 * Ещё можно будет делать вот так: https://stackoverflow.com/a/56380283
 * тогда не придётся собирать ClickHouseDataSource руками
 */
public class MobmetIntapiSetupHelper {

    private static final Logger log = LoggerFactory.getLogger(MobmetIntapiSetupHelper.class);

    private static volatile boolean setupDone = false;

    private MobmetIntapiSetupHelper() {
    }

    public static void setup() {
        if (!setupDone) {
            synchronized (MobmetIntapiSetupHelper.class) {
                if (!setupDone) {
                    setupLogger();
                    setupDaemon();
                    setupDone = true;
                }
            }
        }
    }

    private static void setupLogger() {
        MediumTestsLogSetup.setup();
    }

    private static void setupDaemon() {
        String configFile = getBuildPath("config.xml");
        log.info("Сonfig file: {}", configFile);

        Map<String, String> variables = new HashMap<>();
        variables.put("DAEMON_ROOT", getBuildPath("daemon_root"));
        variables.put("targetHost", "localhost");
        variables.put("jmxPort", valueOf(findAvailableTcpPort()));
        variables.putAll(System.getenv());

        variables.put("TVM_SELF_CLIENT_ID", String.valueOf(TestTvmServices.SELF.getClientId()));
        variables.put("TVM_SELF_SECRET", TestTvmServices.SELF.getSecret());
        try {
            variables.put("TVM_API_PORT", Files.readString(Paths.get("tvmapi.port")));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configFile))) {
            writer.write(renderTemplate("/ru/yandex/metrika/mobmet/intapi/common", "config.conf.ftl", variables));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }

        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configFile);
        System.setProperty("jmxDefaultDomain", MobmetIntapiSetupHelper.class.getName());
    }
}
