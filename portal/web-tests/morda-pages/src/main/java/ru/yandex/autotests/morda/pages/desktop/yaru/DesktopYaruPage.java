package ru.yandex.autotests.morda.pages.desktop.yaru;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.yaru.blocks.HeaderBlock;
import ru.yandex.autotests.morda.pages.desktop.yaru.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.yaru.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopYaruPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithHeader<HeaderBlock>
{

    public DesktopYaruPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private HeaderBlock headerBlock;

    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public HeaderBlock getHeaderBlock() {
        return headerBlock;
    }
}
