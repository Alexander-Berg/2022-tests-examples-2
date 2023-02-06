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
public class TouchMainAllMorda extends MainMorda<TouchMainAllMorda>
        implements AbstractTouchMorda<TouchMainAllMorda> {

    private TouchMainAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        cookie("mda", "0");
    }

    public static TouchMainAllMorda touchMainAll() {
        return touchMainAll("production");
    }

    public static TouchMainAllMorda touchMainAll(String environment) {
        return touchMainAll("https", environment);
    }

    public static TouchMainAllMorda touchMainAll(String scheme, String environment) {
        return new TouchMainAllMorda(scheme, "www", environment);
    }

    public static List<TouchMainAllMorda> getDefaultList(String environment) {
        return asList(
                touchMainAll(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                touchMainAll(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                touchMainAll(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                touchMainAll(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                touchMainAll(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_MAIN_ALL;
    }

    @Override
    public TouchMainAllMorda me() {
        return this;
    }
}
