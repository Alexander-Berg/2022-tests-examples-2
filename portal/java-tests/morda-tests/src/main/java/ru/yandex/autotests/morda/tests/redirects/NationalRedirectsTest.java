package ru.yandex.autotests.morda.tests.redirects;

import com.jayway.restassured.http.ContentType;
import com.jayway.restassured.response.Response;
import org.apache.http.HttpHost;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.client.utils.URIUtils;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.log4j.Logger;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.autotests.morda.utils.cookie.HttpClientCookieUtils;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collection;
import java.util.List;
import java.util.Spliterator;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Spliterators.spliteratorUnknownSize;
import static java.util.stream.Collectors.toList;
import static java.util.stream.StreamSupport.stream;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 02.03.17
 */
@Aqua.Test(title = "National redirects")
@RunWith(Parameterized.class)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.REDIRECTS})
public class NationalRedirectsTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private static final Logger LOGGER = Logger.getLogger(NationalRedirectsTest.class);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        //m("clid", "12345").
        return Stream.of(MINSK, KYIV, ASTANA)
                .map(region -> desktopMain(CONFIG.pages().getEnvironment()).region(region))
                .collect(toList());
    }

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private DesktopMainMorda morda;
    private MordaClient mordaClient;
    private DesktopMainMorda ruMorda;

    public NationalRedirectsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaClient = new MordaClient();
        this.ruMorda = desktopMain(CONFIG.pages().getEnvironment());
    }

    @Test
    public void shouldSee302Code() {
        Response response = mordaClient.morda(ruMorda)
                .cookie("yandex_gid", String.valueOf(morda.getRegion().getRegionId()))
                .followRedirects(false)
                .invoke();
        assertThat("Должно вернуться 302", response.getStatusCode(), equalTo(302));
    }

    @Test
    public void shouldRedirectFromRu() throws IOException, URISyntaxException {
        HttpClient httpClient = HttpClientBuilder.create().build();
        HttpClientCookieUtils cookieUtils = cookieUtils(httpClient);
        cookieUtils
                .addCookie("yandex_gid", String.valueOf(morda.getRegion().getRegionId()), ".yandex.ru");

        HttpClientContext context = HttpClientContext.create();
        HttpGet method = new HttpGet(ruMorda.getUrl().toString());
        method.addHeader("User-Agent", CONFIG.pages().getDesktopUserAgent());
        method.addHeader("Accept", ContentType.ANY.toString());
        method.addHeader("Content-Type", ContentType.ANY.toString());

        LOGGER.info(curlFormat(method, cookieUtils).toString());
        HttpResponse response = httpClient.execute(method, context);
        LOGGER.info(response.getStatusLine());

        List<URI> redirectPath = context.getRedirectLocations();
        URI lastRedirectUri = URIUtils.resolve(ruMorda.getUrl(),
                new HttpHost(morda.getUrl().getHost()), redirectPath);

        assertThat("Должно редиректить на " + morda.getUrl(),
                lastRedirectUri.toString(), startsWith(morda.getUrl().toString()));
    }


    private StringBuilder curlFormat(HttpRequestBase httpRequestBase, HttpClientCookieUtils cookieUtils) {
        StringBuilder data = new StringBuilder();
        try {
            return data.append("curl -vLskX ")
                    .append(httpRequestBase.getMethod())
                    .append(" '").append(httpRequestBase.getURI()).append("' ")
                    .append(headersFormat(httpRequestBase)).append(" ")
                    .append(cookiesFormat(cookieUtils)).append(" ");
//                    .append(bodyFormat(requestSpec));
        } catch (Throwable t) {
            System.out.println("Can't construct curl string\n" + t.getMessage());
            return data;
        }
    }

    private static String headersFormat(HttpRequestBase httpRequestBase) {
        return Stream.of(httpRequestBase.getAllHeaders())
                .map(e -> "-H '" + e.getName() + ": " + e.getValue() + "'")
                .collect(Collectors.joining(" "));
    }

    private static String cookiesFormat(HttpClientCookieUtils cookieUtils) {
        if (cookieUtils.getCookies().size() > 0) {
            String cookieString = stream(spliteratorUnknownSize(cookieUtils.getCookies().iterator(), Spliterator.ORDERED), false)
                    .map(e -> e.getName() + "=" + e.getValue())
                    .collect(Collectors.joining("; "));
            return "-b '" + cookieString + "'";
        } else {
            return "";
        }
    }

//    private static String bodyFormat(FilterableRequestSpecification requestSpec) throws JsonProcessingException {
//        if (requestSpec.getBody() != null && (requestSpec.getMethod().equals(POST) || requestSpec.getMethod().equals(PUT))) {
//            return new StringBuilder("-d '")
//                    .append(requestSpec.getBody().toString())
//                    .append("'").toString();
//        }
//        return "";
//    }

}
