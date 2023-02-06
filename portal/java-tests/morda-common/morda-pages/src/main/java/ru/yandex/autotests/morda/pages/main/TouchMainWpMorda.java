package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
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
public class TouchMainWpMorda extends MainMorda<TouchMainWpMorda>
        implements AbstractTouchMorda<TouchMainWpMorda> {

    private TouchMainWpMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        cookie("mda", "0");
    }

    public static TouchMainWpMorda touchMainWp() {
        return touchMainWp("production");
    }

    public static TouchMainWpMorda touchMainWp(String environment) {
        return touchMainWp("https", environment);
    }

    public static TouchMainWpMorda touchMainWp(String scheme, String environment) {
        return new TouchMainWpMorda(scheme, "www", environment);
    }

    public static List<TouchMainWpMorda> getDefaultList(String environment) {
        return asList(
                touchMainWp(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                touchMainWp(environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                touchMainWp(environment).region(Belarus.MINSK).language(MordaLanguage.BE),
                touchMainWp(environment).region(Kazakhstan.ALMATY).language(MordaLanguage.KK),
                touchMainWp(environment).region(Russia.KAZAN).language(MordaLanguage.TT)
        );
    }

    @Override
    public String getDefaultUserAgent() {
        return CONFIG.getTouchwpUserAgent();
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).queryParam("q", "").build();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_MAIN_WP;
    }

    @Override
    public TouchMainWpMorda me() {
        return this;
    }
}
