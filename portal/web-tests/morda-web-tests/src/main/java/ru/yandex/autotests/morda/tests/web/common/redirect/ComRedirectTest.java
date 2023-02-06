package ru.yandex.autotests.morda.tests.web.common.redirect;

import org.glassfish.jersey.client.ClientProperties;
import org.hamcrest.Matchers;
import org.junit.Assume;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.client.MordaClientBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriBuilder;
import java.util.ArrayList;
import java.util.Collection;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * User: asamar
 * Date: 26.11.2015.
 */
@Aqua.Test(title = "Com redirect")
@Features("Redirect")
@Stories("Com redirect")
@RunWith(Parameterized.class)
public class ComRedirectTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        Collection<Object[]> data = new ArrayList<>();

        String userAgentTouchIphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B436 Safari/600.1.4";//CONFIG.getMordaUserAgentTouchIphone();
        String androidUserAgent = "Mozilla/5.0 (Linux; Android 5.1; Nexus 5 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.111 Mobile Safari/537.36";

        data.add(new Object[]{"tr", "78.177.27.4", androidUserAgent});
        data.add(new Object[]{"ru", "188.143.128.49", androidUserAgent});

        return data;
    }

    private String name;
    private String ip;
    private String userAgent;
    private String targetUri;
    private String redirectRu;
    private String redirectTr;

    public ComRedirectTest(String name, String ip, String userAgent) {
        this.name = name;
        this.ip = ip;
        this.userAgent = userAgent;

        targetUri = UriBuilder.fromUri("scheme://{env}yandex.com/")
                .scheme(CONFIG.getMordaScheme())
                .build(new Morda.MordaEnvironment("www", CONFIG.getMordaEnvironment(), false).parseEnvironment())
                .toString();

        redirectRu = UriBuilder.fromUri("scheme://{env}yandex.ru/")
                .scheme(CONFIG.getMordaScheme())
                .queryParam("com","1")
                .build(new Morda.MordaEnvironment("www", CONFIG.getMordaEnvironment(), false).parseEnvironment())
                .toString();

        redirectTr = UriBuilder.fromUri("scheme://{env}yandex.com.tr/")
                .scheme(CONFIG.getMordaScheme())
                .queryParam("com","1")
                .build(new Morda.MordaEnvironment("www", CONFIG.getMordaEnvironment(), false).parseEnvironment())
                .toString();
    }

    @Test
    public void redirectTouchTest() {
        Client client = MordaClientBuilder.mordaClient()
                .withLogging(true).build();

        Response response = client.target(targetUri)
                .request()
                .header("X-Forwarded-For", ip)
                .header("User-Agent", userAgent)
                .buildGet()
                .property(ClientProperties.FOLLOW_REDIRECTS, Boolean.FALSE)
                .invoke();

        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
        assertThat("Плохой код ответа от \"" + response.getLocation() + "\"", status, Matchers.equalTo(Response.Status.FOUND));

        if (name.startsWith("ru")) {
            assertThat("Редирект на ru не удался", response.getLocation().toString(), equalTo(redirectRu));
        } else {
            assertThat("Редирект на com.tr не удался", response.getLocation().toString(), equalTo(redirectTr));
        }
        response.close();
        client.close();


//        HttpClient httpClient = HttpClientBuilder.create().build();
//
//        HttpClientContext context = HttpClientContext.create();
//        HttpGet req = new HttpGet(targetUri);
//        req.setHeader("X-Forwarded-For", ip);
//        req.setHeader("User-Agent", userAgent);
//        HttpResponse response = httpClient.execute(req, context);
//
//        List<URI> redirectPath = context.getRedirectLocations();
//
//        HttpUriRequest currentReq = (HttpUriRequest) context.getAttribute(
//                ExecutionContext.HTTP_REQUEST);
//        HttpHost currentHost = (HttpHost)  context.getAttribute(
//                ExecutionContext.HTTP_TARGET_HOST);
//        String currentUrl = (currentReq.getURI().isAbsolute()) ? currentReq.getURI().toString() : (currentHost.toURI() + currentReq.getURI());
//        if (name.startsWith("ru")){
//            assertThat("Сначала должно быть /com=1", redirectPath, containsInAnyOrder(
//                    fromUri(redirectRu).queryParam("com","1").build()
//            ));
//        } else {
//            assertThat("Сначала должно быть /com=1", redirectPath, containsInAnyOrder(
//                    fromUri(redirectTr).queryParam("com","1").build()
//            ));
//        }
//
//        assertThat("Плохой код ответа", response.getStatusLine().getStatusCode(), equalTo(200));
    }

    @Test
    public void redirectDesktopTest() {
        Assume.assumeFalse("Редирект только com -> com.tr ", name.equals("ru"));

        Client client = MordaClientBuilder.mordaClient()
                .withLogging(true).build();

        Response response = client.target(targetUri)
                .request()
                .header("X-Forwarded-For", ip)
                .buildGet()
                .property(ClientProperties.FOLLOW_REDIRECTS, Boolean.FALSE)
                .invoke();

        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
        assertThat("Плохой код ответа от \"" + response.getLocation() + "\"", status, Matchers.equalTo(Response.Status.FOUND));
        assertThat("Редирект на com.tr не удался", response.getLocation().toString(), equalTo(redirectTr));
        response.close();
        client.close();
    }

}
