package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;

/**
 * Created by ava1on on 07.04.17.
 */
public class UserParamsParameters extends AbstractFormParameters {

    @FormParameter("action")
    private UserParamsUploadingAction action;

    public UserParamsUploadingAction getAction() {
        return action;
    }

    public void setAction(UserParamsUploadingAction action) {
        this.action = action;
    }

    public UserParamsParameters withAction(UserParamsUploadingAction action) {
        this.action = action;
        return this;
    }

    public static UserParamsParameters userParamsAction(UserParamsUploadingAction action) {
        return new UserParamsParameters().withAction(action);
    }
}
