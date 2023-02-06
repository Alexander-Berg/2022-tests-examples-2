package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchComTrMorda extends ComTrMorda<TouchComTrMorda>
        implements AbstractTouchMorda<TouchComTrMorda> {

    private TouchComTrMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TouchComTrMorda touchComTr() {
        return touchComTr("production");
    }

    public static TouchComTrMorda touchComTr(String environment) {
        return touchComTr("https", environment);
    }

    public static TouchComTrMorda touchComTr(String scheme, String environment) {
        return new TouchComTrMorda(scheme, "www", environment);
    }

    public static List<TouchComTrMorda> getDefaultList(String environment) {
        return asList(touchComTr(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_COMTR;
    }

    @Override
    public TouchComTrMorda me() {
        return this;
    }
}
