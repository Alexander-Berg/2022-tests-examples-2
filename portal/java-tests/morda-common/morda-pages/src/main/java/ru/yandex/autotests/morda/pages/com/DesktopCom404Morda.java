package ru.yandex.autotests.morda.pages.com;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopCom404Morda extends ComMorda<DesktopCom404Morda>
        implements AbstractDesktopMorda<DesktopCom404Morda> {

    private DesktopCom404Morda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopCom404Morda desktopCom404() {
        return desktopCom404("production");
    }

    public static DesktopCom404Morda desktopCom404(String environment) {
        return desktopCom404("https", environment);
    }

    public static DesktopCom404Morda desktopCom404(String scheme, String environment) {
        return new DesktopCom404Morda(scheme, "www", environment);
    }

    public static List<DesktopCom404Morda> getDefaultList(String environment) {
        return AVAILABLE_LANGUAGES.stream()
                .map(e -> desktopCom404(environment).language(e))
                .collect(Collectors.toList());
    }


    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COM_404;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl())
                .path("/sl/blah")
                .build();
    }

    @Override
    public DesktopCom404Morda me() {
        return this;
    }
}
