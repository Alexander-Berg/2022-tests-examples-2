package ru.yandex.autotests.morda.pages.spok;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopSpokMorda extends SpokMorda<DesktopSpokMorda>
        implements AbstractDesktopMorda<DesktopSpokMorda> {

    private DesktopSpokMorda(String scheme, String environment, MordaDomain domain) {
        super(scheme, environment, domain);
    }

    public static DesktopSpokMorda desktopSpok(MordaDomain domain) {
        return desktopSpok("production", domain);
    }

    public static DesktopSpokMorda desktopSpok(String environment, MordaDomain domain) {
        return desktopSpok("https", environment, domain);
    }

    public static DesktopSpokMorda desktopSpok(String scheme, String environment, MordaDomain domain) {
        return new DesktopSpokMorda(scheme, environment, domain);
    }

    public static List<DesktopSpokMorda> getDefaultList(String environment) {
        return MordaDomain.getSpokDomains().stream()
                .filter(e -> e != MordaDomain.MD)
                .map(d -> desktopSpok(environment, d))
                .collect(Collectors.toList());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN;
    }

    @Override
    public DesktopSpokMorda me() {
        return this;
    }
}
