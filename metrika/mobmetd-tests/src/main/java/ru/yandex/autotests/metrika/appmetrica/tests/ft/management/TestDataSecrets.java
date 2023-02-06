package ru.yandex.autotests.metrika.appmetrica.tests.ft.management;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ru.yandex.autotests.metrika.appmetrica.properties.VaultProperties;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;

import java.util.Map;

public class TestDataSecrets {

    private static final Map<String, String> SECRET_CONTENT =
            VaultClient.loadLastVersion(VaultProperties.getInstance().getUsersSecretId());

    /**
     * Храним секреты как json, иначе сломается проверка протухших токенов
     */
    private static final Gson GSON = new GsonBuilder().create();

    public static String getPassword(String secretKey) {
        Map<String, String> content = GSON.fromJson(SECRET_CONTENT.get(secretKey), new TypeToken<Map<String, String>>() {}.getType());
        return content.get("password");
    }

    public static String getYcEditorPrivateKey() {
        Map<String, String> serviceAccountSecret = GSON.fromJson(
                SECRET_CONTENT.get("YC_EDITOR_KEY"), new TypeToken<Map<String, String>>() {}.getType()
        );
        return serviceAccountSecret.get("private_key");
    }

    public static String getYcViewerPrivateKey() {
        Map<String, String> serviceAccountSecret = GSON.fromJson(
                SECRET_CONTENT.get("YC_VIEWER_KEY"), new TypeToken<Map<String, String>>() {}.getType()
        );
        return serviceAccountSecret.get("private_key");
    }
}
