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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Change My Param")
@RunWith(Parameterized.class)
@Features("My")
@Stories("Change My Param")
public class ChangeMyParamTest {

    private final Client client;
    private final Domain domain;
    private final Authorized authorized;
    private final String block;
    private final List<String> params1;
    private final List<String> params2;
    private final String retpath;
    private final ClientSteps userClient;
    private final MyCookieSteps userMy;

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Change: \"{1}={2}\"->\"{1}={3}\"; {4} Retpath: {5}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (String b : MyCookieData.MY_BLOCKS.subList(0, 4)) {
                for (List<String> p1 : MyCookieData.MY_PARAMS) {
                    for (List<String> p2 : MyCookieData.MY_PARAMS) {
                        for (Authorized auth : Authorized.values()) {
                            data.add(new Object[]{d, b, p1, p2, auth, null});
                            data.add(new Object[]{d, b, p1, p2, auth, d.getYandexUrl()});
                        }
                    }
                }
            }
        }
        return data;
    }

    public ChangeMyParamTest(Domain domain, String block, List<String> params1, List<String> params2,
                             Authorized authorized, String retpath)
    {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.block = block;
        this.params1 = params1;
        this.params2 = params2;
        this.authorized = authorized;
        this.retpath = retpath;
        this.userClient = new ClientSteps(client);
        this.userMy = new MyCookieSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
        userMy.setMy(block, params1, retpath);
        userMy.shouldSeeMyCookie(block, params1);
    }

    @Test
    public void changeMyParam() {
        userMy.setMy(block, params2, retpath);
        userMy.shouldSeeMyCookie(block, params2);
    }
}
