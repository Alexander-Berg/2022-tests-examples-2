package ru.yandex.autotests.mordatmplerr.mordatypes;

import ru.yandex.autotests.utils.morda.url.Domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class MainMorda extends MordaWithDomains {
    private boolean isFamily = false;

    public MainMorda(Domain domain) {
        super(domain);
    }

    @Override
    public String getUrl(String mordaEnv) {
        if (isFamily) {
            return super.getUrl(mordaEnv.replace("www", "family"));
        } else {
            return super.getUrl(mordaEnv);
        }
    }

    public static MainMorda mainMorda(Domain domain) {
        return new MainMorda(domain);
    }

    public static MainMorda familyMorda(Domain domain) {
        MainMorda morda = new MainMorda(domain);
        morda.isFamily = true;
        return morda;
    }

    @Override
    public String toString() {
        if (isFamily) {
            return "MAIN FAMILY " + super.toString();
        }
        return "MAIN " + super.toString();
    }
}
