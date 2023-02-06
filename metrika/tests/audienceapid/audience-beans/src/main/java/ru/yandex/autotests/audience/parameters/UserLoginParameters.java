package ru.yandex.autotests.audience.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by konkov on 14.07.2016.
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
