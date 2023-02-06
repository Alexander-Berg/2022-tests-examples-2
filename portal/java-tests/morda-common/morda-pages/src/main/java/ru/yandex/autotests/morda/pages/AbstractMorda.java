package ru.yandex.autotests.morda.pages;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.usermanager.beans.UserData;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11/05/16
 */
public abstract class AbstractMorda<T> implements Morda<T> {
    protected final Map<String, Object> queryParams = new HashMap<>();
    protected final Map<String, String> headers = new HashMap<>();
    protected final Map<String, String> cookies = new HashMap<>();
    protected final List<UserData> users = new ArrayList<>();
    protected String scheme;
    protected String prefix;
    protected String environment;
    protected String subPage = "";
    private GeobaseRegion region;
    private MordaLanguage language;

    protected AbstractMorda(String scheme, String prefix, String environment) {
        this.scheme = scheme;
        this.prefix = prefix;
        this.environment = environment;
        userAgent(getDefaultUserAgent());
    }

    @Override
    public String getPath() {
        return subPage;
    }

    @Override
    public T path(String path) {
        this.subPage = path;
        return me();
    }

    @Override
    public Map<String, Object> getQueryParams() {
        return queryParams;
    }

    @Override
    public T queryParam(String param, Object value) {
        queryParams.put(param, value);
        return me();
    }

    @Override
    public String getScheme() {
        return scheme;
    }

    @Override
    public String getEnvironment() {
        if (environment == null || environment.isEmpty()) {
            throw new IllegalArgumentException("Environment must not be null or empty");
        }

        if (environment.equals("production")) {
            return prefix + ".";
        }

        if (environment.equals("serp")) {
            return "";
        }

        return prefix + "-" + environment + ".";
    }

    @Override
    public String getUserAgent() {
        return headers.get(USER_AGENT);
    }

    @Override
    public T userAgent(String userAgent) {
        header(USER_AGENT, userAgent);
        return me();
    }

    protected GeobaseRegion getRegion() {
        return region;
    }

    protected T region(GeobaseRegion region) {
        this.region = region;
        return me();
    }

    public MordaLanguage getLanguage() {
        return language;
    }

    protected T language(MordaLanguage language) {
        if (getAvailableLanguages().contains(language)) {
            this.language = language;
            return me();
        }
        throw new IllegalArgumentException("Language " + language + " is not allowed for morda " + getMordaType());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain().getValue();
    }

    @Override
    public T cookie(String name, String value) {
        this.cookies.put(name, value);
        return me();
    }

    @Override
    public T header(String name, String value) {
        this.headers.put(name, value);
        return me();
    }

    @Override
    public T login(List<UserData> users) {
        this.users.addAll(users);
        return me();
    }

    @Override
    public T experiments(List<String> experiments) {
        if (experiments.isEmpty()) {
            return me();
        }

        header(X_YANDEX_TEST_EXP_FORCE_DISABLED, "1");
        List<String> newExperiments = new ArrayList<>(getExperiments());
        newExperiments.addAll(experiments);

        header(X_YANDEX_TEST_EXP, StringUtils.join(newExperiments, ","));
        return me();
    }

    @Override
    public Map<String, String> getCookies() {
        return Collections.unmodifiableMap(cookies);
    }

    @Override
    public Map<String, String> getHeaders() {
        return Collections.unmodifiableMap(headers);
    }

    @Override
    public List<String> getExperiments() {
        String experimentsHeader = headers.get(X_YANDEX_TEST_EXP);
        if (experimentsHeader == null || experimentsHeader.isEmpty()) {
            return new ArrayList<>();
        }
        return asList(experimentsHeader.split(","));
    }

    @Override
    public List<UserData> getUsers() {
        return users;
    }

    @Override
    public String toString() {
        return getMordaType().name().toLowerCase() + " \"" + getUrl() + "\"";
    }
}
