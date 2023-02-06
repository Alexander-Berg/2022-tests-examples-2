package ru.yandex.autotests.morda.data.services.searchapi;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.services.ServiceApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.services.ServicesApiV2Data;
import ru.yandex.autotests.morda.beans.exports.application_package_v2.ApplicationPackageV2Entry;
import ru.yandex.autotests.morda.beans.exports.application_package_v2.ApplicationPackageV2Export;
import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Entry;
import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Export;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.exports.filters.MordaDomainFilter;
import ru.yandex.autotests.morda.matchers.IntentMatcher;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Step;

import java.text.Collator;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._1;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.IntentMatcher.intent;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13/10/16
 */
public class ServicesSearchApiV2Data {

    private static final ServicesV122Export SERVICES_V_122_EXPORT = new ServicesV122Export().populate();
    private static final ApplicationPackageV2Export APPLICATION_PACKAGE_V_2_EXPORT = new ApplicationPackageV2Export().populate();

    private SearchApiRequestData requestData;

    public ServicesSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    public static List<ServicesV122Entry> getAvailableServices(MordaDomain domain) {
        return SERVICES_V_122_EXPORT
                .find(
                        MordaDomainFilter.filter(domain),
                        e -> e.getApiSearch() != 0
                );
    }

    @Step("Check services")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkData(response.getServices().getData());
    }

    @Step("Check search data")
    public void checkData(ServicesApiV2Data servicesData) {
        for (ServiceApiV2 service : servicesData.getList()) {
            checkService(service);
        }
        for (ServiceApiV2 service : servicesData.getMore().getList()) {
            checkService(service);
        }
        checkMoreSort(servicesData.getMore().getList());
        checkMoreList(servicesData.getMore().getList());
    }

    @Step("Check more sort")
    public void checkMoreSort(List<ServiceApiV2> services) {

        List<String> texts = services.stream().map(ServiceApiV2::getText).collect(Collectors.toList());
        List<String> textsToSort = new ArrayList<>(texts);

        textsToSort.sort(Collator.getInstance(new Locale("ru")));

        checkBean(texts, equalTo(textsToSort));
    }

    @Step("Check more list")
    public void checkMoreList(List<ServiceApiV2> services) {

        List<String> ids = services.stream().map(ServiceApiV2::getId).collect(Collectors.toList());
        List<String> expected = SERVICES_V_122_EXPORT.find(
                MordaDomainFilter.filter(MordaDomain.fromString(requestData.getGeo().getKubrDomain())),
                e -> e.getApiSearch() != 0
        )
                .stream()
                .map(ServicesV122Entry::getId)
                .collect(Collectors.toList());

        checkBean(ids, hasSameItemsAsList(expected));
    }


    @Step("Check service {0}")
    public void checkService(ServiceApiV2 service) {
        System.out.println(service.getId());
        Matcher<String> url = null;


        if (!service.getId().equals("more")) {
            Optional<ApplicationPackageV2Entry> applicationPackageV2Entry =
                    APPLICATION_PACKAGE_V_2_EXPORT.find(e -> e.getName().equals(service.getId())).stream().findFirst();
            ServicesV122Entry servicesV122Entry = SERVICES_V_122_EXPORT.find(
                    MordaDomainFilter.filter(MordaDomain.fromString(requestData.getGeo().getKubrDomain())),
                    e -> service.getId().equals(e.getId())
            ).stream().findFirst().get();
            if (service.getId().equals("video")) {
                url = startsWith("viewport://");
            } else if (applicationPackageV2Entry.isPresent()) {
                ApplicationPackageV2Entry entry = applicationPackageV2Entry.get();
                IntentMatcher intentMatcher = intent()
                        .packageMatcher(equalTo(entry.getPackage()));
                //                    .browserFallbackUrl(urlMatcher(u));

                if (entry.getAndIntent() != null) {
                    intentMatcher.url(equalTo(entry.getAndIntent().replace("http://", "")));
                }
                url = intentMatcher;
            } else {

                if (service.getId().equals("tv")) {
                    url = urlMatcher("https://m.tv.yandex" + requestData.getGeo().getKubrDomain());
                } else {
                    String s = servicesV122Entry.getTouch() != null ? servicesV122Entry.getTouch() : servicesV122Entry.getHref();
                    String normalized = s.startsWith("//") ? "https:" + s : s;
                    url = urlMatcher(normalized);
                }
            }
        }

        SearchApiDp dp = requestData.getDp() == null ? _1 : requestData.getDp();

        if (service.getId().equals("more")) {

            checkBean(service, allOfDetailed(
                    hasPropertyWithValue(on(ServiceApiV2.class).getIcon(),
                            equalTo("https://api.yastatic.net/morda-logo/i/yandex-app/informer/services/" + service.getId() + "." + dp.getValue() + ".png")),
                    hasPropertyWithValue(on(ServiceApiV2.class).getText(), equalTo(
                            TankerManager.get("home", "tabs", "More", requestData.getLanguage())))
            ));
        } else {

            checkBean(service, allOfDetailed(
                    hasPropertyWithValue(on(ServiceApiV2.class).getIcon(),
                            equalTo("https://api.yastatic.net/morda-logo/i/yandex-app/informer/services/" + service.getId() + "." + dp.getValue() + ".png")),
                    hasPropertyWithValue(on(ServiceApiV2.class).getUrl(), url),
                    hasPropertyWithValue(on(ServiceApiV2.class).getText(), equalTo(
                                    TankerManager.getSafely("home", "services", "services." + service.getId() + ".title", requestData.getLanguage())
                            ))
            ));
        }
    }

    @Step("Check services exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getServices(), notNullValue()));
    }

    @Step("Ping urls")
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        ServicesApiV2Data services = response.getServices().getData();

        Set<String> urls = new HashSet<>();

        services.getList().forEach(e -> urls.add(e.getUrl()));
        services.getMore().getList().forEach(e -> urls.add(e.getUrl()));

        Set<String> normalizedUrls = urls.stream()
                .filter(e -> e != null && !e.startsWith("viewport"))
                .map(SearchApiDataUtils::getFallbackUrl).collect(Collectors.toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
