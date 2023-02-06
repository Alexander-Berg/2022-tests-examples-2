package ru.yandex.metrika.userparams.sharder.services;

import java.util.ArrayList;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;

import static org.assertj.core.api.Assertions.assertThat;


public class SamplingServiceTest {

    private SamplingService samplingService;

    private final long userId = 420L;
    private final long userId1 = 322L;

    private final ParamOwnerKey ownerKey = new ParamOwnerKey(42, userId);

    private final Param param1 = new Param(ownerKey, "path", "value", 0d, 1L);
    private final Param param2 = new Param(ownerKey, "another path", "another value", 1d, 4L);

    private final List<Param> paramList = new ArrayList<>(List.of(param1, param2));

    private final ListParamWrapper params = new ListParamWrapper(paramList, ownerKey.getUserId(), ownerKey.getCounterId(), "");

    @Before
    public void init() {
        samplingService = new SamplingService();
    }

    @Test
    public void emptyFilterTest() {
        samplingService.filter(params);

        assertThat(params.getParams()).hasSize(2);
        assertThat(params.getParams()).containsExactly(param1, param2);
    }

    @Test
    public void fullFilterTest() {
        samplingService.banUserId(userId);

        int quantityOfFilteredParams = samplingService.filter(params);

        assertThat(quantityOfFilteredParams).isEqualTo(2);
        assertThat(params.getParams()).hasSize(0);
    }

    @Test
    public void doesntFilterOtherUserIds() {
        samplingService.banUserId(userId1);

        int quantityOfFilteredParams = samplingService.filter(params);

        assertThat(quantityOfFilteredParams).isEqualTo(0);
        assertThat(params.getParams()).hasSize(2);
    }

}
