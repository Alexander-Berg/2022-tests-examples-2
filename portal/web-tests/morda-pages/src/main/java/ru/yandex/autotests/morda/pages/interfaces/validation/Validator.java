package ru.yandex.autotests.morda.pages.interfaces.validation;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geohelper.GeohelperResponse;
import ru.yandex.autotests.utils.morda.users.User;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/04/15
 */
public class Validator<T> {
    private WebDriver driver;
    private T morda;
    private User user;
    private Cleanvars cleanvars;
    private boolean geoLocated = false;
    private GeohelperResponse geohelperResponse;

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

    public Validator<T> withUser(User user) {
        this.user = user;
        return this;
    }

    public Validator<T> withCleanvars(Cleanvars cleanvars) {
        this.cleanvars = cleanvars;
        return this;
    }


    public void setCleanvars(Cleanvars cleanvars) {
        this.cleanvars = cleanvars;
    }

    public Cleanvars getCleanvars() {
        return cleanvars;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public GeohelperResponse getGeohelperResponse() {
        return geohelperResponse;
    }

    public void setGeohelperResponse(GeohelperResponse geohelperResponse) {
        this.geohelperResponse = geohelperResponse;
        this.geoLocated = geohelperResponse != null;
    }

    public Validator<T> withGeohelperResponse(GeohelperResponse geohelperResponse) {
        this.geohelperResponse = geohelperResponse;
        this.geoLocated = geohelperResponse != null;
        return this;
    }

    public boolean isGeoLocated() {
        return geoLocated;
    }
}
