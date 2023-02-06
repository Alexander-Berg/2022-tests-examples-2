package ru.yandex.autotests.turkey.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.turkey.blocks.all.AllServicesAllList;
import ru.yandex.autotests.turkey.blocks.all.AllServicesBottomList;
import ru.yandex.autotests.turkey.blocks.all.AllServicesFooter;
import ru.yandex.autotests.turkey.blocks.all.AllServicesHeader;
import ru.yandex.autotests.turkey.blocks.all.AllServicesSpecialList;
import ru.yandex.autotests.turkey.blocks.all.AllServicesTopList;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: alex89
 * Date: 29.10.12
 */
public class AllServicesPage {
    public AllServicesPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    public AllServicesHeader allServicesHeader;

    public AllServicesTopList allServicesTopList;

    public AllServicesAllList allServicesAllList;

    public AllServicesBottomList allServicesBottomList;

    public AllServicesSpecialList allServicesSpecialList;

    public AllServicesFooter allServicesFooter;
}
