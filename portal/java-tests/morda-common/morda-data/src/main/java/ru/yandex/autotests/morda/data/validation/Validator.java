package ru.yandex.autotests.morda.data.validation;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/04/15
 */
public class Validator<T> {
    private WebDriver driver;
    private T morda;
    private MordaCleanvars cleanvars;
    private boolean geoLocated = false;

    public Validator(WebDriver driver, T morda) {
        this.driver = driver;
        this.morda = morda;
    }

    public void setDriver(WebDriver driver) {
        this.driver = driver;
    }

    public void setMorda(T morda) {
        this.morda = morda;
    }

    public WebDriver getDriver() {
        return driver;
    }

    public T getMorda() {
        return morda;
    }

    public Validator<T> withCleanvars(MordaCleanvars cleanvars) {
        this.cleanvars = cleanvars;
        return this;
    }

    public void setCleanvars(MordaCleanvars cleanvars) {
        this.cleanvars = cleanvars;
    }

    public MordaCleanvars getCleanvars() {
        return cleanvars;
    }

    public boolean isGeoLocated() {
        return geoLocated;
    }
}
