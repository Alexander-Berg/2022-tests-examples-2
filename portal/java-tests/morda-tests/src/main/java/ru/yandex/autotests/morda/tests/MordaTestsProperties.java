package ru.yandex.autotests.morda.tests;

import com.jayway.restassured.RestAssured;
import com.jayway.restassured.parsing.Parser;
import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/05/16
 */
@Resource.Classpath("morda-tests.properties")
public class MordaTestsProperties {
    static {
        RestAssured.registerParser("text/plain", Parser.JSON);
        RestAssured.registerParser("text/javascript", Parser.JSON);
    }

    public MordaTestsProperties() {
        PropertyLoader.populate(this);
    }

    private MordaPagesProperties mordaPagesProperties = new MordaPagesProperties();
    private WeatherPagesProperties weatherPagesProperties = new WeatherPagesProperties();

    public WeatherPagesProperties weather() {
        return weatherPagesProperties;
    }
    public MordaPagesProperties pages() {
        return mordaPagesProperties;
    }

    @Property("morda.tests.mode")
    private String testMode;

    @Property("morda.tests.toPing")
    private boolean toPing;

    @Property("any.host")
    private URI anyHost;

    @Property("any.environment")
    private String anyEnvironment;

    public TestMode getTestMode() {
        return TestMode.fromString(testMode);
    }

    public URI getAnyHost() {
        return anyHost;
    }

    public String getAnyEnvironment() {
        return anyEnvironment;
    }

    public boolean isToPing() {
        return toPing;
    }

    public enum TestMode {
        FULL,
        BASE,
        MONITORING,
        SMOKE;

        public static TestMode fromString(String str) {
            for (TestMode mode : TestMode.values()) {
                if (mode.name().equalsIgnoreCase(str)) {
                    return mode;
                }
            }
            return TestMode.BASE;
        }
    }
}
