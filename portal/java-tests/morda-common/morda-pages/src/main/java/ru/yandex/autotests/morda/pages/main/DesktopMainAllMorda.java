package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopMainAllMorda extends MainMorda<DesktopMainAllMorda>
        implements AbstractDesktopMorda<DesktopMainAllMorda> {

    private DesktopMainAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopMainAllMorda desktopMainAll() {
        return desktopMainAll("production");
    }

    public static DesktopMainAllMorda desktopMainAll(String environment) {
        return desktopMainAll("https", environment);
    }

    public static DesktopMainAllMorda desktopMainAll(String scheme, String environment) {
        return new DesktopMainAllMorda(scheme, "www", environment);
    }

    public static List<DesktopMainAllMorda> getDefaultList(String environment) {
        return asList(
                desktopMainAll(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                desktopMainAll(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                desktopMainAll(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                desktopMainAll(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                desktopMainAll(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path("all").build();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN_ALL;
    }

    @Override
    public DesktopMainAllMorda me() {
        return this;
    }
}
