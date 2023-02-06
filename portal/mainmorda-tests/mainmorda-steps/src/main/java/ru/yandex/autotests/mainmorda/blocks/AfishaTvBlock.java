package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 26.09.12
 */

@Name("Блок Афиша-Тв")
@FindBy(xpath = "//div[contains(@class,'b-wrapper-tvafisha')]")
public class AfishaTvBlock extends Widget {
    @Name("Таб 'Афиша'")
    @FindBy(xpath = ".//div[contains(@class,'b-tabs__names')]//a[contains(@href,'afisha')]")
    public TvAfishaNewsTab afishaTab;

    @Name("Заголовок отдельного виджета 'Афиша'")
    @FindBy(xpath = "//div[contains(@class,'b-wrapper-afisha')]//div[contains(@class,'b-content-item__title')]//a")
    public HtmlElement afishaTitle;

    @Name("Таб 'Тв'")
    @FindBy(xpath = ".//div[contains(@class,'b-tabs__names')]//a[contains(@href,'tv')]")
    public TvAfishaNewsTab tvTab;

    @Name("Заголовок отдельного виджета 'Тв'")
    @FindBy(xpath = "//div[contains(@class,'b-wrapper-tv')]//div[contains(@class,'b-content-item__title')]//a")
    public HtmlElement tvTitle;

    @Name("События афишы")
    @FindBy(xpath = ".//ul[@class='b-afisha-list']//li[not(contains(@class, 'b-content__list__item_promo'))]")
    public List<AfishaEvent> afishaEvents;

    @Name("Премьера Афиши")
    @FindBy(xpath = ".//div[@class='b-afisha__premiere']")
    public AfishaPremiere afishaPremiere;

    @Name("События TV")
    @FindBy(xpath = ".//ul[@class='b-tv-list']//li[@class='b-content_list__item' and ./table]")
    public List<TvEvent> tvEvents;

    public static class AfishaEvent extends HtmlElement {
        @Name("Жанр события афиши")
        @FindBy(xpath = ".//span[contains(@class,'genre')]")
        public HtmlElement genre;

        @Name("Ссылка на событие афиши")
        @FindBy(xpath = ".//a")
        public HtmlElement eventLink;
    }

    public static class AfishaPremiere extends HtmlElement {
        @Name("Ссылки на премьеру")
        @FindBy(xpath = ".//a")
        public List<HtmlElement> afishaPremiereLinks;

        @Name("Дата примьеры")
        @FindBy(xpath = ".//div[@class='b-afisha__premiere_day']")
        public HtmlElement afishaPremiereDate;
    }

    public static class TvEvent extends HtmlElement {
        @Name("Время тв-события")
        @FindBy(xpath = ".//div[contains(@class,'time')]")
        public HtmlElement time;

        @Name("Ссылка на тв-событие")
        @FindBy(xpath = ".//a")
        public HtmlElement eventLink;

        @Name("Название канала")
        @FindBy(xpath = ".//span[contains(@class,'channel')]")
        public HtmlElement channel;
    }
}