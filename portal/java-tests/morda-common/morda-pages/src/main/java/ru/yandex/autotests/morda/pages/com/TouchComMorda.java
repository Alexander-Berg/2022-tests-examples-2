package ru.yandex.autotests.morda.pages.com;

import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;
import java.util.stream.Collectors;

import static ru.yandex.autotests.morda.pages.com.PdaComMorda.pdaCom;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchComMorda extends ComMorda<TouchComMorda>
        implements AbstractTouchMorda<TouchComMorda> {

    private TouchComMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TouchComMorda touchCom() {
        return touchCom("production");
    }

    public static TouchComMorda touchCom(String environment) {
        return touchCom("https", environment);
    }

    public static TouchComMorda touchCom(String scheme, String environment) {
        return new TouchComMorda(scheme, "www", environment);
    }

    public static List<TouchComMorda> getDefaultList(String environment) {
        return AVAILABLE_LANGUAGES.stream()
                .map(e -> touchCom(environment).language(e))
                .collect(Collectors.toList());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_COM;
    }

    @Override
    public TouchComMorda me() {
        return this;
    }
}
