package ru.yandex.autotests.morda.pages.desktop.smarttv;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.smarttv.blocks.SmartTvSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 18.11.16
 */
public class SmartTvPage implements PageWithSearchBlock<SmartTvSearchBlock> {

    private SmartTvSearchBlock searchBlock;

    public SmartTvPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public SmartTvSearchBlock getSearchBlock() {
        return searchBlock;
    }
}
