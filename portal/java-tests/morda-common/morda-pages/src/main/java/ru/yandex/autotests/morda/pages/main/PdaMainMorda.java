package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractPdaMorda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaMainMorda extends MainMorda<PdaMainMorda>
        implements AbstractPdaMorda<PdaMainMorda> {

    private PdaMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        cookie("mda", "0");
    }

    public static PdaMainMorda pdaMain() {
        return pdaMain("production");
    }

    public static PdaMainMorda pdaMain(String environment) {
        return pdaMain("https", environment);
    }

    public static PdaMainMorda pdaMain(String scheme, String environment) {
        return new PdaMainMorda(scheme, "www", environment);
    }

    public static List<PdaMainMorda> getDefaultList(String environment) {
        return asList(
                pdaMain(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                pdaMain(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                pdaMain(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                pdaMain(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                pdaMain(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_MAIN;
    }

    @Override
    public PdaMainMorda me() {
        return this;
    }
}
