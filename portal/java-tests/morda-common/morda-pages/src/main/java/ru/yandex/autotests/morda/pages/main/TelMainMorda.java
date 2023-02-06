package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.AbstractTelMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TelMainMorda extends MainMorda<TelMainMorda>
        implements AbstractTelMorda<TelMainMorda> {

    private TelMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TelMainMorda telMain() {
        return telMain("production");
    }

    public static TelMainMorda telMain(String environment) {
        return telMain("https", environment);
    }

    public static TelMainMorda telMain(String scheme, String environment) {
        return new TelMainMorda(scheme, "www", environment);
    }

    public static List<TelMainMorda> getDefaultList(String environment) {
        return asList(telMain(environment));
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.RU;
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TEL_MAIN;
    }

    @Override
    public TelMainMorda me() {
        return this;
    }
}
