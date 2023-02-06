package ru.yandex.autotests.morda.tests.any;

import org.apache.commons.lang3.RandomStringUtils;
import org.apache.log4j.Logger;
import org.junit.AssumptionViolatedException;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.RuleChain;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.exports.x404_redirects.X404RedirectsExport;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.core.UriBuilder;
import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.restassured.requests.Request.RequestAction.requestAction;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/06/16
 */
@Aqua.Test(title = "Редиректы any")
@Features({"Any", "x404_redirects"})
@RunWith(Parameterized.class)
public class AnyX404RedirectsTest {
    private static final Logger LOGGER = Logger.getLogger(AnyX404RedirectsTest.class);
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private static final String SAMPLE_PATH = "a/b/c";
    private static final String SAMPLE_QUERY = "q1=v1&q2=v2";

    @Rule
    public RuleChain rules = RuleChain.outerRule(new AllureLoggingRule());

    protected MordaClient mordaClient = new MordaClient();
    protected String fromUrl;
    protected String toUrl;

    public AnyX404RedirectsTest(String fromUrl, String toUrl) {
        this.fromUrl = fromUrl;
        this.toUrl = toUrl;
        prepareUrs();
    }

    @Parameterized.Parameters(name = "{0} -> {1}")
    public static Collection<String[]> data() {
        return new X404RedirectsExport().populate(DesktopMainMorda.desktopMain(CONFIG.pages().getEnvironment()).getUrl())
                .getData()
                .stream()
                .filter(e -> e.getSkipTest() == null || "0".equals(e.getSkipTest()))
                .map(e -> {
                    List<String[]> cases = new ArrayList<>();

                    String fromUrl = e.getFromUrl();
                    String toUrl = e.getToUrl();

                    if (fromUrl.startsWith("//")) {
                        cases.add(new String[]{normalize(fromUrl, "http"), normalize(toUrl, "http")});
                        cases.add(new String[]{normalize(fromUrl, "https"), normalize(toUrl, "https")});
                    } else {
                        cases.add(new String[]{fromUrl, normalize(toUrl, URI.create(fromUrl).getScheme())});
                    }
                    return cases;
                })
                .flatMap(Collection::stream)
                .collect(Collectors.toList());
    }

    private static String normalize(String url, String scheme) {
        if (url.startsWith("//")) {
            return scheme + ":" + url;
        }
        return url;
    }

    private void prepareUrs() {
        String randomParam = RandomStringUtils.random(20, true, false);
        String tmp = fromUrl;
        if (fromUrl.endsWith("*")) {
            fromUrl = fromUrl.replace("*", SAMPLE_PATH);
        }

        UriBuilder fromUrlBuilder = UriBuilder.fromUri(fromUrl)
                .queryParam("from_morda", randomParam);

        if (toUrl.contains("$request_uri")) {
            if (!tmp.endsWith("*")) {
                fromUrlBuilder.path(SAMPLE_PATH);
            }
            toUrl = toUrl.replace("$request_uri", SAMPLE_PATH);
        }

        if (toUrl.contains("$args")) {
            String q = SAMPLE_QUERY + "&from_morda=" + randomParam;
            fromUrlBuilder.replaceQuery(q);
            toUrl = toUrl.replace("$args", "?" + q);
        }

        fromUrl = fromUrlBuilder.build().toString();
    }

    @Test
    public void anyRedirect() throws Exception {
        mordaClient.any(CONFIG.getAnyHost(), CONFIG.getAnyEnvironment(), URI.create(fromUrl))
                .beforeRequest(requestAction(request -> {
                    LOGGER.info("START REQUEST");
                }))
                .afterRequest(requestAction(request -> {
                    LOGGER.info("END REQUEST");
                }))
                .readAsResponse()
                .then()
                .header("Location", equalTo(toUrl));
    }

    @Test
    public void plainRedirect() throws Exception {
        try {
            InetAddress inetAddress = InetAddress.getByName(URI.create(fromUrl).getHost());
            LOGGER.info("Resolved url to " + inetAddress.toString());
            new RestAssuredGetRequest(fromUrl)
                    .followRedirects(false)
                    .beforeRequest(requestAction(request -> {
                        LOGGER.info("START REQUEST");
                    }))
                    .afterRequest(requestAction(request -> {
                        LOGGER.info("END REQUEST");
                    }))
                    .readAsResponse()
                    .then()
                    .header("Location", equalTo(toUrl));

        } catch (UnknownHostException e) {
            throw new AssumptionViolatedException(e.getMessage(), e);
        }
    }
}
