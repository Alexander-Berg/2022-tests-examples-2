package ru.yandex.autotests.mordatmplerr.mordatypes;

import gumi.builders.UrlBuilder;
import ru.yandex.autotests.utils.morda.url.Domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public abstract class MordaWithDomains extends Morda {
    private static final String MORDA_URL_PATTERN = "https://%s.yandex%s/";

    private Domain domain;

    protected MordaWithDomains(Domain domain) {
        this.domain = domain;
    }

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(UrlBuilder.fromString(String.format(getUrlPattern(), mordaEnv, domain)));
    }

    @Override
    protected String getUrlPattern() {
        return MORDA_URL_PATTERN;
    }

    @Override
    public String toString() {
        return domain.name() + " " + super.toString();
    }
}

