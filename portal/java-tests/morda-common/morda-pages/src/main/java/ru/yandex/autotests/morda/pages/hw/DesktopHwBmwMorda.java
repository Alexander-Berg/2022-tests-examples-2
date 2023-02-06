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
public class DesktopHwBmwMorda extends HwMorda<DesktopHwBmwMorda>
        implements AbstractDesktopMorda<DesktopHwBmwMorda> {

    private DesktopHwBmwMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopHwBmwMorda desktopHwBmw() {
        return desktopHwBmw("production");
    }

    public static DesktopHwBmwMorda desktopHwBmw(String environment) {
        return desktopHwBmw("https", environment);
    }

    public static DesktopHwBmwMorda desktopHwBmw(String scheme, String environment) {
        return new DesktopHwBmwMorda(scheme, "hw", environment);
    }

    public static List<DesktopHwBmwMorda> getDefaultList(String environment) {
        return asList(desktopHwBmw(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_HW_BMW;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/bmw")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public DesktopHwBmwMorda me() {
        return this;
    }
}
