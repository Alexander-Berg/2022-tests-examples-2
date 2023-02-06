package ru.yandex.metrika.spring.quota.redis;

import java.io.IOException;

import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.auth.RoleUtils;
import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.dbclients.redis.RedisSourceList;
import ru.yandex.metrika.spring.quota.QuotaException;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class QuotaServiceImplTest {

    @Ignore
    @Test
    public void checkQuota() throws IOException {
        Log4jSetup.basicSetup();
        final QuotaConfig quotaConfig = new QuotaConfig();
        quotaConfig.setJsonConfig("{\n" +
                "  \"quota_config\": {\n" +
                "    \"ALL\": {\n" +
                "      \"create_geo\": [\n" +
                "        {\n" +
                "          \"window_size_millis\": 60000,\n" +
                "          \"limit\": 10\n" +
                "        },\n" +
                "        {\n" +
                "          \"window_size_millis\": 3600000,\n" +
                "          \"limit\": 100\n" +
                "        },\n" +
                "        {\n" +
                "          \"window_size_millis\": 86400000,\n" +
                "          \"limit\": 500\n" +
                "        }\n" +
                "      ],\n" +
                "      \"read\": [\n" +
                "        {\n" +
                "          \"window_size_millis\": 86400000,\n" +
                "          \"limit\": 5000\n" +
                "        }\n" +
                "      ]\n" +
                "    }\n" +
                "  }\n" +
                "}");
        final RedisSourceList sources = new RedisSourceList();
        sources.getSource().get(0).setHost("sas-3ny8p43rteh7a8rl.db.yandex.net");
        sources.getSource().get(0).setPort(26379);
        sources.setPassword("");
        sources.setMasterId("mtredis-test");

        final RedisConnector connector = new RedisConnector(sources);
        connector.init();

        AuthUtils authUtils = mock(AuthUtils.class);
        RoleUtils roleUtils = mock(RoleUtils.class);
        when(roleUtils.isManager(any(MetrikaUserDetails.class))).thenReturn(false);

        QuotaServiceImpl quotaService = new QuotaServiceImpl(quotaConfig, QuotaService.UID_EXTRACTOR, connector, "audience-quota", (p) -> new QuotaException("quota exceeded"), roleUtils, authUtils);

        for (int i = 0; i < 10; i++) {
            System.out.println("i=" + i);
            quotaService.checkQuota("42", "create_geo");
        }
    }
}
