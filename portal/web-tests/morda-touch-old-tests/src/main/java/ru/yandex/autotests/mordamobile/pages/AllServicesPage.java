package ru.yandex.autotests.mordamobile.pages;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesAllList;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesFooter;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesPageHeader;
import ru.yandex.autotests.mordamobile.blocks.all.AllServicesTopList;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

public class AllServicesPage {
    public AllServicesPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    public AllServicesPageHeader allServicesPageHeader;

    public AllServicesTopList allServicesTopList;

    public AllServicesAllList allServicesAllList;

    public AllServicesFooter allServicesFooter;

}