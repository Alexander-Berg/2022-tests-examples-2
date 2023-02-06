package ru.yandex.autotests.internalapid.tests;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import com.google.common.collect.Sets;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.apache.commons.io.IOUtils;
import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import uk.co.datumedge.hamcrest.json.SameJSONAs;

import ru.yandex.autotests.internalapid.beans.data.Counters;
import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.steps.IdmSteps;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.internalapid.steps.IdmSteps.EXTERNAL_COUNTER_GRANT_ROLE;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Title("Тесты ручек IDM")
public class IdmTest extends InternalApidTest {

    private final static String PIN_CODE_ROLE = "delegate_read";
    private final static String CRM_SUPPORT_BASE_ROLE = "crm_support_base";

    @Test
    @Title("Тест ручки /idm/info")
    public void testInfo() {
        try {
            String expected = IOUtils.toString(IdmSteps.class.getResource("/idm_info.json"), StandardCharsets.UTF_8);
            String actual = userSteps.onIdmSteps().getIdmInfo();
            assertThat("/idm/info вернул ожидаемые данные", actual, SameJSONAs.sameJSONAs(expected).allowingExtraUnexpectedFields());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    @Title("Тест ручки /idm/get-user-roles")
    public void getUserRoles() {
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), "yamanager", Users.MANAGER_2.get(User.LOGIN));
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), EXTERNAL_COUNTER_GRANT_ROLE,
                Users.MANAGER_2.get(User.LOGIN), Optional.empty(), Optional.of(Counters.SIMPLE_COUNTER.getId()), Optional.of(GrantType.VIEW), Optional.of(false));
        final JsonObject userRoles = userSteps.onIdmSteps().getUserRoles(Users.MANAGER_2.get(User.LOGIN));
        Set<String> roleIds = userSteps.onIdmSteps().extractRoleIds(userRoles);

        assertThat("Пользователю добавились роли", roleIds, Matchers.equalTo(Sets.newHashSet("yamanager", EXTERNAL_COUNTER_GRANT_ROLE)));
    }

    @Test
    @Title("Создание роли для пин-кодов /idm/add-role")
    public void pinCodeRoles() {
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), PIN_CODE_ROLE, Users.PINCODE_DELEGATE_USER.get(User.LOGIN), Users.PINCODE_TARGET_USER.get(User.LOGIN));
        final JsonObject userRoles = userSteps.onIdmSteps().getUserRoles(Users.MANAGER_2.get(User.LOGIN));
        assertThat("Пользователю добавились роли", userSteps.onIdmSteps().extractRoleIds(userRoles), Matchers.equalTo(Sets.newHashSet(PIN_CODE_ROLE)));
    }

    @Test
    @Title("Создание базовой роли саппорта для пин-кодов /idm/add-role")
    public void baseSupportPinCodeRoles() {
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), CRM_SUPPORT_BASE_ROLE, Users.PINCODE_DELEGATE_USER.get(User.LOGIN), Users.PINCODE_TARGET_USER.get(User.LOGIN));
        final JsonObject userRoles = userSteps.onIdmSteps().getUserRoles(Users.MANAGER_2.get(User.LOGIN));
        assertThat("Пользователю добавились роли", userSteps.onIdmSteps().extractRoleIds(userRoles), Matchers.equalTo(Sets.newHashSet(CRM_SUPPORT_BASE_ROLE)));
    }

    @Test
    @Title("Тест ручки /idm/get-all-roles")
    public void getAllRoles() throws InterruptedException {
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), "yamanager", Users.MANAGER_2.get(User.LOGIN));
        userSteps.onIdmSteps().addRole(Users.MANAGER_2.get(User.LOGIN), EXTERNAL_COUNTER_GRANT_ROLE,
                Users.MANAGER_2.get(User.LOGIN), Optional.empty(), Optional.of(Counters.SIMPLE_COUNTER.getId()), Optional.of(GrantType.VIEW), Optional.of(false));

        final JsonObject allRoles = userSteps.onIdmSteps().getAllRoles();
        Set<JsonObject> userRoles = StreamSupport.stream(allRoles.get("users").getAsJsonArray().spliterator(), false)
                .map(JsonElement::getAsJsonObject)
                .filter(us -> Users.MANAGER_2.get(User.LOGIN).equals(us.get("login").getAsString()))
                .collect(Collectors.toSet());

        Set<String> roleIds = userRoles.stream()
                .flatMap(ur -> userSteps.onIdmSteps().extractRoleIds(ur).stream())
                .collect(Collectors.toSet());

        assertThat("В общем списке ролей есть добавленные роли пользователя", roleIds, Matchers.equalTo(Sets.newHashSet("yamanager", "external_counter_grant")));
    }


    @Before
    @After
    public void clean() {
        userSteps.onIdmSteps().removeRole(Users.MANAGER_2.get(User.LOGIN), "yamanager", Users.MANAGER_2.get(User.LOGIN));
        userSteps.onIdmSteps().removeRole(Users.MANAGER_2.get(User.LOGIN), EXTERNAL_COUNTER_GRANT_ROLE,
                Users.MANAGER_2.get(User.LOGIN), Optional.empty(), Optional.of(Counters.SIMPLE_COUNTER.getId()), Optional.of(GrantType.VIEW), Optional.of(false));
        userSteps.onIdmSteps().removeRole(Users.MANAGER_2.get(User.LOGIN), PIN_CODE_ROLE, Users.PINCODE_DELEGATE_USER.get(User.LOGIN), Users.PINCODE_TARGET_USER.get(User.LOGIN));
        userSteps.onIdmSteps().removeRole(Users.MANAGER_2.get(User.LOGIN), CRM_SUPPORT_BASE_ROLE, Users.PINCODE_DELEGATE_USER.get(User.LOGIN), Users.PINCODE_TARGET_USER.get(User.LOGIN));
    }

}
