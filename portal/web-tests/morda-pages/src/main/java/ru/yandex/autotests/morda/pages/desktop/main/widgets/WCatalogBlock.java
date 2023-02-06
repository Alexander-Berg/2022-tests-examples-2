package ru.yandex.autotests.morda.pages.desktop.main.widgets;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Link;

import java.util.ArrayList;
import java.util.List;

/**
 * User: asamar
 * Date: 13.01.2016.
 */
public class WCatalogBlock extends HtmlElement{
//    public WCatalogBlock(WebDriver driver) {
////        HtmlElementLoader.populate(this, driver);
////    }

    @Name("Виджеты на странице каталога")
    @FindBy(xpath = "//div[@class='b-catalog-widget']/div[contains(@class,'wrapper')]/a")
    public List<HtmlElement> widgetsInCatalog;

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
