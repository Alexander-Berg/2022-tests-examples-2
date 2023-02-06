package ru.yandex.metrika.internalapid.api.management.client;

import java.util.Collections;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers;
import org.springframework.security.web.FilterChainProxy;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.internalapid.api.config.InternalapiConfiguration;

@ContextConfiguration(classes = {InternalapiConfiguration.class})
@WebAppConfiguration
public class BaseIntapiTest {

    @Autowired
    @Qualifier("convMainTemplate")
    protected MySqlJdbcTemplate convMain;

    @Autowired
    @Qualifier("dictsTemplate")
    protected MySqlJdbcTemplate dicts;

    @Autowired
    protected WebApplicationContext wac;

    @Autowired
    protected FilterChainProxy springSecurityFilterChain;

    protected MockMvc mockMvc;

    protected MetrikaUserDetails getUserByUid(long uid) {
        var user = AuthUtils.buildSimpleUserDetails(uid, "127.0.01");
        AuthUtils.setUserDetails(user);
        return user;
    }

    protected MetrikaUserDetails getManagerUserByUid(long uid) {
        var user = AuthUtils.buildSimpleUserDetails(uid, "127.0.01");
        user.setRoleNames(Collections.singleton("manager"), 1);
        AuthUtils.setUserDetails(user);
        return user;
    }

    protected void mockMvcBaseSetup() {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .apply(SecurityMockMvcConfigurers.springSecurity(springSecurityFilterChain))
                .build();
    }

    protected void createCounter(int counterId, long ownerUid) {
        convMain.update(
                "INSERT IGNORE INTO counters " +
                        "(`counter_id`," +
                        "`owner`," +
                        "`name`," +
                        "create_time," +
                        "external_class," +
                        "external_cid," +
                        "email," +
                        "LayerID," +
                        "informer_color," +
                        "informer_indicators) " +
                        "VALUES (?, ?, ?, NOW(),?,?,?,?,?,?)",
                counterId,
                ownerUid,
                "test",
                0,
                0,
                "test email",
                1,
                "test informer color",
                "test informer indicators"
        );
    }


}
