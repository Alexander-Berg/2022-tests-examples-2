package ru.yandex.autotests.morda.pages.desktop.tune.pages;

import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneAdv;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneFooter;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneHeader;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;

/**
 * User: asamar
 * Date: 24.08.16
 */
public interface TuneWithAdv extends PageWithFooter<TuneFooter>, PageWithHeader<TuneHeader> {
    TuneAdv getAdvBlock();
}
