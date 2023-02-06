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
public class DesktopFamilyMainMorda extends MainMorda<DesktopFamilyMainMorda>
        implements AbstractDesktopMorda<DesktopFamilyMainMorda> {

    private DesktopFamilyMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopFamilyMainMorda desktopFamilyMain() {
        return desktopFamilyMain("production");
    }

    public static DesktopFamilyMainMorda desktopFamilyMain(String environment) {
        return desktopFamilyMain("https", environment);
    }

    public static DesktopFamilyMainMorda desktopFamilyMain(String scheme, String environment) {
        return new DesktopFamilyMainMorda(scheme, "family", environment);
    }

    public static List<DesktopFamilyMainMorda> getDefaultList(String environment) {
        return asList(
                desktopFamilyMain(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                desktopFamilyMain(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                desktopFamilyMain(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                desktopFamilyMain(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                desktopFamilyMain(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN;
    }

    @Override
    public DesktopFamilyMainMorda me() {
        return this;
    }
}
