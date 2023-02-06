package ru.yandex.autotests.morda.pages.hw;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopHwLgMorda extends HwMorda<DesktopHwLgMorda>
        implements AbstractDesktopMorda<DesktopHwLgMorda> {

    private DesktopHwLgMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopHwLgMorda desktopHwLg() {
        return desktopHwLg("production");
    }

    public static DesktopHwLgMorda desktopHwLg(String environment) {
        return desktopHwLg("https", environment);
    }

    public static DesktopHwLgMorda desktopHwLg(String scheme, String environment) {
        return new DesktopHwLgMorda(scheme, "hw", environment);
    }

    public static List<DesktopHwLgMorda> getDefaultList(String environment) {
        return asList(desktopHwLg(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_HW_LG;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/lg")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public DesktopHwLgMorda me() {
        return this;
    }
}
