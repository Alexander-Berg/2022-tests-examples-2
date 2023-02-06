package ru.yandex.autotests.mordatmplerr.logs;

import org.apache.commons.lang.StringUtils;
import org.junit.Test;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.net.URI;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.03.14
 */
@Aqua.Test(title = "Check-files Logs")
@Features("Check-files Logs")
public class CheckFilesLogsTest {
    private static final Properties CONFIG = new Properties();
    private static final String CHECK_FILES_URL =
            "http://" + CONFIG.getMordaEnv()+ ".yandex.ru/morda-kitty-check-files.error_log";

    @Test
    public void logs() throws Exception {
        Client client = MordaClient.getJsonEnabledClient();
        String response = client.target(URI.create(CHECK_FILES_URL)).request().buildGet().invoke().readEntity(String.class);
        if (response.length() > 0) {
            List<String> res = Arrays.asList(response.split("\n"));
            assertThat("check-files found errors:\n" + StringUtils.join(res, "\n"), res, hasSize(0));
        }
    }
}
