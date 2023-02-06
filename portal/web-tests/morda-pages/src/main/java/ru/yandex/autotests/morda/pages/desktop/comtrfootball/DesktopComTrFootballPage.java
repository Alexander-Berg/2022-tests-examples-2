package ru.yandex.autotests.morda.pages.desktop.comtrfootball;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.comtrfootball.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.comtrfootball.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.desktop.comtrfootball.blocks.SetHomeBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSetHomeBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopComTrFootballPage implements PageWithLogo<LogoBlock>, PageWithSearchBlock<SearchBlock>,
        PageWithSetHomeBlock<SetHomeBlock>
{

    public DesktopComTrFootballPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;
    private SearchBlock searchBlock;
    private SetHomeBlock setHomeBlock;

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public SetHomeBlock getSetHomeBlock() {
        return setHomeBlock;
    }
}
