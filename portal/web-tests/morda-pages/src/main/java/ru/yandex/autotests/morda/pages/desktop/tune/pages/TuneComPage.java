package ru.yandex.autotests.morda.pages.desktop.tune.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneFooter;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneHeader;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneLanguage;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneSearch;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 16.08.16
 */
public class TuneComPage implements TuneWithSearch {

    public TuneSearch searchBlock;
    public TuneHeader headerBlock;
    public TuneFooter footerBlock;
    public TuneLanguage languageBlock;

    public TuneComPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
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

    public TuneLanguage getLanguageBlock() {
        return languageBlock;
    }
}
