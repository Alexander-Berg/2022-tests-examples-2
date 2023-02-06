package ru.yandex.autotests.morda.tests.htmlcontent;

import org.junit.Rule;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static javax.ws.rs.core.UriBuilder.fromUri;

/**
 * User: asamar
 * Date: 24.01.17
 */
@Aqua.Test(title = "Weather page content")
@Features({"Consistency", "Weather html page content"})
@RunWith(Parameterized.class)
public class WeatherPageContentTest extends AbstractHtmlContentTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureFeatureRule feature;

    public WeatherPageContentTest(String tag, URI uri, String userAgent) {
        super(() -> new MordaClient().weather(userAgent, uri).readAsResponse().getBody().asString());
        this.feature = new AllureFeatureRule(uri.toString());
    }

    @Parameterized.Parameters(name = "{0} {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String desktopUserAgent = CONFIG.pages().getDesktopUserAgent();
        String touchUserAgent = CONFIG.pages().getTouchUserAgent();
        String pdaUserAgent = CONFIG.pages().getPdaUserAgent();

        getDesktopUris().forEach(uri ->
                        data.add(new Object[]{"desktop", uri, desktopUserAgent}));

        getTouchUris().forEach(uri ->
                data.add(new Object[]{"touch", uri, touchUserAgent}));

        getPdaUris().forEach(uri ->
                data.add(new Object[]{"pda", uri, pdaUserAgent}));

        return data;
    }

    private static List<URI> getDesktopUris() {
        List<URI> data = new ArrayList<>();

        String environment = CONFIG.weather().getWeatherEnvironment();
        String scheme = CONFIG.weather().getWeatherScheme();

        for (String domain : asList(".ru",".ua",".by",".kz",".com.tr")) {

            URI baseUri = fromUri("{scheme}://{env}.yandex{domain}/pogoda")
                    .build(scheme, environment, domain);

            if (".com.tr".equals(domain)) {
                baseUri = fromUri("{scheme}://{env}.yandex{domain}/hava")
                        .build(scheme, environment, domain);
            }

            data.add(fromUri(baseUri).path("moscow").build());
            data.add(fromUri(baseUri).path("london").build());
            data.add(fromUri(baseUri).path("moscow/details").build());
            data.add(fromUri(baseUri).path("moscow/month").build());
            data.add(fromUri(baseUri).path("moscow/month/february").build());
            data.add(fromUri(baseUri).path("moscow/nowcast").build());
            data.add(fromUri(baseUri).path("moscow/maps").build());
            data.add(fromUri(baseUri).path("moscow/choose").build());
            data.add(fromUri(baseUri).path("region/225").build());
            data.add(fromUri(baseUri).path("404").build());
            data.add(fromUri(baseUri).path("500err").build());
            data.add(fromUri(baseUri).path("err_500").build());
            data.add(fromUri(baseUri).path("meteum").build());
            data.add(fromUri(baseUri).path("yekaterinburg").queryParam("appsearch_header", "1").build());
            data.add(fromUri(baseUri).path("kyiv/details").fragment("30").build());
            data.add(fromUri(baseUri).path("yekaterinburg").queryParam("appsearch_header", "1").fragment("d_30").build());

            data.add(fromUri(baseUri)
                    .path("moscow")
                    .path("maps")
                    .queryParam("region", "ru-north-west")
                    .build());
            data.add(fromUri(baseUri)
                    .path("search")
                    .queryParam("request", "f")
                    .queryParam("suggest_reqid", "207167371146191839222884488177864")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow")
                    .path("informer")
                    .build());

            // с координатами
            data.add(fromUri(baseUri)
                    .queryParam("lat", "44.016815")
                    .queryParam("lon", "39.234738")
                    .build());
            data.add(fromUri(baseUri).path("moscow/details")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow/month")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow/month/august")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow/nowcast")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri).path("moscow/maps")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow")
                    .path("informer")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
        }

        URI yaruUri = UriBuilder.fromUri("{scheme}://mini.pogoda.nodejs.weather-test.yandex.ru")
                .path("moscow")
                .queryParam("lat", "55.7348213")
                .queryParam("lon", "37.5858192")
                .build(scheme);
//        data.add(yaruUri);

        return data;
    }

    private static List<URI> getTouchUris() {
        List<URI> data = new ArrayList<>();

        String environment = CONFIG.weather().getWeatherEnvironment();
        String scheme = CONFIG.weather().getWeatherScheme();

        for (String domain : asList(".ru",".ua",".by",".kz",".com.tr")) {

            URI baseUri = UriBuilder.fromUri("{scheme}://{env}.yandex{domain}/pogoda")
                    .build(scheme, environment, domain);

            if (".com.tr".equals(domain)) {
                baseUri = fromUri("{scheme}://{env}.yandex{domain}/hava")
                        .build(scheme, environment, domain);
            }

            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .queryParam("lat", "59.95940399169922")
                    .queryParam("lon", "30.40688514709473")
                    .build());
            data.add(fromUri(baseUri)
                    .queryParam("lat", "44.016815")
                    .queryParam("lon", "39.234738")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .path("details")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .path("details")
                    .queryParam("lat", "59.95940399169922")
                    .queryParam("lon", "30.40688514709473")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .path("hourly")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .path("hourly")
                    .queryParam("lat", "59.95940399169922")
                    .queryParam("lon", "30.40688514709473")
                    .build());
            data.add(fromUri(baseUri).path("kyiv/details").fragment("30").build());
        }

        return data;
    }

    private static List<URI> getPdaUris() {
        List<URI> data = new ArrayList<>();

        String environment = CONFIG.weather().getWeatherEnvironment();
        String scheme = CONFIG.weather().getWeatherScheme();

        // убрал .ru и .com.tr
        for (String domain : asList(".ua",".by",".kz")) {

            URI baseUri = UriBuilder.fromUri("{scheme}://{env}.yandex{domain}/pogoda")
                    .build(scheme, environment, domain);

            if (".com.tr".equals(domain)) {
                baseUri = fromUri("{scheme}://{env}.yandex{domain}/hava")
                        .build(scheme, environment, domain);
            }

            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .build());
            data.add(fromUri(baseUri)
                    .path("saint-petersburg")
                    .queryParam("lat", "59.95940399169922")
                    .queryParam("lon", "30.40688514709473")
                    .build());
            data.add(fromUri(baseUri)
                    .path("search")
                    .queryParam("request", "п")
                    .build());
        }

        return data;
    }
}
