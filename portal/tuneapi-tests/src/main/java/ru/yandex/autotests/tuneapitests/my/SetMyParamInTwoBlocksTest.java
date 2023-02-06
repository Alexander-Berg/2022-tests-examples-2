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
@Aqua.Test(title = "Set My Param In Two Blocks")
@RunWith(Parameterized.class)
@Features("My")
@Stories("Set My Param In Two Blocks")
public class SetMyParamInTwoBlocksTest {

    private final Client client;
    private final Domain domain;
    private final Authorized authorized;
    private final String block1;
    private final String block2;
    private final List<String> params1;
    private final List<String> params2;
    private final String retpath;
    private final ClientSteps userClient;
    private final MyCookieSteps userMy;

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Block1: \"{1}={3}\"; Block2: \"{2}={4}\"; {5}; Retpath: {6}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (String b1 : MyCookieData.MY_BLOCKS.subList(0, 2)) {
                for (String b2 : MyCookieData.MY_BLOCKS.subList(2, 4)) {
                    for (List<String> p1 : MyCookieData.MY_PARAMS.subList(0, 2)) {
                        for (List<String> p2 : MyCookieData.MY_PARAMS.subList(2, 4)) {
                            for (Authorized auth : Authorized.values()) {
                                data.add(new Object[]{d, b1, b2, p1, p2, auth, null});
                                data.add(new Object[]{d, b1, b2, p1, p2, auth, d.getYandexUrl()});
                            }
                        }
                    }
                }
            }
        }
        return data;
    }

    public SetMyParamInTwoBlocksTest(Domain domain, String block1, String block2, List<String> params1, List<String> params2,
                                     Authorized authorized, String retpath)
    {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.block1 = block1;
        this.block2 = block2;
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
    }

    @Test
    public void setMyParamInTwoBlocks() {
        userMy.setMy(block1, params1, retpath);
        userMy.setMy(block2, params2, retpath);
        userMy.shouldSeeMyCookie(block1, params1);
        userMy.shouldSeeMyCookie(block2, params2);
    }
}
