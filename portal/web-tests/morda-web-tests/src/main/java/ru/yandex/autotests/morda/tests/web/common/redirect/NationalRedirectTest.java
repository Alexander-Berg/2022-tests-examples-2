package ru.yandex.autotests.morda.tests.web.common.redirect;

import org.apache.http.HttpHost;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.client.utils.URIUtils;
import org.apache.http.impl.client.HttpClientBuilder;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Cookie;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 25.04.16
 */
@Aqua.Test(title = "National redirect")
@Features("Redirect")
@Stories("National redirect")
@RunWith(Parameterized.class)
public class NationalRedirectTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {

        Collection<Object[]> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        URI mordaUri = desktopMain(scheme, environment, MOSCOW).getUrl();
        URI mordaUriWithClid = fromUri(mordaUri).queryParam("clid", "12345").build();

        Cookie kiev = new Cookie("yandex_gid", "143", "/", ".yandex.ru");
        Cookie minsk = new Cookie("yandex_gid", "157", "/", ".yandex.ru");
        Cookie astana = new Cookie("yandex_gid", "163", "/", ".yandex.ru");

        URI targetMinskUri = desktopMain(scheme, environment, MINSK).getUrl();
        URI targetKievkUri = desktopMain(scheme, environment, KIEV).getUrl();
        URI targetAstanakUri = desktopMain(scheme, environment, ASTANA).getUrl();

        Stream.of(mordaUri, mordaUriWithClid)
                .forEach(e -> {
                            data.add(new Object[]{"Minsk", e, minsk, targetMinskUri});
                            data.add(new Object[]{"Kiev", e, kiev, targetKievkUri});
                            data.add(new Object[]{"Astana", e, astana, targetAstanakUri});
                        }
                );

        return data;
    }

    private URI uri;
    private URI targetUri;
    private Client client;
    private Cookie yandexGid;


    public NationalRedirectTest(String city, URI uri, Cookie yaGid, URI targetUri) {
        this.uri = uri;
        this.yandexGid = yaGid;
        this.targetUri = targetUri;
    }

    @Test
    public void targetUri() throws IOException, URISyntaxException {
        HttpClient httpClient = HttpClientBuilder.create().build();


        cookieUtils(httpClient)
                .addCookie(yandexGid.getName(), yandexGid.getValue(), yandexGid.getDomain());

        HttpClientContext context = HttpClientContext.create();
        httpClient.execute(new HttpGet(uri), context);

        List<URI> redirectPath = context.getRedirectLocations();
        URI lastRedirectUri = URIUtils.resolve(uri, new HttpHost(targetUri.getHost()), redirectPath);

        assertThat("Урл не тот!", lastRedirectUri.toString(), startsWith(targetUri.toString()));
    }

    @Test
    public void foundCode() throws IOException {
        HttpClient httpClient = HttpClientBuilder.create().disableRedirectHandling().build();

        cookieUtils(httpClient)
                .addCookie(yandexGid.getName(), yandexGid.getValue(), yandexGid.getDomain());

        HttpClientContext context = HttpClientContext.create();
        HttpResponse response = httpClient.execute(new HttpGet(uri), context);

        assertThat("Код не тот", response.getStatusLine().getStatusCode(), equalTo(302));

    }

//    @Test
//    @Ignore
//    public void redirect() {
//        this.client = MordaClientBuilder.mordaClient()
//                .withLogging(true).build();
//
//        Response response = client.target(uri)
//                .request()
//                .cookie(yandexGid)
//                .buildGet()
//                .property(ClientProperties.FOLLOW_REDIRECTS, Boolean.FALSE)
//                .invoke();
//
//        shoudHaveStatus(response, Response.Status.FOUND, uri);
//
//        UrlMatcher urlMatcher = urlMatcher()
//                .scheme("https")
//                .host("pass.yandex.ru")
//                .urlParams(
//                        urlParam("retpath", startsWith(normalizeUrl(targetUri.toString())))
//                ).build();
//
//        assertThat("Редирект на " + targetUri + " не удался", response.getLocation().toString(), urlMatcher);
//
//        Response locationResponce = client.target(response.getLocation())
//                .request()
//                .cookie(yandexGid)
//                .buildGet()
//                .invoke();
//
//        shoudHaveStatus(locationResponce, OK, response.getLocation());
//
//        locationResponce.close();
//        response.close();
//    }
//
//    private String normalizeUrl(String url) {
//        return url
//                .replaceAll("(/(?=$))", "")
//                .replaceAll("/", "%2F")
//                .replaceAll(":", "%3A")
//                .replaceAll("=", "%3D");
//    }
//
//
//    @Step("expect status {1} on {2}")
//    public void shoudHaveStatus(Response response, Response.Status expectedStatus, URI uri) {
//        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
//        assertThat("Плохой код ответа от \"" + uri + "\"", status, equalTo(expectedStatus));
//    }


}
