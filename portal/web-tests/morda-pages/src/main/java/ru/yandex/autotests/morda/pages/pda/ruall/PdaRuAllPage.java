package ru.yandex.autotests.morda.pages.pda.ruall;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.pda.ruall.blocks.LogoBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class PdaRuAllPage implements PageWithLogo<LogoBlock> {

    public PdaRuAllPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }
}
