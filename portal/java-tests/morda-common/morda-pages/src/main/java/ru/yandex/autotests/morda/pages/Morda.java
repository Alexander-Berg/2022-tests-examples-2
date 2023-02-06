package ru.yandex.autotests.morda.pages;

import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.qatools.usermanager.beans.UserData;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11/05/16
 */
public interface Morda<T> {
    MordaPagesProperties CONFIG = new MordaPagesProperties();
    String USER_AGENT = "User-Agent";
    String X_YANDEX_TEST_COUNTERS = "X-Yandex-TestCounters";
    String X_YANDEX_TEST_EXP = "X-Yandex-TestExp";
    String X_YANDEX_TEST_EXP_FORCE_DISABLED = "X-Yandex-TestExpForceDisabled";

    String getScheme();

    String getEnvironment();

    MordaType getMordaType();

    String getUserAgent();

    String getDefaultUserAgent();

    URI getBaseUrl();

    default URI getUrl() {
        UriBuilder builder = UriBuilder.fromUri(getBaseUrl())
                .path(getPath());
        for (Map.Entry<String, Object> q : getQueryParams().entrySet()) {
            builder.queryParam(q.getKey(), q.getValue());
        }
        return builder.build();
    }

    T path(String path);

    String getPath();

    T queryParam(String param, Object value);

    Map<String, Object> getQueryParams();

    URI getPassportHost();

    URI getTuneHost();

    T me();

    T login(List<UserData> users);

    default T login(UserData... users) {
        return login(asList(users));
    }

    T userAgent(String userAgent);

    T cookie(String name, String value);

    T header(String name, String value);

    T experiments(List<String> experiments);

    Map<String, String> getCookies();

    Map<String, String> getHeaders();

    List<String> getExperiments();

    List<UserData> getUsers();

    MordaLanguage getLanguage();

    Set<MordaLanguage> getAvailableLanguages();

    MordaDomain getDomain();

    String getCookieDomain();

    default T experiments(String... experiments) {
        return experiments(asList(experiments));
    }

    default T blockCounters() {
        return header(X_YANDEX_TEST_COUNTERS, "0");
    }

    default T forceCounters() {
        return header(X_YANDEX_TEST_COUNTERS, "1");
    }
}
