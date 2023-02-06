package ru.yandex.autotests.morda.pages.desktop.comtr;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.comtr.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.comtr.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.desktop.comtr.blocks.SetHomeBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSetHomeBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopComTrPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithSetHomeBlock<SetHomeBlock>
{

    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private SetHomeBlock setHomeBlock;

    public DesktopComTrPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SetHomeBlock getSetHomeBlock() {
        return setHomeBlock;
    }
}
