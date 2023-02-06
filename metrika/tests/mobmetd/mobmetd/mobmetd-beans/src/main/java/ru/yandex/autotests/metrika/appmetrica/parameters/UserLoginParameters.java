package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by graev on 15/12/2016.
 */
public class UserLoginParameters extends AbstractFormParameters {
    @FormParameter("user_login")
    private String userLogin;

    public String getUserLogin() {
        return userLogin;
    }

    public void setUserLogin(String userLogin) {
        this.userLogin = userLogin;
    }

    public UserLoginParameters withUserLogin(final String userLogin) {
        this.userLogin = userLogin;
        return this;
    }

    public static UserLoginParameters userLogin(String userLogin) {
        return new UserLoginParameters().withUserLogin(userLogin);
    }
}