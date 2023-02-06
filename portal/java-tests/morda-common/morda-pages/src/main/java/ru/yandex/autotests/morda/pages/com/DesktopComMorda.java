package ru.yandex.autotests.morda.pages.com;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopComMorda extends ComMorda<DesktopComMorda>
        implements AbstractDesktopMorda<DesktopComMorda> {

    private DesktopComMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static DesktopComMorda desktopCom() {
        return desktopCom("production");
    }

    public static DesktopComMorda desktopCom(String environment) {
        return desktopCom("https", environment);
    }

    public static DesktopComMorda desktopCom(String scheme, String environment) {
        return new DesktopComMorda(scheme, "www", environment);
    }

    public static List<DesktopComMorda> getDefaultList(String environment) {
        return AVAILABLE_LANGUAGES.stream()
                .map(e -> desktopCom(environment).language(e))
                .collect(Collectors.toList());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COM;
    }

    @Override
    public DesktopComMorda me() {
        return this;
    }
}
