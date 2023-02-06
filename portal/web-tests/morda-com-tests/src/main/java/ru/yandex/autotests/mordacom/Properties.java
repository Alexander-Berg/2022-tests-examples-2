package ru.yandex.autotests.mordacom;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: leonsabr
 * Date: 24.10.11
 * Класс со свойствами для профиля .com морды.
 */

public class Properties extends BaseProperties {

    public Properties() {
        super();
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("morda.scheme")
    private String mordaScheme;

    @Property("morda.environment")
    private String mordaEnvironment;

    @Property("morda.useragent.touch.iphone")
    private String mordaUserAgentTouchIphone;

    @Property("morda.useragent.touch.wp")
    private String mordaUserAgentTouchWp;

    @Property("morda.useragent.pda")
    private String mordaUserAgentPda;

    @Property("morda.pages.to.test")
    private List<String> mordaPagesToTest;

    @Property("morda.pages.not.to.test")
    private List<String> mordaPagesNotToTest;



    @Property("morda.com.langs")
    protected String mordaComLangs = "en";

    @Override
    public Domain getBaseDomain() {
        return Domain.COM;
    }

    //for page 404 tests
    @Override
    public Language getLang() {
        return Language.EN;
    }

    public List<Language> getMordaComLangs() {
        List<Language> languages = new ArrayList<>();
        for (String lang : mordaComLangs.replace(" ", "").split(",")) {
            languages.add(Language.getLanguage(lang));
        }
        return languages;
    }




    public String getMordaScheme() {
        return mordaScheme;
    }

    public String getMordaEnvironment() {
        return mordaEnvironment;
    }

    public String getMordaUserAgentTouchIphone() {
        return mordaUserAgentTouchIphone;
    }

    public String getMordaUserAgentTouchWp() {
        return mordaUserAgentTouchWp;
    }

    public String getMordaUserAgentPda() {
        return mordaUserAgentPda;
    }

    public List<MordaType> getMordaPagesNotToTest() {
        if (mordaPagesNotToTest == null || mordaPagesNotToTest.isEmpty()) {
            return new ArrayList<>();
        }

        return mordaPagesNotToTest.stream().map(MordaType::valueOf).collect(Collectors.toList());
    }

    public List<MordaType> getMordaPagesToTest() {
        List<MordaType> result = new ArrayList<>();
        if (mordaPagesToTest == null || mordaPagesToTest.isEmpty()) {
            result.addAll(asList(MordaType.values()));
        } else {
            mordaPagesToTest.stream().forEach((page) -> result.add(MordaType.valueOf(page)));
        }

        result.removeAll(getMordaPagesNotToTest());

        return result;
    }






}
