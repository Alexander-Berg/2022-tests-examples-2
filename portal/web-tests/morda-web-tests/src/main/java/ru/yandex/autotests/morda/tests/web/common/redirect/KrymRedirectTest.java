package ru.yandex.autotests.morda.tests.web.common.redirect;

import org.apache.http.HttpHost;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.client.utils.URIUtils;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.glassfish.jersey.client.ClientProperties;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.cookie.ClientCookieUtils;
import ru.yandex.autotests.morda.utils.cookie.HttpClientCookieUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

import static javax.ws.rs.core.Response.Status.FOUND;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.utils.client.MordaClientBuilder.mordaClient;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 19.04.16
 */
@Aqua.Test(title = "Krym redirect")
@Features("Redirect")
@Stories("Krym redirect")
@RunWith(Parameterized.class)
public class KrymRedirectTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {

        Collection<Object[]> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        URI mordaUri = desktopMain(scheme, environment, MOSCOW).getUrl();
        URI mordaUriWithClid = fromUri(mordaUri).queryParam("clid", "12345").build();

        Stream.of(mordaUri, mordaUriWithClid)
                .forEach(e ->
                                data.add(new Object[]{"Simferopol", e})
                );

        return data;
    }

    private URI uri;
    private long timestamp;

    public KrymRedirectTest(String city, URI uri) {
        this.uri = uri;
    }

    @Before
    public void init() {
        LocalDateTime expiry = LocalDateTime.now().plusMonths(6);
        timestamp = expiry.toEpochSecond(ZoneOffset.systemDefault().getRules().getOffset(expiry));
    }

    @Test
    public void responseCodeTest() {
        Client client = mordaClient()
                .withLogging(true)
                .build();

        ClientCookieUtils utils = cookieUtils(client);
        utils.addCookie("yp", timestamp + ".cr.ua", ".yandex.ru");
        utils.addCookie("yandex_gid", "146", ".yandex.ru");

        Response response = client.target(uri)
                .request()
                .buildGet()
                .property(ClientProperties.FOLLOW_REDIRECTS, Boolean.FALSE)
                .invoke();

        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
        assertThat("Плохой код ответа от \"" + uri + "\"", status, equalTo(FOUND));

        response.close();
        client.close();
    }

    @Test
    public void targetUriTest() throws IOException, URISyntaxException {
        String host = uri.getHost().replace(".ru", ".ua");
        final String YANDEX_UA  = fromUri(uri)
                .scheme(uri.getScheme())
                .host(host)
                .replaceQuery("")
                .build().toString();

        CloseableHttpClient httpClient = HttpClientBuilder.create().build();

        HttpClientCookieUtils utils = cookieUtils(httpClient);
        utils.addCookie("yp", timestamp + ".cr.ua", ".yandex.ru");
        utils.addCookie("yp", timestamp + ".cr.ua", ".yandex.ua");
        utils.addCookie("yandex_gid", "146", ".yandex.ru");
        utils.addCookie("yandex_gid", "146", ".yandex.ua");

        HttpClientContext context = HttpClientContext.create();

        CloseableHttpResponse response = httpClient.execute(new HttpGet(uri), context);

        List<Cookie> setCookies = context.getCookieStore().getCookies();

        List<URI> redirectPath = context.getRedirectLocations();
        URI targetUri = URIUtils.resolve(uri, new HttpHost(YANDEX_UA), redirectPath);

        assertThat("Код не тот", response.getStatusLine().getStatusCode(), equalTo(200));
        assertThat("Крым наш!" + setCookies, targetUri.toString(), startsWith(YANDEX_UA));

        response.close();
        httpClient.close();

    }
}
