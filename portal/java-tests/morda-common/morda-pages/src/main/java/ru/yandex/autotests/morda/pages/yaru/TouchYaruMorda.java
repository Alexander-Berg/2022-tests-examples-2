package ru.yandex.autotests.morda.pages.yaru;

import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchYaruMorda extends YaruMorda<TouchYaruMorda>
        implements AbstractTouchMorda<TouchYaruMorda> {

    private TouchYaruMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TouchYaruMorda touchYaru() {
        return touchYaru("production");
    }

    public static TouchYaruMorda touchYaru(String environment) {
        return touchYaru("https", environment);
    }

    public static TouchYaruMorda touchYaru(String scheme, String environment) {
        return new TouchYaruMorda(scheme, "www", environment);
    }

    public static List<TouchYaruMorda> getDefaultList(String environment) {
        return asList(touchYaru(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_YARU;
    }

    @Override
    public TouchYaruMorda me() {
        return this;
    }
}
