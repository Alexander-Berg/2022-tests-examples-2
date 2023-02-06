package ru.yandex.autotests.morda.pages.desktop.firefox;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.firefox.blocks.FirefoxLogoBlock;
import ru.yandex.autotests.morda.pages.desktop.firefox.blocks.FooterBlock;
import ru.yandex.autotests.morda.pages.desktop.firefox.blocks.InformersBlock;
import ru.yandex.autotests.morda.pages.desktop.firefox.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.firefox.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFirefoxLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithInformers;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopFirefoxPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithFirefoxLogo<FirefoxLogoBlock>, PageWithFooter<FooterBlock>, PageWithInformers<InformersBlock>
{

    public DesktopFirefoxPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private SearchBlock searchBlock;

    private FooterBlock footerBlock;

    private LogoBlock logoBlock;

    private FirefoxLogoBlock firefoxLogoBlock;

    private InformersBlock informersBlock;

    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public String toString() {
        return "desktop firefox";
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public FirefoxLogoBlock getFirefoxLogo() {
        return firefoxLogoBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public InformersBlock getInformersBlock() {
        return informersBlock;
    }
}
