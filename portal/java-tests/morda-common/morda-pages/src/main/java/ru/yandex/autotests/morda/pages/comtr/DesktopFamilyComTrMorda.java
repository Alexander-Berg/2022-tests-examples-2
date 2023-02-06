package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopFamilyComTrMorda extends ComTrMorda<DesktopFamilyComTrMorda>
        implements AbstractDesktopMorda<DesktopFamilyComTrMorda> {

    private DesktopFamilyComTrMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopFamilyComTrMorda desktopFamilyComTr() {
        return desktopFamilyComTr("production");
    }

    public static DesktopFamilyComTrMorda desktopFamilyComTr(String environment) {
        return desktopFamilyComTr("https", environment);
    }

    public static DesktopFamilyComTrMorda desktopFamilyComTr(String scheme, String environment) {
        return new DesktopFamilyComTrMorda(scheme, "aile", environment);
    }

    public static List<DesktopFamilyComTrMorda> getDefaultList(String environment) {
        return asList(desktopFamilyComTr(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COMTR;
    }

    @Override
    public DesktopFamilyComTrMorda me() {
        return this;
    }
}
