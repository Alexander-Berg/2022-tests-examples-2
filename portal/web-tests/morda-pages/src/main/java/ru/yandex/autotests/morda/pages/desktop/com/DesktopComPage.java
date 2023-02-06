package ru.yandex.autotests.morda.pages.desktop.com;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.com.blocks.CountriesBlock;
import ru.yandex.autotests.morda.pages.desktop.com.blocks.FooterBlock;
import ru.yandex.autotests.morda.pages.desktop.com.blocks.HeaderBlock;
import ru.yandex.autotests.morda.pages.desktop.com.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.com.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithCountriesBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopComPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithCountriesBlock<CountriesBlock>, PageWithFooter<FooterBlock>, PageWithHeader<HeaderBlock> {

    public DesktopComPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private CountriesBlock countriesBlock;
    private FooterBlock footerBlock;
    private HeaderBlock headerBlock;

    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public CountriesBlock getCountriesBlock() {
        return countriesBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public HeaderBlock getHeaderBlock() {
        return headerBlock;
    }
}
