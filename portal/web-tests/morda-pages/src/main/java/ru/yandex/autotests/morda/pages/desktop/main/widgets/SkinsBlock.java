package ru.yandex.autotests.morda.pages.desktop.main.widgets;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.themes.Group;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers;

import java.util.List;

import static java.util.Arrays.stream;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_STATLOG;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 26.11.2015.
 */
@Name("Блок с темами")
@FindBy(xpath = "//div[contains(@class, 'b-themes-catalog_current-group_')]")
public class SkinsBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    public List<Skin> skins;
    public List<ThemeGroup> themeGroups;

    @Name("Стрелка вправо")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__arrow_scroll_right')]")
    public HtmlElement rightArrow;

    @Name("Сбросить тему")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__pull-right')]/a[1]")
    public HtmlElement reset;

    @Name("Отмена")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__pull-right')]/a[2]")
    public HtmlElement cancell;

    @Name("Сохранить тему")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__pull-right')]/a[3]")
    public HtmlElement save;

    @Override
    @Step("Check themes block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateGroups(themeGroups, validator),
                        validateReset(reset, validator),
                        validateCancell(cancell, validator),
                        validateSave(save, validator)
                );
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateGroups(List<ThemeGroup> themeGroup,
                                                     Validator<? extends DesktopMainMorda> validator) {

        HierarchicalErrorCollector collector = collector();

        ThemeGroup activeGroup = themeGroup.stream()
                .filter(ThemeGroup::isActive)
                .findFirst()
                .get();

        List<Skin> showingSkins = activeGroup.getShowingSkins(skins);

        List<Group> groups = validator.getCleanvars().getThemes().getGroup();
        Group allGroup = new ru.yandex.autotests.mordabackend.beans.themes.Group();
        allGroup.setId("all");
        groups.add(0, allGroup);

        validateThemes(showingSkins, activeGroup.getGroupName(), validator);

        for (int i = 0; i != Math.min(themeGroup.size(), groups.size()); i++) {
            collector.check(validateGroup(themeGroup.get(i), groups.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(themeGroup, hasSize(groups.size()))
        );
        collector.check(countCollector);

        return collector();
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateGroup(ThemeGroup themeGroup,
                                                    Group group,
                                                    Validator<? extends DesktopMainMorda> validator) {

        return collector()
                .check(shouldSeeElement(themeGroup))
                .check(shouldSeeElementMatchingTo(themeGroup,
                                allOfDetailed(
                                        hasAttribute(DATA_STATLOG, equalTo("catalogskin.tab." + group.getId())),
                                        hasText(getTranslation(
                                                "home",
                                                "skinsGroup",
                                                group.getId(),
                                                validator.getMorda().getLanguage()))
                                ))
                );
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateThemes(List<Skin> skins,
                                                     String groupId,
                                                     Validator<? extends DesktopMainMorda> validator) {
        HierarchicalErrorCollector collector = collector();
        List<String> themes;

        if (groupId.equals("all")) {
            themes = validator.getCleanvars().getThemes().getList().stream().map(Theme::getId).collect(toList());
        } else {
            themes = validator.getCleanvars().getThemes().getGroup().stream()
                    .filter(e -> e.getId().equals(groupId))
                    .findFirst()
                    .get()
                    .getThemesArray();
        }


        for (int i = 0; i != Math.min(skins.size(), themes.size()); i++) {
            collector.check(validateSkin(skins.get(i), themes.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(skins, hasSize(themes.size()))
        );
        collector.check(countCollector);


        return collector;
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateSkin(Skin skin,
                                                   String id,
                                                   Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(skin))
                .check(
                        shouldSeeElement(skin.icon),
                        shouldSeeElement(skin.name),
                        shouldSeeElement(skin.img)
                )
                .check(
                        shouldSeeElementMatchingTo(skin, allOfDetailed(
                                        hasAttribute(TITLE, equalTo(getTranslation(
                                                "home",
                                                "allskins",
                                                id,
                                                validator.getMorda().getLanguage()))),
                                        hasAttribute(HREF, startsWith(validator.getMorda().getThemeUrl() + id)))
                        ),
                        shouldSeeElementMatchingTo(skin.icon,
                                WrapsElementMatchers.hasAttribute(
                                        "data-preview_url",
                                        equalTo("/skins/bender/" + id + "/preview.jpg"))
                        ),
                        shouldSeeElementMatchingTo(skin.name,
                                hasText(getTranslation(
                                        "home",
                                        "allskins",
                                        id,
                                        validator.getMorda().getLanguage()))
                        ),
                        shouldSeeElementMatchingTo(skin.img,
                                hasAttribute(SRC,
                                        equalTo("/skins/bender/" + id + "/preview.jpg"))
                        )
                );
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateReset(HtmlElement reset, Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(reset))
                .check(shouldSeeElementMatchingTo(reset,
                        allOfDetailed(
                                hasAttribute(HREF,
                                        startsWith(validator.getMorda().getUrl().toString())),
                                hasText(getTranslation("home", "skinslist", "reset", validator.getMorda().getLanguage())
                                )
                        )
                ));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateCancell(HtmlElement cancell, Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(cancell))
                .check(shouldSeeElementMatchingTo(cancell,
                        allOfDetailed(
                                hasAttribute(HREF,
                                        startsWith(validator.getMorda().getUrl().toString())),
                                hasText(getTranslation("home", "skinslist", "decline", validator.getMorda().getLanguage())
                                )
                        )
                ));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateSave(HtmlElement save, Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(save))
                .check(shouldSeeElementMatchingTo(save,
                        allOfDetailed(
                                hasAttribute(HREF, equalTo("")),
//                                        startsWith(validator.getMorda().getUrl().toString())),
                                hasText(getTranslation("home", "skinslist", "accept", validator.getMorda().getLanguage())
                                )
                        )
                ));
    }


    @Step("{0}")
    public HierarchicalErrorCollector validateShareSkin(String skinId, Validator<? extends DesktopMainMorda> validator) {

        Skin skin = this.skins.stream().filter(sk -> sk.getId().equals(skinId)).findFirst().get();
        return collector()
                .check(shouldSeeElement(skin))
                .check(shouldSeeElement(skin.shareSkin))
                .check(
                        shouldSeeElement(skin.shareSkin.vkIcon),
                        shouldSeeElement(skin.shareSkin.fbIcon),
                        shouldSeeElement(skin.shareSkin.odnoklIcon)
                )
                .check(
                        shouldSeeElementMatchingTo(skin.shareSkin.vkIcon,
                                WrapsElementMatchers.hasAttribute("data-url", validator.getMorda().getThemeUrl() + skinId)),
                        shouldSeeElementMatchingTo(skin.shareSkin.vkLink,
                                hasAttribute(HREF, startsWith("https://vk.com/share.php"))),
                        shouldSeeElementMatchingTo(skin.shareSkin.fbIcon,
                                WrapsElementMatchers.hasAttribute("data-url", validator.getMorda().getThemeUrl() + skinId)),
                        shouldSeeElementMatchingTo(skin.shareSkin.fbLink,
                                hasAttribute(HREF, startsWith("https://www.facebook.com/sharer.php"))),
                        shouldSeeElementMatchingTo(skin.shareSkin.odnoklIcon,
                                WrapsElementMatchers.hasAttribute("data-url", validator.getMorda().getThemeUrl() + skinId)),
                        shouldSeeElementMatchingTo(skin.shareSkin.odnoklLink,
                                hasAttribute(HREF, startsWith("https://connect.ok.ru/offer")))
                );
    }


    @Name("Группа")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__tab ')]")
    public static class ThemeGroup extends HtmlElement {

        public String getGroupName() {
            String[] eee = this.getAttribute("class").split(" ");
            return this.getAttribute("class").split(" ")[1].replace("b-themes-catalog__tab_name_", "");
        }

        public boolean isActive() {
            return this.getAttribute("class").split(" ")[2].contains("b-themes-catalog__tab_active_true");
        }

        public List<Skin> getShowingSkins(List<Skin> skins) {
            return skins.stream().filter(e -> e.hasGroup(getGroupName())).collect(toList());
        }
    }

    @Name("Скин")
    @FindBy(xpath = ".//a[contains(@class, 'b-themes-catalog__theme-item ')]")
    public static class Skin extends HtmlElement {

        @Name("Иконка")
        @FindBy(xpath = ".//div[1]")
        public HtmlElement icon;

        @Name("Картинка")
        @FindBy(xpath = ".//div[1]/img")
        public HtmlElement img;

        @Name("Название скина")
        @FindBy(xpath = ".//div[2]")
        public HtmlElement name;

        public ShareSkin shareSkin;

        public boolean hasGroup(String groupName) {
            return this.getAttribute("class").contains("b-themes-catalog__theme-item_group-" + groupName + "_true");
        }

        public String getId() {
            return stream(this.getAttribute("class").split(" "))
                    .filter(e -> e.contains("b-themes-catalog__theme-item_id_"))
                    .findFirst()
                    .get()
                    .replace("b-themes-catalog__theme-item_id_", "");
        }
    }

    @Name("Поделяшки")
    @FindBy(xpath = ".//div[contains(@class, 'b-themes-catalog__theme-item-share_enable_true')]")
    public static class ShareSkin extends HtmlElement {

        @Name("Поделиться темой")
        @FindBy(xpath = ".//div[1]")
        public HtmlElement header;

        @Name("Иконка Вконтакте")
        @FindBy(xpath = ".//div[contains(@data-services, 'vkontakte')]")
        public HtmlElement vkIcon;

        @Name("Ссылка Вконтакте")
        @FindBy(xpath = ".//div[contains(@data-services, 'vkontakte')]//a")
        public HtmlElement vkLink;

        @Name("Иконка Фэйсбук")
        @FindBy(xpath = ".//div[contains(@data-services, 'facebook')]")
        public HtmlElement fbIcon;

        @Name("Ссылка Фэйсбук")
        @FindBy(xpath = ".//div[contains(@data-services, 'facebook')]//a")
        public HtmlElement fbLink;

        @Name("Иконка одноклассники")
        @FindBy(xpath = ".//div[contains(@data-services, 'odnoklassniki')]")
        public HtmlElement odnoklIcon;

        @Name("Ссылка одноклассники")
        @FindBy(xpath = ".//div[contains(@data-services, 'odnoklassniki')]//a")
        public HtmlElement odnoklLink;
    }

}
