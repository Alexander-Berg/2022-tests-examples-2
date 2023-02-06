package ru.yandex.autotests.morda.pages.desktop.op;

import org.openqa.selenium.WebDriver;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopOpPage {

    public DesktopOpPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

}
