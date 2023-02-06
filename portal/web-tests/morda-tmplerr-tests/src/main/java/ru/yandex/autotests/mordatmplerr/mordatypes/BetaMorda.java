package ru.yandex.autotests.mordatmplerr.mordatypes;

import ru.yandex.autotests.utils.morda.url.Domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class BetaMorda extends MordaWithDomains {

    protected BetaMorda(Domain domain) {
        super(domain);
    }

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(mordaEnv.replace("www", "beta"));
    }

    public static BetaMorda betaMorda(Domain domain) {
        return new BetaMorda(domain);
    }

    @Override
    public String toString() {
        return "BETA " + super.toString();
    }
}
