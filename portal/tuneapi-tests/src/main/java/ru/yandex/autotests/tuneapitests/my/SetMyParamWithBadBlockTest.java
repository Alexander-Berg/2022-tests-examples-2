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
@Aqua.Test(title = "Set My Param With Bad Blocks")
@RunWith(Parameterized.class)
@Features("My")
@Stories("Set My Param With Bad Blocks")
public class SetMyParamWithBadBlockTest {

    private final Client client;
    private final Domain domain;
    private final Authorized authorized;
    private final String block;
    private final List<String> params;
    private final String retpath;
    private final ClientSteps userClient;
    private final MyCookieSteps userMy;

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Block: \"{1}\"; Param: {2}; {3}; Retpath: {4}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (String b : MyCookieData.BAD_BLOCKS) {
                for (List<String> p : MyCookieData.MY_PARAMS.subList(0, 2)) {
                    for (Authorized auth : Authorized.values()) {
                        data.add(new Object[]{d, b, p, auth, null});
                        data.add(new Object[]{d, b, p, auth, d.getYandexUrl()});
                    }
                }
            }
        }
        return data;
    }

    public SetMyParamWithBadBlockTest(Domain domain, String block, List<String> params, Authorized authorized, String retpath) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.block = block;
        this.params = params;
        this.authorized = authorized;
        this.retpath = retpath;
        this.userClient = new ClientSteps(client);
        this.userMy = new MyCookieSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
    }

    @Test
    public void myParamNotSetWithBadBlock() {
        userMy.setMy(block, params, retpath);
        userMy.shouldNotSeeMyCookieParamSet(block);
    }
}
