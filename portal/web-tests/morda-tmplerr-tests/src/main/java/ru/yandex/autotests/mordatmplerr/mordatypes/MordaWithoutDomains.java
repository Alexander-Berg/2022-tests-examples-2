package ru.yandex.autotests.mordatmplerr.mordatypes;

import gumi.builders.UrlBuilder;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public abstract class MordaWithoutDomains extends Morda {
    private static final String MORDA_URL_PATTERN = "https://%s.yandex%s/";

    public String getUrl(String mordaEnv) {
        return super.getUrl(UrlBuilder.fromString(String.format(getUrlPattern(), mordaEnv)));
    }

    @Override
    protected String getUrlPattern() {
        return MORDA_URL_PATTERN;
    }
}
