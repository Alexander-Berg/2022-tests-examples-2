package ru.yandex.metrika.cdp.api.tests.medium.access;

import java.util.Collection;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.test.context.TestSecurityContextHolder;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.RequestBuilder;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.cdp.api.spring.CdpApiTestConfig;
import ru.yandex.metrika.cdp.api.tests.medium.AbstractCdpApiTest;

import static org.assertj.core.util.Arrays.array;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.cdp.api.users.TestUsers.READ_ONLY_USER_NAME;
import static ru.yandex.metrika.cdp.api.users.TestUsers.SIMPLE_USER_NAME;
import static ru.yandex.metrika.cdp.api.users.TestUsers.YA_MANAGER_NAME;
import static ru.yandex.metrika.cdp.api.users.TestUsers.usersByUsername;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = CdpApiTestConfig.class)
@WebAppConfiguration
public class CdpApiAccessTest extends AbstractCdpApiTest {
    private static final String VIEW_PATH_TEMPLATE = "/cdp/api/v1/test/counter/{counterId}/access/view";
    private static final String SAVE_PATH_TEMPLATE = "/cdp/api/v1/test/counter/{counterId}/access/save";

    private static final Function<Integer, RequestBuilder> viewMethod = (counterId) -> get(VIEW_PATH_TEMPLATE, counterId);
    private static final Function<Integer, RequestBuilder> saveMethod = (counterId) -> get(SAVE_PATH_TEMPLATE, counterId);
    private static final ResultMatcher ok = status().isOk();
    private static final ResultMatcher forbidden = status().isForbidden();

    private int counterId;

    @Parameter(value = 0)
    public MetrikaUserDetails user;

    @Parameter(value = 1)
    public Function<Integer, RequestBuilder> requestBuilderFunction;

    @Parameter(value = 2)
    public ResultMatcher expectedStatus;

    @Parameter(value = 3)
    public String name; // just for name

    @Parameterized.Parameters(name = "{index}: {3}")
    public static Collection<Object[]> parameters() {
        return
                List.of(
                        array(usersByUsername.get(READ_ONLY_USER_NAME), viewMethod, ok),
                        array(usersByUsername.get(READ_ONLY_USER_NAME), saveMethod, forbidden),

                        array(usersByUsername.get(SIMPLE_USER_NAME), viewMethod, ok),
                        array(usersByUsername.get(SIMPLE_USER_NAME), saveMethod, ok),

                        array(usersByUsername.get(YA_MANAGER_NAME), viewMethod, ok),
                        array(usersByUsername.get(YA_MANAGER_NAME), saveMethod, ok)
                ).stream().map(arr -> array(
                        arr[0], arr[1], arr[2],
                        ((MetrikaUserDetails) arr[0]).getUsername() + ", "
                                + (arr[1].equals(viewMethod) ? "view" : "save") + " method, "
                                + (arr[2].equals(ok) ? "ok" : "forbidden") + " expected"
                )).collect(Collectors.toList());
    }

    @Before
    @Override
    public void setUp() throws Exception {
        super.setUp();
        Authentication authentication = new UsernamePasswordAuthenticationToken(user, user.getPassword(), user.getAuthorities());
        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(authentication);
        TestSecurityContextHolder.setContext(context);
        // preparing counter_id
        counterId = createCounter();
    }

    @After
    public void tearDown() {
        SecurityContextHolder.clearContext();
        TestSecurityContextHolder.clearContext();
    }

    @Test
    public void test() throws Exception {
        mockMvc.perform(requestBuilderFunction.apply(counterId)).andExpect(expectedStatus);
    }

}
