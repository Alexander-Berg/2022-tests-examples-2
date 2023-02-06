package ru.yandex.autotests.tuneapitests.my;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.tuneapitests.steps.ClientSteps;
import ru.yandex.autotests.tuneapitests.steps.MyCookieSteps;
import ru.yandex.autotests.tuneapitests.utils.Authorized;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assume.assumeTrue;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Set My Param Json")
@RunWith(Parameterized.class)
@Features("My")
@Stories("Set My Param Json")
public class SetMyParamJsonTest {

    private final Client client;
    private final Domain domain;
    private final Authorized authorized;
    private final String block;
    private final List<String> params;
    private final ClientSteps userClient;
    private final MyCookieSteps userMy;

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Block: \"{1}\"; Param: {2}; {3}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (String b : MyCookieData.MY_BLOCKS) {
                for (List<String> p : MyCookieData.MY_PARAMS) {
                    for (Authorized auth : Authorized.values()) {
                        data.add(new Object[]{d, b, p, auth});
                    }
                }
            }
        }
        return data;
    }

    public SetMyParamJsonTest(Domain domain, String block, List<String> params, Authorized authorized) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.block = block;
        this.params = params;
        this.authorized = authorized;
        this.userClient = new ClientSteps(client);
        this.userMy = new MyCookieSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
    }

    @Test
    @Stories("Set My Param Json")
    public void setMyParamJson() {
        assumeTrue("Domain is invalid", domain.isDomainValidForJsonRequest());
        TuneResponse response = userMy.setMyJson(block, params, "1");
        userClient.shouldSeeOkTuneResponse(response);
        userMy.shouldSeeMyCookie(block, params);
    }

    @Test
    @Stories("Error My Param Json With Invalid Domain")
    public void errorMyParamJsonInvalidDomain() {
        assumeTrue("Domain is valid", !domain.isDomainValidForJsonRequest());
        TuneResponse response = userMy.setMyJson(block, params, "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userMy.shouldNotSeeMyCookieParamSet(block);
    }

    @Test
    @Stories("Error My Param Json With No sk")
    public void errorMyParamJsonWithoutSk() {
        TuneResponse response = userMy.setMyJsonWithoutSk(block, params, "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userMy.shouldNotSeeMyCookieParamSet(block);
    }

    @Test
    @Stories("Set My Param Json On Tune Internal")
    public void setMyParamOnTuneInternal() {
        TuneResponse response = userMy.setMyJsonOnTuneInternal(block, params, null);
        userClient.shouldSeeOkTuneResponse(response);
        userMy.shouldSeeMyCookie(block, params);
    }
}
