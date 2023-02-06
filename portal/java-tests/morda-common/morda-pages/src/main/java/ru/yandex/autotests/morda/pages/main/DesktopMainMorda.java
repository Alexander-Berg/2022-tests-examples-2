package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
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
public class DesktopMainMorda extends MainMorda<DesktopMainMorda>
        implements AbstractDesktopMorda<DesktopMainMorda> {

    private DesktopMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopMainMorda desktopMain() {
        return desktopMain("production");
    }

    public static DesktopMainMorda desktopMain(String environment) {
        return desktopMain("https", environment);
    }

    public static DesktopMainMorda desktopMain(String scheme, String environment) {
        return new DesktopMainMorda(scheme, "www", environment);
    }

    public static List<DesktopMainMorda> getDefaultList(String environment) {
        return asList(
                desktopMain(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                desktopMain(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                desktopMain(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                desktopMain(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                desktopMain(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN;
    }

    @Override
    public DesktopMainMorda me() {
        return this;
    }
}
