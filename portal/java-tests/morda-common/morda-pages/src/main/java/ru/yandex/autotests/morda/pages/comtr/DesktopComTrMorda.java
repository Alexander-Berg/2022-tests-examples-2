package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopComTrMorda extends ComTrMorda<DesktopComTrMorda>
        implements AbstractDesktopMorda<DesktopComTrMorda> {

    private DesktopComTrMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopComTrMorda desktopComTr() {
        return desktopComTr("production");
    }

    public static DesktopComTrMorda desktopComTr(String environment) {
        return desktopComTr("https", environment);
    }

    public static DesktopComTrMorda desktopComTr(String scheme, String environment) {
        return new DesktopComTrMorda(scheme, "www", environment);
    }

    public static List<DesktopComTrMorda> getDefaultList(String environment) {
        return asList(desktopComTr(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COMTR;
    }

    @Override
    public DesktopComTrMorda me() {
        return this;
    }
}
