package ru.yandex.autotests.morda.pages.desktop.tune.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneFooter;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneGeo;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneHeader;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TunePlaces;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneSearch;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 15.08.16
 */
public class TuneComTrPage implements
         TuneWithGeo, TuneWithPlaces, TuneWithSearch {

    public TuneGeo geoBlock;
    public TunePlaces placesBlock;
    public TuneSearch searchBlock;
    public TuneHeader headerBlock;
    public TuneFooter footerBlock;


    public TuneComTrPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public TuneGeo getGeoBlock() {
        return geoBlock;
    }

    @Override
    public TunePlaces getPlacesBlock() {
        return placesBlock;
    }

    @Override
    public TuneSearch getSearchBlock() {
        return searchBlock;
    }

    @Override
    public TuneFooter getFooterBlock() {
        return footerBlock;
    }

    @Override
    public TuneHeader getHeaderBlock() {
        return headerBlock;
    }
}
