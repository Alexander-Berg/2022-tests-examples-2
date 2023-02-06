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
public class DesktopHwLgV2Morda extends HwMorda<DesktopHwLgV2Morda>
        implements AbstractDesktopMorda<DesktopHwLgV2Morda> {

    private DesktopHwLgV2Morda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopHwLgV2Morda desktopHwLgV2() {
        return desktopHwLgV2("production");
    }

    public static DesktopHwLgV2Morda desktopHwLgV2(String environment) {
        return desktopHwLgV2("https", environment);
    }

    public static DesktopHwLgV2Morda desktopHwLgV2(String scheme, String environment) {
        return new DesktopHwLgV2Morda(scheme, "hw", environment);
    }

    public static List<DesktopHwLgV2Morda> getDefaultList(String environment) {
        return asList(desktopHwLgV2(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_HW_LG_2;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/lg-v2")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public DesktopHwLgV2Morda me() {
        return this;
    }
}
