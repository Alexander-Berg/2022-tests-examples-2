package ru.yandex.autotests.morda.pages.touch.com;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.com.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.touch.com.blocks.SearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class TouchComPage implements PageWithLogo<LogoBlock>, PageWithSearchBlock<SearchBlock> {

    public TouchComPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;
    private SearchBlock searchBlock;

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }
}
