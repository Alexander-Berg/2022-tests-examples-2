package ru.yandex.autotests.morda.pages.desktop.tune.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneAdv;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneFooter;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneGeo;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneHeader;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneLanguage;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TunePlaces;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneSearch;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 15.08.16
 */
public class TuneMainPage implements
         TuneWithGeo, TuneWithPlaces, TuneWithLang, TuneWithSearch, TuneWithAdv {

    public TuneMainPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    public TuneFooter footer;
    public TuneHeader header;
    public TuneGeo geoBlock;
    public TunePlaces placesBlock;
    public TuneLanguage langBlock;
    public TuneSearch searchBlock;
    public TuneAdv advBlock;

    @Override
    public TuneLanguage getLangBlock() {
        return langBlock;
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
    public TuneAdv getAdvBlock() {
        return advBlock;
    }

    @Override
    public TuneSearch getSearchBlock() {
        return searchBlock;
    }

    @Override
    public TuneHeader getHeaderBlock() {
        return header;
    }

    @Override
    public TuneFooter getFooterBlock() {
        return footer;
    }
}
