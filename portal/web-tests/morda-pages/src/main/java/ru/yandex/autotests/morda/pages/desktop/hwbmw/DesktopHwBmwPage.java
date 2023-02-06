package ru.yandex.autotests.morda.pages.desktop.hwbmw;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.hwbmw.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopHwBmwPage implements PageWithLogo<LogoBlock>
{

    public DesktopHwBmwPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;

    @Override
    public String toString() {
        return "desktop hw/bmw";
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }
}
