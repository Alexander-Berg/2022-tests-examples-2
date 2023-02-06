package ru.yandex.autotests.morda.pages.touch.comtr;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLoginDomik;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.FooterBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.HeaderBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.LoginDomikBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.SearchBlock;
import ru.yandex.autotests.morda.steps.WebElementSteps;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class TouchComTrPage implements PageWithSearchBlock<SearchBlock>, PageWithFooter<FooterBlock>,
        PageWithLogo<LogoBlock>, PageWithHeader<HeaderBlock>, PageWithLoginDomik<LoginDomikBlock>
{

    private WebDriver driver;

    public TouchComTrPage(WebDriver driver) {
        this.driver = driver;
        HtmlElementLoader.populate(this, driver);
    }

    private SearchBlock searchBlock;

    private FooterBlock footerBlock;

    private LogoBlock logoBlock;

    private HeaderBlock headerBlock;

    private LoginDomikBlock loginDomikBlock;

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public HeaderBlock getHeaderBlock() {
        return headerBlock;
    }

    @Override
    public LoginDomikBlock getLoginDomik() {
        return loginDomikBlock;
    }

    @Override
    public void openLoginDomik() {
        WebElementSteps.clickOn(headerBlock.getLoginLink());
    }

}
