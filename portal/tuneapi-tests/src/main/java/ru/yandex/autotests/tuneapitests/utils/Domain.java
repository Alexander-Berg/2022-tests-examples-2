package ru.yandex.autotests.tuneapitests.utils;

import ru.yandex.autotests.tuneapitests.Properties;

import java.net.MalformedURLException;
import java.net.URI;
import java.net.URL;
import java.util.EnumSet;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public enum Domain {
    RU(".ru"),
    UA(".ua"),
    BY(".by"),
    KZ(".kz"),
    COM(".com"),
    COM_TR(".com.tr");

    private static final Properties CONFIG = new Properties();
    private static final String YANDEX_URL_PATTERN = "https://www.yandex%s/";
    private static final String POGODA_URL_PATTERN = "https://pogoda.yandex%s";
    private static final String POGODA_COMTR_URL = "https://hava.yandex.com.tr";
    private static final String MAIL_LOGGED_URL_PATTERN = "https://mail.yandex%s";
    private static final String TUNE_URL_PATTERN = "%s://%s.yandex%s";
    private static final String PASSPORT_URL_PATTERN = "https://passport.yandex%s/";
    private static final String COOKIE_DOMAIN = ".yandex%s";

    private String value;

    Domain(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public String getCookieDomain() {
        return String.format(COOKIE_DOMAIN, value);
    }

    public String getYandexUrl() {
        return String.format(YANDEX_URL_PATTERN, value);
    }

    public URI getTuneUrl() {
        return URI.create(String.format(TUNE_URL_PATTERN, CONFIG.getTuneProtocol(), CONFIG.getTuneEnv(), value));
    }

    public URI getTuneInternalUrl() {
        return URI.create(String.format(TUNE_URL_PATTERN, CONFIG.getTuneInternalProtocol(), CONFIG.getTuneInternalEnv(), value));
    }

    public URI getTuneUrlForGeoApi() {
        if (EnumSet.of(KZ, UA, BY).contains(this)) {
            return URI.create(String.format(TUNE_URL_PATTERN, CONFIG.getTuneProtocol(), CONFIG.getTuneEnv(), RU.getValue()));
        } else {
            return URI.create(String.format(TUNE_URL_PATTERN, CONFIG.getTuneProtocol(), CONFIG.getTuneEnv(), value));
        }
    }

    public URI getTuneUrl(String protocol, String env) {
        return URI.create(String.format(TUNE_URL_PATTERN, protocol, env, value));
    }

    public URI getPogodaUrl() {
        if (this.equals(COM_TR)) {
            return URI.create(POGODA_COMTR_URL);
        } else if (this.equals(COM)) {
            return URI.create(String.format(POGODA_URL_PATTERN, ".ru"));
        }
        return URI.create(String.format(POGODA_URL_PATTERN, value));
    }

    public URI getMailUrl() {
        return URI.create(String.format(MAIL_LOGGED_URL_PATTERN, value));
    }

    public URL getPassportUrl() {
        try {
            return new URL(String.format(PASSPORT_URL_PATTERN, value));
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
    }

    public URL getBasePassportUrl() {
        try {
            if (EnumSet.of(KZ, UA, BY).contains(this)) {
                return new URL(String.format(PASSPORT_URL_PATTERN, RU.getValue()));
            } else {
                return new URL(String.format(PASSPORT_URL_PATTERN, value));
            }
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
    }

    private static final EnumSet<Domain> JSON_SET_INVALID_DOMAINS = EnumSet.of(Domain.KZ, Domain.UA, Domain.BY);

    public boolean isDomainValidForJsonRequest() {
        return !JSON_SET_INVALID_DOMAINS.contains(this);
    }
}
