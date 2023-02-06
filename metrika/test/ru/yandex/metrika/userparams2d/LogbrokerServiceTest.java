package ru.yandex.metrika.userparams2d;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.contr.CounterBignessService;
import ru.yandex.metrika.counters.serverstate.CountersServerNanoLayerIdByCounterState;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.userparams2d.services.LogbrokerService;
import ru.yandex.metrika.util.collections.Lists2;
import ru.yandex.metrika.util.hash.YandexConsistentHash;

import static org.mockito.Matchers.anyInt;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class LogbrokerServiceTest {
    private LogbrokerService logbrokerService;

    private final int nanoShardID = 21;

    private final LogbrokerWriterStub<UserParamLBCHRow> gigaDownstreamStub = new LogbrokerWriterStub<>();
    private final LogbrokerWriterStub<UserParamLBCHRow> nanoDownstreamStub = new LogbrokerWriterStub<>();

    private final CounterBignessService bignessService = mock(CounterBignessService.class);
    private final CountersServerNanoLayerIdByCounterState countersServerNanoLayerIdByCounterState = mock(CountersServerNanoLayerIdByCounterState.class);


    private List<Param> getParams(int counterId) {
        List<Param> params = new ArrayList<>();

        for (int i = 0; i < 10; ++i) {
            ParamOwnerKey ownerKey = new ParamOwnerKey(counterId, i);
            params.add(new Param(ownerKey, "myParam", "value" + ownerKey.getUserId(), 0d));
        }
        return params;
    }

    @Before
    public void init() {
        logbrokerService = new LogbrokerService(gigaDownstreamStub, nanoDownstreamStub, bignessService, countersServerNanoLayerIdByCounterState);
    }


    @Test
    public void correctlyWritesMessagesWithBigCounters() {
        int gigaCounterID = 42;

        when(bignessService.isBig(gigaCounterID)).thenReturn(true);
        var params = getParams(gigaCounterID);
        logbrokerService.saveParams(params);

        verify(countersServerNanoLayerIdByCounterState, never()).getNanoLayerId(anyInt());

        gigaDownstreamStub.assertHaveOnlyMessages(paramsToGigaLBRows(params));
        nanoDownstreamStub.assertHaveNoMessages();
    }

    @Test
    public void correctlyWritesMessagesWithSmallCounters() {
        int gigaCounterID = 42;
        when(bignessService.isBig(gigaCounterID)).thenReturn(false);
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(gigaCounterID)).thenReturn(nanoShardID);

        var params = getParams(gigaCounterID);
        logbrokerService.saveParams(params);

        gigaDownstreamStub.assertHaveOnlyMessages(paramsToGigaLBRows(params));
        nanoDownstreamStub.assertHaveOnlyMessages(paramsToNanoLBRows(params));
    }

    @Test
    public void correctlyWritesMessagesWithDifferentCounters() {
        int gigaCounterID = 42;
        int nanoCounterID = 32;

        when(bignessService.isBig(gigaCounterID)).thenReturn(true);
        when(bignessService.isBig(nanoCounterID)).thenReturn(false);

        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(nanoCounterID)).thenReturn(nanoShardID);

        var bigParams = getParams(gigaCounterID);
        var smallParams = getParams(nanoCounterID);

        var paramsAll = Lists2.concat(bigParams, smallParams);

        logbrokerService.saveParams(paramsAll);

        gigaDownstreamStub.assertHaveOnlyMessages(paramsToGigaLBRows(paramsAll));
        nanoDownstreamStub.assertHaveOnlyMessages(paramsToNanoLBRows(smallParams));
    }

    private List<UserParamLBCHRow> paramsToGigaLBRows(List<Param> params) {
        return params.stream()
                .map(param -> new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())))
                .collect(Collectors.toList());
    }

    private List<UserParamLBCHRow> paramsToNanoLBRows(List<Param> params) {
        return params.stream()
                .map(param -> new UserParamLBCHRow(param, LocalDateTime.now(), false, nanoShardID))
                .collect(Collectors.toList());
    }
}
