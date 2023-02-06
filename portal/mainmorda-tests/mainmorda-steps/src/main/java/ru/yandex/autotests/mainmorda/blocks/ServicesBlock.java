package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 17.05.12
 * Блок сервисов
 */
@FindBy(xpath = "//div[contains(@class, 'b-wrapper-services')]")
@Name("Блок сервисов")
public class ServicesBlock extends Widget {
    @Name("Сервисы с подписями")
    @FindBy(xpath = ".//div[@class='b-services__items']/div[@class='b-content_list__item']")
    public List<HtmlLinkWithComment> serviceLinksWithComments;

    @Name("Ссылки на сервисы без подписей")
    @FindBy(xpath = ".//div[@class='b-services__info']//a")
    public List<HtmlElement> serviceLinksWithoutComments;

    @Name("Все ссылки на сервисы")
    @FindBy(xpath = ".//a[contains(@class, 'b-link ') or @class='b-link']")
    public List<HtmlElement> allServices;

    public static class HtmlLinkWithComment extends HtmlElement {
        @Name("Ссылка на сервис")
        @FindBy(xpath = ".//a[contains(@class,'b-services__item')]")
        public HtmlElement serviceLink;

        @Name("Комментарий к сервису")
        @FindBy(xpath = ".//a[contains(@class,'b-link_black')]")
        public HtmlElement serviceComment;
    }

}