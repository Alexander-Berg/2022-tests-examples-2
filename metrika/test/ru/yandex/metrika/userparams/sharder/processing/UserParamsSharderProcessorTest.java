package ru.yandex.metrika.userparams.sharder.processing;


import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.lb.read.processing.LbReadProcessingTestUtil;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.sharder.services.SamplingService;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

public class UserParamsSharderProcessorTest {

    private final SamplingService samplingService = mock(SamplingService.class);
    private final LogbrokerWriterStub<UserParamUpdate> updatesDownstreamStub = new LogbrokerWriterStub<>();
    private UserparamsSharderProcessor processor;

    private final ParamOwnerKey ownerKey = new ParamOwnerKey(42, 420L);

    private final Param param1 = new Param(ownerKey, "path", "value", 0d, 1L);
    private final Param param2 = new Param(ownerKey, "another path", "another value", 1d, 4L);

    private final Param emptyParam = new Param(ownerKey, "", "", 0d, 1L);

    private final String CLIENT_USER_ID = "client_user_id";

    private final List<Param> singleParam = List.of(param1, param2);
    private final List<Param> emptyParamList = new ArrayList<>(List.of(emptyParam));
    private final ListParamWrapper wrappedSingleParam = new ListParamWrapper(singleParam, ownerKey.getUserId(), ownerKey.getCounterId(), "");
    private final ListParamWrapper wrappedSingleParamWithClientUserId = new ListParamWrapper(singleParam, ownerKey.getUserId(), ownerKey.getCounterId(), CLIENT_USER_ID);
    private final ListParamWrapper emptyParamWithClientUserId = new ListParamWrapper(emptyParamList, ownerKey.getUserId(), ownerKey.getCounterId(), CLIENT_USER_ID);

    @Before
    public void init() {
        processor = new UserparamsSharderProcessor(updatesDownstreamStub, samplingService);
        processor.afterPropertiesSet();
        updatesDownstreamStub.clear();
    }

    @Test
    public void simpleTest() {
        processor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(wrappedSingleParam))).join();

        updatesDownstreamStub.assertHaveExactlyOneMessage(new UserParamUpdate(wrappedSingleParam, UserParamAction.UPDATE));
    }

    @Test
    public void filterTest() {
        processor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(wrappedSingleParam))).join();

        verify(samplingService).filter(wrappedSingleParam);
    }

    @Test
    public void clientUserIdTest() {
        processor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(wrappedSingleParamWithClientUserId))).join();

        verify(samplingService).filter(wrappedSingleParamWithClientUserId);
    }

    @Test
    public void emptyParamWithClientUserIdTest() {
        processor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(emptyParamWithClientUserId))).join();

        verify(samplingService).filter(emptyParamWithClientUserId);
    }

}
