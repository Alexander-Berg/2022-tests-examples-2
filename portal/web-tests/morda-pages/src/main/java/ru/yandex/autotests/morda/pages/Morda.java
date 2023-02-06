package ru.yandex.autotests.morda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public abstract class Morda<T> {

    protected String scheme;
    protected MordaEnvironment environment;
    protected Language language;
    protected Region region;

    protected Morda(String scheme, MordaEnvironment environment) {
        this.scheme = scheme;
        this.environment = environment;
    }

    public abstract MordaType getMordaType();

    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    public abstract MordaAllureBaseRule getRule(DesiredCapabilities caps);

    public abstract T getPage(WebDriver driver);

    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
    }

    public abstract URI getUrl();

    public URI getPassportUrl() {
        return getPassportUrl("passport");
    }

    public abstract URI getPassportUrl(String passportEnv);

    public URI getTuneUrl() {
        return getTuneUrl("tune");
    }

    public abstract URI getTuneUrl(String tuneEnv);

    public abstract URI getSerpUrl();

    public String getScheme() {
        return scheme;
    }

    public void setScheme(String scheme) {
        this.scheme = scheme;
    }

    public MordaEnvironment getEnvironment() {
        return environment;
    }

    public void setEnvironment(MordaEnvironment environment) {
        this.environment = environment;
    }

    public Language getLanguage() {
        return language;
    }

    protected void setLanguage(Language language) {
        this.language = language;
    }

    public Region getRegion() {
        return region;
    }

    protected void setRegion(Region region) {
        this.region = region;
    }

    public abstract String getCookieDomain();

    public abstract String getFeature();

    public static class MordaEnvironment {
        private String prefix;
        private String environment;
        private boolean availableSerp;

        public MordaEnvironment(String prefix, String environment, boolean availableSerp) {
            this.prefix = prefix;
            this.environment = environment;
            this.availableSerp = availableSerp;
        }

        public String getPrefix() {
            return prefix;
        }

        public String getEnvironment() {
            return environment;
        }

        public boolean isAvailableSerp() {
            return availableSerp;
        }

        public String parseEnvironment() {
            if (environment == null || environment.isEmpty()) {
                throw new IllegalArgumentException("Environment must not be null or empty");
            }

            if (environment.equals("production")) {
                return prefix + ".";
            }

            if (environment.equals("serp")) {
                return availableSerp ? "" : prefix + ".";
            }

            return prefix + "-" + environment + ".";
        }

    }

}
