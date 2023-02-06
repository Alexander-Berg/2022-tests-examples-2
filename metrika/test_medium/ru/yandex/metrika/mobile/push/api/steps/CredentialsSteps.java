package ru.yandex.metrika.mobile.push.api.steps;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.qatools.allure.annotations.Step;

@Component
public class CredentialsSteps {

    @Autowired
    private MySqlJdbcTemplate mobileTemplate;

    @Step("Добавление валидных учетных данных")
    public void add(long appId) {
        mobileTemplate.update(
                "INSERT IGNORE INTO apple_push_credentials(application_id, cert, password) VALUES (?, ?, ?)",
                appId, new byte[0], "password");
        mobileTemplate.update(
                "INSERT IGNORE INTO android_push_credentials(application_id, auth_key) VALUES (?, ?)",
                appId, "key");
    }

}
