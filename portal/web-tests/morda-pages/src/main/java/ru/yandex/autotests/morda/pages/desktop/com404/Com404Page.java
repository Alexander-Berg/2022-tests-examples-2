package ru.yandex.autotests.morda.pages.desktop.com404;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.com404.blocks.ErrorMessageBlock;
import ru.yandex.autotests.morda.pages.desktop.com404.blocks.FooterBlock;
import ru.yandex.autotests.morda.pages.desktop.com404.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.com404.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWith404MessageBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
public class Com404Page implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithFooter<FooterBlock>, PageWith404MessageBlock<ErrorMessageBlock> {

    public Com404Page(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private FooterBlock footerBlock;
    private ErrorMessageBlock errorMessageBlock;

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public ErrorMessageBlock get404MessageBlock() {
        return errorMessageBlock;
    }
}
