package ru.yandex.autotests.morda.pages.touch.comtrall;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.touch.comtrall.blocks.LogoBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class TouchComTrAllPage implements PageWithLogo<LogoBlock> {

    private WebDriver driver;
    private LogoBlock logoBlock;

    public TouchComTrAllPage(WebDriver driver) {
        this.driver = driver;
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

}
