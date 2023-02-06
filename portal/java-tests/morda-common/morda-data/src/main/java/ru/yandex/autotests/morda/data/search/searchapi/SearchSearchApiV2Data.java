package ru.yandex.autotests.morda.data.search.searchapi;

import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.search.SearchApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.search.SearchApiV2Informer;
import ru.yandex.autotests.morda.beans.exports.traffic_mobile.TrafficMobileExport;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.IntentMatcher.intent;
import static ru.yandex.autotests.morda.matchers.MordaNavigateMatcher.mordaNavigate;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13/10/16
 */
public class SearchSearchApiV2Data {

    private static final TrafficMobileExport TRAFFIC_MOBILE_EXPORT = new TrafficMobileExport().populate();

    private SearchApiRequestData requestData;

    public SearchSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }


    @Step("Check search")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkData(response.getSearch().getData());
    }

    @Step("Check search data")
    public void checkData(SearchApiV2Data searchData) {
        checkInformer(searchData.getInformer());
    }

    @Step("Check informer")
    public void checkInformer(List<SearchApiV2Informer> informers) {
        Optional<SearchApiV2Informer> mail = informers.stream().filter(e -> e.getId().equals("mail")).findFirst();
        assertThat("No mail informer found", mail.isPresent(), is(true));
        checkMail(mail.get());

        Optional<SearchApiV2Informer> weather = informers.stream().filter(e -> e.getId().equals("weather")).findFirst();
        assertThat("No weather informer found", weather.isPresent(), is(true));
        checkWeather(weather.get());

        Optional<SearchApiV2Informer> traffic = informers.stream().filter(e -> e.getId().equals("traffic")).findFirst();
        if (traffic.isPresent()) {
            checkTraffic(traffic.get());
        }
//        else {
//            assertThat("No traffic informer should exist", traffic.isPresent(), is(false));
//        }
    }

    @Step("Check mail")
    public void checkMail(SearchApiV2Informer informer) {

        String iconPattern = "https://api.yastatic.net/morda-logo/i/yandex-app/informer/services/mail.%s.png";
        SearchApiDp dp = requestData.getDp() == null ? SearchApiDp._1 : requestData.getDp();
        checkBean(informer, allOfDetailed(
                hasPropertyWithValue(on(SearchApiV2Informer.class).getIcon(), equalTo(String.format(iconPattern, dp.getValue()))),
                hasPropertyWithValue(
                        on(SearchApiV2Informer.class).getUrl(),
                        intent()
                                .packageMatcher(equalTo("ru.yandex.mail"))
                                .browserFallbackUrl(urlMatcher("https://mail.yandex" + requestData.getGeo().getKubrDomain()))
                )
        ));
    }

    @Step("Check weather")
    public void checkWeather(SearchApiV2Informer informer) {
        checkBean(informer, allOfDetailed(
                hasPropertyWithValue(on(SearchApiV2Informer.class).getText(), not(isEmptyOrNullString())),
                hasPropertyWithValue(
                        on(SearchApiV2Informer.class).getUrl(),
                        mordaNavigate(
                                "weather/weather",
                                urlMatcher("https://yandex" + requestData.getGeo().getKubrDomain()).path(regex("pogoda/.*"))
                        )
                )
        ));
    }

    @Step("Check traffic")
    public void checkTraffic(SearchApiV2Informer informer) {

        MordaDomain fallbackDomain = MordaDomain.fromString(requestData.getGeo().getKubrDomain()).equals(MordaDomain.UA)
                ? MordaDomain.UA
                : MordaDomain.RU;

        checkBean(informer, allOfDetailed(
                hasPropertyWithValue(on(SearchApiV2Informer.class).getText(), not(isEmptyOrNullString())),
                hasPropertyWithValue(
                        on(SearchApiV2Informer.class).getUrl(),
                        intent()
                                .packageMatcher(equalTo("ru.yandex.yandexmaps"))
                                .scheme(equalTo("http"))
                                .url(startsWith("yandex.ru/maps"))
                                .browserFallbackUrl(
                                        urlMatcher("https://yandex" + fallbackDomain.getValue())
                                                .path(regex("maps/\\d+/.+/probki"))
                                )
                )
        ));
    }

    @Step("Check search exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getSearch(), notNullValue()));
    }

    @Step("Ping urls")
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        SearchApiV2Data search = response.getSearch().getData();

        Set<String> urls = new HashSet<>();

        search.getInformer().forEach(e -> urls.add(e.getUrl()));

        Set<String> normalizedUrls = urls.stream().map(SearchApiDataUtils::getFallbackUrl).collect(Collectors.toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
