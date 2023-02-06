package ru.yandex.autotests.morda.pages.desktop.page404;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.page404.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.page404.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class Desktop404Page implements PageWithLogo<LogoBlock>, PageWithSearchBlock<SearchBlock>
{

    public Desktop404Page(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;
    private SearchBlock searchBlock;


    @Override
    public String toString() {
        return "desktop 404";
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }
}
