package ru.yandex.autotests.morda.pages.desktop.tune.pages;

import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneFooter;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneHeader;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TunePlaces;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;

/**
 * User: asamar
 * Date: 24.08.16
 */
public interface TuneWithPlaces extends PageWithFooter<TuneFooter>, PageWithHeader<TuneHeader> {
    TunePlaces getPlacesBlock();
}
