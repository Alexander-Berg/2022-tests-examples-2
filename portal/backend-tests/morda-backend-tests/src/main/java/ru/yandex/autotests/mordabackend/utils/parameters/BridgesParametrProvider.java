package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.bridges.BridgeInfo;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
public class BridgesParametrProvider implements ParameterProvider {

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {
        List<BridgeInfo> itemsList = new ArrayList<>();
        itemsList.addAll(cleanvars.getBridges().get0());
        itemsList.addAll(cleanvars.getBridges().get1());
        List<Object[]> data = new ArrayList<>();
        for (BridgeInfo bridgeInfo : itemsList) {
            data.add(new Object[]{bridgeInfo.getBridgeId(), bridgeInfo});
        }
        return data;
    }
}
