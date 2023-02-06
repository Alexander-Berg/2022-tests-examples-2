package ru.yandex.autotests.morda.tests;

import com.jayway.restassured.response.Response;
import org.apache.log4j.Logger;
import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.steps.ValidateSchemaSteps;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.Set;
import java.util.stream.Stream;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/16
 */
public abstract class SearchApiChecker<T> implements Checker<T> {
    protected static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    protected static final Random RANDOM = new Random();
    protected final Logger LOGGER = Logger.getLogger(this.getClass());
    protected SearchApiRequestData requestData;

    public SearchApiChecker(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    //    static <T> SearchApiChecker<T> getChecker(SearchApiRequest request) {
//        SearchApiBlock block = request.getBlock();
//
//        switch (block) {
//            case TV:
//                return tvSearchApiChecker(version, region, language);
//            case AFISHA:
//                return afishaSearchApiChecker(version, region, language);
//            case APPLICATION:
//                return applicationSearchApiChecker(version, region, language);
//            case BRIDGES:
//                return bridgesSearchApiChecker(version, region, language);
//            case INFORMER:
//                return informerSearchApiChecker(version, region, language);
//            case NOW:
//                return nowSearchApiChecker(version, region, language);
//            case POI:
//                return poiSearchApiChecker(version, region, language);
//            case STOCKS:
//                return stocksSearchApiChecker(version, region, language);
//            case TOPNEWS:
//                return topnewsSearchApiChecker(version, region, language);
//            case TRANSPORT:
//                return TransportSearchApiChecker.transportSearchApiChecker(version, region, language);
//            case WEATHER:
//                return weatherSearchApiChecker(version, region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for block " + block);
//        }
//    }

    static String getFallbackUrl(String url) {
        if (url == null || !url.startsWith("intent://")) {
            return url;
        }
        String fallbackStart = "S.browser_fallback_url=";

        Optional<String> fallback = Stream.of(url.split(";"))
                .filter(e -> e.startsWith(fallbackStart))
                .map(e -> e.substring(fallbackStart.length()))
                .findFirst();

        if (!fallback.isPresent()) {
            throw new IllegalStateException("Failed to parse intent url: " + url);
        }

        String encodedUrl = fallback.get();
        try {
            return URLDecoder.decode(encodedUrl, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Failed to decode url: " + encodedUrl, e);
        }
    }

    static String getYellowskinkUrl(String url) {
        if (url == null || !url.startsWith("yellowskin://")) {
            return url;
        }

        String urlStart = "url=";

        Optional<String> encodedUrl = Stream.of(url.substring(url.indexOf("?") + 1).split("&"))
                .filter(e -> e.startsWith(urlStart))
                .map(e -> e.substring(urlStart.length()))
                .findFirst();

        if (!encodedUrl.isPresent()) {
            throw new IllegalStateException("Failed to parse intent url: " + url);
        }

        String encoded = encodedUrl.get();
        try {
            return URLDecoder.decode(encoded, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Failed to decode url: " + encodedUrl, e);
        }
    }

    public abstract String getJsonSchemaFile();

    public abstract void check(T response);

    public abstract void checkExists(T response);

    @Step("Validate response format")
    public void checkJsonSchema(Response response) {
        ValidateSchemaSteps.validate(response, getJsonSchemaFile());
    }

    public void pingLinks(T response) {
        pingLinks(response, null, null);
    }

    public void pingLinks(T response, GeobaseRegion region) {
        pingLinks(response, region, null);
    }

    public void pingLinks(T response, MordaLanguage language) {
        pingLinks(response, null, language);
    }

    public void pingLinks(T response, GeobaseRegion region, MordaLanguage language) {
        Set<String> urls = getUrlsToPing(response);
//        assertThat("No urls found", urls, not(empty()));

        List<LinkUtils.PingResult> pingResults = LinkUtils.ping(urls, region, language);
        long failedRequests = pingResults.stream()
                .filter(e -> e.isError() || e.getStatusCode() >= 400)
                .count();
        assertThat("Found " + failedRequests + " failed requests", failedRequests, equalTo(0L));
    }

    public void pingStatic(T response) {
        Set<String> urls = getStaticUrls(response);
//        assertThat("No static urls found", urls, not(empty()));
        List<LinkUtils.PingResult> pingResults = LinkUtils.ping(urls);
        long failedRequests = pingResults.stream()
                .filter(e -> e.isError() || e.getStatusCode() != 200)
                .count();

        assertThat("Found " + failedRequests + " failed static requests", failedRequests, equalTo(0L));
    }

    public <E> void checkWithAttachment(E t, Matcher<? super E> matcher) {
        AttachmentUtils.attachText("check.info", matcher.toString());
        assertThat(t, matcher);
    }
}
