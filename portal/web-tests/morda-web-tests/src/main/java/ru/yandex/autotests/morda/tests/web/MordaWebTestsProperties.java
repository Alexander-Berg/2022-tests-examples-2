package ru.yandex.autotests.morda.tests.web;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/03/15
 */
@Resource.Classpath("morda-web-tests.properties")
public class MordaWebTestsProperties {

    public MordaWebTestsProperties() {
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

    public static void main(String[] args) {
        System.out.println(new MordaWebTestsProperties().getMordaPagesToTest());
    }
}
