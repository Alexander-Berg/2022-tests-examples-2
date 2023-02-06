package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
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
public class TouchMainMorda extends MainMorda<TouchMainMorda>
        implements AbstractTouchMorda<TouchMainMorda> {

    private TouchMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        cookie("mda", "0");
    }

    public static TouchMainMorda touchMain() {
        return touchMain("production");
    }

    public static TouchMainMorda touchMain(String environment) {
        return touchMain("https", environment);
    }

    public static TouchMainMorda touchMain(String scheme, String environment) {
        return new TouchMainMorda(scheme, "www", environment);
    }

    public static List<TouchMainMorda> getDefaultList(String environment) {
        return asList(
                touchMain(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                touchMain(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                touchMain(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                touchMain(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                touchMain(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_MAIN;
    }

    @Override
    public TouchMainMorda me() {
        return this;
    }
}
