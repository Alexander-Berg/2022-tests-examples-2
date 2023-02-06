package ru.yandex.metrika.internalapid.api.management.client.controllercontext;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.internalapid.core.CoreController;
import ru.yandex.metrika.rbac.metrika.ManagerRolesProvider;
import ru.yandex.metrika.rbac.metrika.MetrikaManagerRolesProvider;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class CoreControllerContext {

    @Autowired
    private MySqlJdbcTemplate rbacTemplate;

    @Bean
    public CoreController coreController() {
        AuthUtils mockAuthUtils = mock(AuthUtils.class);
        when(mockAuthUtils.hasInternalRoles(List.of(10L))).thenReturn(Map.of(10L, true));
        when(mockAuthUtils.hasInternalRoles(List.of(13L))).thenReturn(Map.of(13L, false));

        return new CoreController(mockAuthUtils);
    }

    @Bean
    public ManagerRolesProvider managerRolesProvider() {
        return new MetrikaManagerRolesProvider(rbacTemplate);
    }

}
