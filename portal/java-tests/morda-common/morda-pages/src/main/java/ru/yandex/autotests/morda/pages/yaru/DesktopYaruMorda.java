package ru.yandex.autotests.morda.pages.yaru;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopYaruMorda extends YaruMorda<DesktopYaruMorda>
        implements AbstractDesktopMorda<DesktopYaruMorda> {

    private DesktopYaruMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopYaruMorda desktopYaru() {
        return desktopYaru("production");
    }

    public static DesktopYaruMorda desktopYaru(String environment) {
        return desktopYaru("https", environment);
    }

    public static DesktopYaruMorda desktopYaru(String scheme, String environment) {
        return new DesktopYaruMorda(scheme, "www", environment);
    }

    public static List<DesktopYaruMorda> getDefaultList(String environment) {
        return asList(desktopYaru(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_YARU;
    }

    @Override
    public DesktopYaruMorda me() {
        return this;
    }
}
