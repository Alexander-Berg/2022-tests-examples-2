package ru.yandex.autotests.morda.mordaspecialtests.js;

import org.apache.log4j.Logger;
import org.glassfish.jersey.client.ClientProperties;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.morda.mordaspecialtests.Properties;
import ru.yandex.autotests.morda.mordaspecialtests.data.ProjectInfo;
import ru.yandex.autotests.morda.mordaspecialtests.utils.DataUtils;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.net.URI;
import java.util.Collection;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.lessThan;

/**
 * Created by eoff on 09/10/14.
 */
@Aqua.Test(title = "Response Code", description = "")
@RunWith(Parameterized.class)
@Feature("Response Code")
public class ResponseTest {
    private static final Properties CONFIG = new Properties();
    public static final Logger LOG = Logger.getLogger(ResponseTest.class);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(DataUtils.getData(CONFIG.isRc()));
    }

    private ProjectInfo.ProjectInfoCase projectInfoCase;
    private String url;

    public ResponseTest(ProjectInfo.ProjectInfoCase projectInfoCase) {
        this.projectInfoCase = projectInfoCase;
        this.url = (CONFIG.isRc()) ? projectInfoCase.getTest() : projectInfoCase.getProd();
    }

    @Test
    public void responseCode() throws IOException {
        Client client = MordaClient.getJsonEnabledClient();

        client.property(ClientProperties.CONNECT_TIMEOUT, 1000);
        client.property(ClientProperties.READ_TIMEOUT,    1000);

        Response response = client.target(URI.create(url)).request().buildGet().invoke();
        int code = response.getStatus();
        response.close();

        assertThat("Response code = " + code, code, lessThan(400));
    }

}
