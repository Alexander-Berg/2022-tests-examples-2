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
public class DesktopMain404Morda extends MainMorda<DesktopMain404Morda>
        implements AbstractDesktopMorda<DesktopMain404Morda> {

    private DesktopMain404Morda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopMain404Morda desktopMain404() {
        return desktopMain404("production");
    }

    public static DesktopMain404Morda desktopMain404(String environment) {
        return desktopMain404("https", environment);
    }

    public static DesktopMain404Morda desktopMain404(String scheme, String environment) {
        return new DesktopMain404Morda(scheme, "www", environment);
    }

    public static List<DesktopMain404Morda> getDefaultList(String environment) {
        return asList(
                desktopMain404(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                desktopMain404(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                desktopMain404(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                desktopMain404(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                desktopMain404(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path("sl/blah").build();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN_404;
    }

    @Override
    public DesktopMain404Morda me() {
        return this;
    }
}
