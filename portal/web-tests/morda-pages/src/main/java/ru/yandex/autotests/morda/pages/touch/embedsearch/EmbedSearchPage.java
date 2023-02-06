package ru.yandex.autotests.morda.pages.touch.embedsearch;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.embedsearch.blocks.SearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 29.11.16
 */
public class EmbedSearchPage implements PageWithSearchBlock<SearchBlock> {

    private SearchBlock searchBlock;

    public EmbedSearchPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }
}
