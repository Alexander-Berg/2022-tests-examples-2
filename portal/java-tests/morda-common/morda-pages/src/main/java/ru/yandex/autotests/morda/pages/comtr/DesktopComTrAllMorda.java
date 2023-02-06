package ru.yandex.autotests.morda.pages.comtr;

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
public class DesktopComTrAllMorda extends ComTrMorda<DesktopComTrAllMorda>
        implements AbstractDesktopMorda<DesktopComTrAllMorda> {

    private DesktopComTrAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopComTrAllMorda desktopComTrAll() {
        return desktopComTrAll("production");
    }

    public static DesktopComTrAllMorda desktopComTrAll(String environment) {
        return desktopComTrAll("https", environment);
    }

    public static DesktopComTrAllMorda desktopComTrAll(String scheme, String environment) {
        return new DesktopComTrAllMorda(scheme, "www", environment);
    }

    public static List<DesktopComTrAllMorda> getDefaultList(String environment) {
        return asList(desktopComTrAll(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COMTR_ALL;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path("all").build();
    }


    @Override
    public DesktopComTrAllMorda me() {
        return this;
    }
}
