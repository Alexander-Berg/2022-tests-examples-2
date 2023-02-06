package ru.yandex.metrika.mobile.push.api.steps;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.qatools.allure.annotations.Step;

@Component
public class ApplicationsSteps {

    @Autowired
    private AuthUtils authUtils;

    @Autowired
    private ApplicationsManageService applicationsManageService;

    @Step("Создание приложения")
    public Application add(long userId, Application application) {
        MetrikaUserDetails user = authUtils.getUserByUid(userId);
        return applicationsManageService.createApplication(application, user, user);
    }

}
