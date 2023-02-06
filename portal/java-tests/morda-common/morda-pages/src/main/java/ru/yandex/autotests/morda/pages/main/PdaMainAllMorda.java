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
public class PdaMainAllMorda extends MainMorda<PdaMainAllMorda>
        implements AbstractPdaMorda<PdaMainAllMorda> {

    private PdaMainAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static PdaMainAllMorda pdaMainAll() {
        return pdaMainAll("production");
    }

    public static PdaMainAllMorda pdaMainAll(String environment) {
        return pdaMainAll("https", environment);
    }

    public static PdaMainAllMorda pdaMainAll(String scheme, String environment) {
        return new PdaMainAllMorda(scheme, "www", environment);
    }

    public static List<PdaMainAllMorda> getDefaultList(String environment) {
        return asList(
                pdaMainAll(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                pdaMainAll(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                pdaMainAll(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                pdaMainAll(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                pdaMainAll(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_MAIN_ALL;
    }

    @Override
    public PdaMainAllMorda me() {
        return this;
    }
}
