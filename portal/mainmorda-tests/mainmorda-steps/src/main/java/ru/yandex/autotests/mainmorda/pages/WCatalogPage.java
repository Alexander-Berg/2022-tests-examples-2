package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.WidgetInCatalog;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Link;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.ArrayList;
import java.util.List;

/**
 * User: alex89
 * Date: 13.12.12
 */

public class WCatalogPage {
    public WCatalogPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Виджеты на странице каталога")
    @FindBy(xpath = "//div[@class='b-catalog-widget']/div[contains(@class,'wrapper')]/a")
    public List<WidgetInCatalog> widgetsInCatalog;

    @Name("Ссылка 'следующая'")
    @FindBy(xpath = "//a[contains(@class,'_next')]")
    public Link next;

    @Name("Рубрики каталога")
    @FindBy(xpath = "//li[contains(@class,'category')]/a")
    public List<Link> rubricsOfCatalog;

    @Name("Каталог в режиме редактирования") //признак открытия каталога
    @FindBy(xpath = "//div[contains(@class,'b-catalog-widget')]")
    public HtmlElement catalog;

    public List<Link> getEditCatalogRubricLink(String rubricName) {
        List<Link> targetRubrics = new ArrayList<Link>();
        for (Link rubric : rubricsOfCatalog) {
            if (rubric.getReference().contains(rubricName)) {
                targetRubrics.add(rubric);
            }
        }
        return targetRubrics;
    }
}
