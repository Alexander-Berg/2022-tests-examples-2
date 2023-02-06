package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.JsonObject;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.idm.model.Slug;
import ru.yandex.metrika.idm.response.AddRoleResponse;
import ru.yandex.metrika.idm.response.Response;
import ru.yandex.qatools.allure.annotations.Step;

public class IdmSteps extends HttpClientLiteFacade {


    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static final String EXTERNAL_COUNTER_GRANT_ROLE = "external_counter_grant";


    public IdmSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Добавить роль {1} для {0}")
    public AddRoleResponse addRole(String staffLogin, String role, String passportLogin) {
        return addRole(staffLogin, role, passportLogin, Optional.empty(), Optional.empty(), Optional.empty(), Optional.empty());
    }

    @Step("Добавить роль {1} для логина {0} для пользователя {2}")
    public AddRoleResponse addRole(String staffLogin, String role, String passportLogin, String userLogin) {
        return addRole(staffLogin, role, passportLogin, Optional.of(userLogin), Optional.empty(), Optional.empty(), Optional.empty());
    }

    @Step("Добавить роль {1} для {0}")
    public AddRoleResponse addRole(String staffLogin, String role, String passportLogin, Optional<String> userLogin, Optional<Long> counterId, Optional<GrantType> grantType, Optional<Boolean> partnerDataAccess) {
        for (int i = 0; i < 3; i++) { //up to three retries, if failed
            AddRoleResponse response = post(AddRoleResponse.class, "idm/add-role", null,
                    makeModifyRoleParameters(staffLogin, userLogin,
                            role, passportLogin, counterId, grantType, partnerDataAccess));
            if (response.getCode() != 1) return response;
        }
        return null;
    }

    @Step("Удалить роль {1} для {0}")
    public Response removeRole(String staffLogin, String role, String passportLogin,String userLogin) {
        return removeRole(staffLogin, role, passportLogin, Optional.of(userLogin), Optional.empty(), Optional.empty(), Optional.empty());
    }

    @Step("Удалить роль {1} для {0}")
    public Response removeRole(String staffLogin, String role, String passportLogin) {
        return removeRole(staffLogin, role, passportLogin, Optional.empty(), Optional.empty(), Optional.empty(), Optional.empty());
    }

    @Step("Удалить роль {1} для {0}")
    public Response removeRole(String staffLogin, String role, String passportLogin, Optional<String> userLogin, Optional<Long> counterId, Optional<GrantType> grantType, Optional<Boolean> partnerDataAccess) {
        return post(Response.class, "idm/remove-role", null, makeModifyRoleParameters(staffLogin, userLogin, role, passportLogin, counterId, grantType, partnerDataAccess));
    }

    private FreeFormParameters makeModifyRoleParameters(String staffLogin, Optional<String> userLogin, String role, String passportLogin,
                                                        Optional<Long> counterId, Optional<GrantType> grantType, Optional<Boolean> partnerDataAccess) {
        Map<Slug, String> roles = new HashMap<>();
        roles.put(Slug.METRIKA, role);
        Map<String, String> fields = new HashMap<>();
        fields.put("passport-login", passportLogin);
        userLogin.ifPresent(ul -> fields.put("user_login", ul));
        counterId.ifPresent(id -> fields.put("counter_id", id.toString()));
        grantType.ifPresent(gt -> fields.put("grant_type", gt.value()));
        partnerDataAccess.ifPresent(pda ->fields.put("partner_data_access", String.valueOf(pda)));

        final FreeFormParameters parameters;
        try {
            parameters = new FreeFormParameters().append("login", staffLogin)
                    .append("role", objectMapper.writeValueAsString(roles))
                    .append("fields", objectMapper.writeValueAsString(fields));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        return parameters;
    }

    @Step("Вызвать ручку /idm/info")
    public String getIdmInfo(IFormParameters... parameters) {
        return get(JsonObject.class, "/idm/info", parameters).toString();
    }

    @Step("Запросить роли пользователя {0}")
    public JsonObject getUserRoles(String staffLogin) {
        return get(JsonObject.class, "/idm/get-user-roles", FreeFormParameters.makeParameters("login", staffLogin));
    }

    @Step("Запросить все роли")
    public JsonObject getAllRoles() {
        JsonObject result;
        for (int i = 0; i < 3; i++) {
            result = get(JsonObject.class, "/idm/get-all-roles");
            if (result.get("code") != null && "0".equals(result.get("code").getAsString())) {
                return result;
            }
        }
        return null;
    }

    public Set<String> extractRoleIds(JsonObject userRoles) {
        return StreamSupport.stream(userRoles.get("roles").getAsJsonArray().spliterator(), false)
                .map(el -> el.getAsJsonArray().get(0).getAsJsonObject().get(Slug.METRIKA.value()).getAsString()).collect(Collectors.toSet());
    }
}
