package ru.yandex.autotests.morda.pages.desktop.hwlg;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.hwlg.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopHwLgPage implements PageWithLogo<LogoBlock>
{

    public DesktopHwLgPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;

    @Override
    public String toString() {
        return "desktop hw/lg";
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }
}
