package ru.yandex.autotests.morda.data;

import ru.yandex.autotests.morda.pages.Morda;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public class AbstractCleanvarsData implements CleanvarsData {
    private Morda<?> morda;

    public AbstractCleanvarsData(Morda<?> morda) {
        this.morda = morda;
    }

    @Override
    public Morda<?> getMorda() {
        return morda;
    }
}
