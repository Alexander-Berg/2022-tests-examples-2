package ru.yandex.metrika.userparams2d;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams2d.services.SampledCountersService;

import static org.assertj.core.api.Assertions.assertThat;


public class SampledCountersServiceTest {
    private final SampledCountersService sampledCountersService = new SampledCountersService();

    private final int sampledCounterID = 42;
    private final int sample = 10;


    private List<Param> getSampledParams() {
        List<Param> params = new ArrayList<>();

        for (int i = 0; i < 10; ++i) {
            ParamOwnerKey ownerKey = new ParamOwnerKey(sampledCounterID, i);
            params.add(new Param(ownerKey, "myParam", "value" + ownerKey.getUserId(), 0d));
        }
        return params;
    }

    private List<Param> getNotSampledParams() {
        List<Param> params = new ArrayList<>();

        for (int i = 0; i < 10; ++i) {
            ParamOwnerKey ownerKey = new ParamOwnerKey(sampledCounterID + 1, i);
            params.add(new Param(ownerKey, "myParam." + i, "value" + ownerKey.getUserId(), 0d));
        }
        return params;
    }

    @Test
    public void filteringSampledParams() {
        sampledCountersService.addSampled(sampledCounterID, sample);
        List<Param> params = getSampledParams();
        int quantityOfFilteredParams = sampledCountersService.filterSampledCounters(params);

        assertThat(params.size()).isEqualTo(1);
        assertThat(quantityOfFilteredParams).isEqualTo(10);
    }

    @Test
    public void notFilteringNotSampledParams() {
        sampledCountersService.addSampled(sampledCounterID, sample);
        List<Param> params = getNotSampledParams();

        int quantityOfFilteredParams = sampledCountersService.filterSampledCounters(params);

        assertThat(params.size()).isEqualTo(10);
        assertThat(quantityOfFilteredParams).isEqualTo(0);
    }

}
