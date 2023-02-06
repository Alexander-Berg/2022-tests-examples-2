package ru.yandex.metrika.userparams2d;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;

import ru.yandex.metrika.api.constructor.contr.CounterBignessService;
import ru.yandex.metrika.counters.serverstate.CountersServerNanoLayerIdByCounterState;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwner;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.ParamOwners2Dao;
import ru.yandex.metrika.userparams.Params2Dao;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.userparams2d.cache.CacheContainer;
import ru.yandex.metrika.userparams2d.services.LogbrokerService;
import ru.yandex.metrika.userparams2d.services.ParamService;
import ru.yandex.metrika.userparams2d.services.UserParamsYtService;
import ru.yandex.metrika.util.hash.YandexConsistentHash;

import static java.util.Arrays.asList;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.argThat;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class ParamServiceTest {

    private ParamService paramService;
    private UserParamsYtService userParamsYtService;

    private ParamOwnerKey ownerKey = new ParamOwnerKey(42, 420L);
    private Param param = new Param(ownerKey, "path", "value", 0d, 1L);
    private Param paramCopy = new Param(ownerKey, "path", "value", 0d, 1L);
    private Param paramModification = new Param(ownerKey, "path", "modified value", 0d, 1L);
    private final Param paramWithBigVersion = new Param(ownerKey, "path", "value", 0d, 42L);
    private final ParamOwner owner = new ParamOwner(ownerKey, 1, 1L);

    private final ParamOwners2Dao paramOwnersDao = mock(ParamOwners2Dao.class);
    private final Params2Dao paramsDao = mock(Params2Dao.class);
    private final CacheContainer cacheContainer = new CacheContainer();

    private final LogbrokerWriterStub<UserParamLBCHRow> gigaDownstreamStub = new LogbrokerWriterStub<>();
    private final LogbrokerWriterStub<UserParamLBCHRow> nanoDownstreamStub = new LogbrokerWriterStub<>();

    private final CounterBignessService bignessService = mock(CounterBignessService.class);
    private final CountersServerNanoLayerIdByCounterState countersServerNanoLayerIdByCounterState = mock(CountersServerNanoLayerIdByCounterState.class);


    @Before
    public void init() {
        LogbrokerService logbrokerService = new LogbrokerService(gigaDownstreamStub, nanoDownstreamStub, bignessService, countersServerNanoLayerIdByCounterState);
        userParamsYtService = new UserParamsYtService(paramOwnersDao, paramsDao);
        paramService = new ParamService(cacheContainer, logbrokerService, userParamsYtService);

        ownerKey = new ParamOwnerKey(42, 420L);
        param = new Param(ownerKey, "path", "value", 0d, 1L);
        paramCopy = new Param(ownerKey, "path", "value", 0d, 1L);
        paramModification = new Param(ownerKey, "path", "modified value", 0d, 1L);
    }

    private void saveParamsFromCore(List<Param> params) {
        paramService.saveParams(params, UpdateSource.CORE, LocalDateTime.now()).join();
    }

    private void saveParamsFromAPI(List<Param> params) {
        paramService.saveParams(params, UpdateSource.API, LocalDateTime.now()).join();
    }

    private void deleteParams(List<Param> params) {
        paramService.deleteParams(params);
    }


    private void putToParamCache(Param param) {
        cacheContainer.paramCache.put(param.getKey(), param);
    }

    private void putToOwnerCache(ParamOwner owner) {
        cacheContainer.ownerCache.put(owner.getKey(), owner);
    }

    private Collection<ParamOwner> getParamOwnersFromCache() {
        return cacheContainer.getOwnerCache().asMap().values();
    }

    private Collection<Param> getParamsFromCache() {
        return cacheContainer.getParamCache().asMap().values();
    }

    /* Тесты для параметров из движка  */

    @Test
    public void cachedAndUnmodified() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        putToParamCache(param);

        saveParamsFromCore(singletonList(paramCopy));

        verify(paramsDao, never()).selectByKeys(any());
        verify(paramsDao, never()).update(any(), any());
        gigaDownstreamStub.assertHaveNoMessages();
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(param);
    }

    @Test
    public void bigCounterCachedAndModified() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        putToParamCache(param);

        saveParamsFromCore(singletonList(paramModification));

        verify(paramsDao, never()).selectByKeys(any());
        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(paramModification);
    }

    @Test
    public void cachedAndModifiedUpdateVersion() {
        when(bignessService.isBig(paramWithBigVersion.getOwnerKey().getCounterId())).thenReturn(true);
        putToParamCache(paramWithBigVersion);

        saveParamsFromCore(singletonList(paramModification));
        Param expectedParam = new Param(paramModification);
        expectedParam.setVersion(paramWithBigVersion.getVersion() + 1);

        verify(paramsDao, never()).selectByKeys(any());
        verify(paramsDao).update(argThat(new CollectionOf<>(expectedParam)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(expectedParam, LocalDateTime.now(), false, YandexConsistentHash.getShard(expectedParam.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(expectedParam);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(expectedParam.getVersion());
    }

    @Test
    public void notCachedAndModifiedUpdateVersion() {
        when(bignessService.isBig(paramWithBigVersion.getOwnerKey().getCounterId())).thenReturn(true);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(paramWithBigVersion.getKey())))).thenReturn(singletonList(paramWithBigVersion));

        saveParamsFromCore(singletonList(paramModification));
        Param expectedParam = new Param(paramModification);
        expectedParam.setVersion(paramWithBigVersion.getVersion() + 1);

        verify(paramsDao).update(argThat(new CollectionOf<>(expectedParam)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(expectedParam, LocalDateTime.now(), false, YandexConsistentHash.getShard(expectedParam.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(expectedParam);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(expectedParam.getVersion());
    }

    @Test
    public void smallCounterCachedAndModified() {
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(param.getOwnerKey().getCounterId())).thenReturn(42);
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        putToParamCache(param);

        saveParamsFromCore(singletonList(paramModification));

        verify(paramsDao, never()).selectByKeys(any());
        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, 42));
        assertThat(getParamsFromCache()).containsExactly(paramModification);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramModification.getVersion());
    }

    @Test
    public void smallCounterNotCachedAndUnmodified() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey())))).thenReturn(singletonList(param));

        saveParamsFromCore(singletonList(paramCopy));

        verify(paramsDao, never()).update(any(), any());
        gigaDownstreamStub.assertHaveNoMessages();
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(paramCopy);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramCopy.getVersion());
    }

    @Test
    public void smallCounterNotCachedAndModified() {
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(param.getOwnerKey().getCounterId())).thenReturn(42);
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey())))).thenReturn(singletonList(param));

        saveParamsFromCore(singletonList(paramModification));

        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, 42));
        assertThat(getParamsFromCache()).containsExactly(paramModification);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramModification.getVersion());
    }

    @Test
    public void bigCounterNotCachedAndModified() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey())))).thenReturn(singletonList(param));

        saveParamsFromCore(singletonList(paramModification));

        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(paramModification);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramModification.getVersion());
    }


    @Test
    public void bigCounterNotCachedNotInYTAndModified() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey())))).thenReturn(emptyList());

        saveParamsFromCore(singletonList(paramModification));

        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();
        assertThat(getParamsFromCache()).containsExactly(paramModification);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramModification.getVersion());
    }

    @Test
    public void persistsOnlyFirstParamInDbWhenLimitForParamOwnerIsExceededAfterFirst() {
        Param param2 = new Param(ownerKey, "path2", "value2", 0d);

        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        when(bignessService.isBig(param2.getOwnerKey().getCounterId())).thenReturn(true);

        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey(), param2.getKey()))))
                .thenReturn(emptyList());

        owner.setParamQuantity(ParamService.MAX_PARAM_QUANTITY - 1);
        putToOwnerCache(owner);

        saveParamsFromCore(asList(param2, param));


        ArgumentCaptor<Collection<Param>> updateParamsCaptor = ArgumentCaptor
                .forClass((Class<Collection<Param>>) (Class) Collection.class);
        verify(paramsDao).update(updateParamsCaptor.capture(), any());

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), ParamService.MAX_PARAM_QUANTITY);
        verify(paramOwnersDao).updateParamQuantities(argThat(new CollectionOf<>(expectedNewOwner)), any());

        Collection<Param> updatedParams = updateParamsCaptor.getValue();
        assertThat(updatedParams).hasSize(1).isSubsetOf(param, param2);

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param2, LocalDateTime.now(), false, YandexConsistentHash.getShard(param2.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamsFromCache()).containsExactly(param2);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(param2.getVersion());
        assertThat(getParamOwnersFromCache()).containsExactly(expectedNewOwner);
    }

    @Test
    public void cachedOwnerAndModifiedParam() {
        when(bignessService.isBig(paramModification.getOwnerKey().getCounterId())).thenReturn(true);
        putToOwnerCache(owner);
        putToParamCache(param);
        saveParamsFromCore(singletonList(paramModification));

        verify(paramOwnersDao, never()).selectByKeys(any());
        verify(paramOwnersDao, never()).updateParamQuantities(any(), any());
        verify(paramOwnersDao, never()).update(any(), any());
        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamOwnersFromCache()).containsExactly(owner);
    }

    @Test
    public void cachedOwnerAndNewParam() {
        putToOwnerCache(owner);
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(param.getKey().getOwnerKey()))))
                .thenReturn(emptyList());

        saveParamsFromCore(singletonList(param));

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), owner.getParamQuantity() + 1);

        verify(paramOwnersDao).updateParamQuantities(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).update(any(), any());

        assertThat(getParamOwnersFromCache()).containsExactly(expectedNewOwner);
    }

    @Test
    public void notCachedOwnerAndModifiedParam() {
        // Owner только в базе, не в кеше, не меняется
        putToParamCache(param);
        saveParamsFromCore(singletonList(paramModification));

        verify(paramOwnersDao, never()).selectByKeys(any());
        verify(paramOwnersDao, never()).update(any(), any());
        verify(paramOwnersDao, never()).updateParamQuantities(any(), any());
        assertThat(getParamOwnersFromCache()).isEmpty();
    }


    @Test
    public void notCachedOwnerAndNewParam() {
        // Owner только в базе, не в кеше, меняется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(param.getOwnerKey()))))
                .thenReturn(singletonList(owner));

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), owner.getParamQuantity() + 1);
        saveParamsFromCore(singletonList(param));

        verify(paramOwnersDao).updateParamQuantities(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).update(any(), any());

        assertThat(getParamOwnersFromCache()).containsExactly(expectedNewOwner);
    }

    @Test
    public void newOwnerAndNewParam() {
        // Owner отсутствует в базе, создаётся
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(param.getOwnerKey()))))
                .thenReturn(emptyList());

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), 1);
        saveParamsFromCore(singletonList(param));

        verify(paramOwnersDao).update(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).updateParamQuantities(any(), any());

        assertThat(getParamOwnersFromCache()).containsExactly(expectedNewOwner);
    }

    /* Тесты для параметров из API  */

    @Test
    public void modifyCachedParamFromApi() {
        when(bignessService.isBig(paramModification.getOwnerKey().getCounterId())).thenReturn(true);
        // Параметр в кеше, меняется
        putToParamCache(param);

        saveParamsFromAPI(singletonList(paramModification));

        verify(paramsDao, never()).selectByKeys(any());
        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamsFromCache()).containsExactly(paramModification);
        assertThat(getParamsFromCache().stream().map(Param::getVersion).toList()).containsExactly(paramModification.getVersion());
    }

    @Test
    public void notModifyNotCachedParamFromAPI() {
        // Параметр только в базе, не в кеше, не меняется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(singletonList(param));

        saveParamsFromAPI(singletonList(paramCopy));

        verify(paramsDao, never()).update(any(), any());

        gigaDownstreamStub.assertHaveNoMessages();
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamsFromCache()).isEmpty();
    }


    @Test
    public void modifyNotCachedParamWithBigCounterFromAPI() {
        when(bignessService.isBig(paramModification.getOwnerKey().getCounterId())).thenReturn(true);
        // Параметр только в базе, не в кеше, меняется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(singletonList(param));

        saveParamsFromAPI(singletonList(paramModification));

        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamsFromCache()).isEmpty();
    }

    @Test
    public void modifyNotCachedParamWithSmallCounterFromAPI() {
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(paramModification.getOwnerKey().getCounterId())).thenReturn(42);
        when(bignessService.isBig(paramModification.getOwnerKey().getCounterId())).thenReturn(false);
        // Параметр только в базе, не в кеше, меняется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(singletonList(param));

        saveParamsFromAPI(singletonList(paramModification));

        verify(paramsDao).update(argThat(new CollectionOf<>(paramModification)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, 42));

        assertThat(getParamsFromCache()).isEmpty();
    }

    @Test
    public void addNewParamWithBigCounterFromAPI() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        // Параметр добавляется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());

        saveParamsFromAPI(singletonList(param));

        verify(paramsDao).update(argThat(new CollectionOf<>(param)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamsFromCache()).isEmpty();
    }

    @Test
    public void addNewParamWithSmallCounterFromAPI() {
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(param.getOwnerKey().getCounterId())).thenReturn(42);
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        // Параметр добавляется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());

        saveParamsFromAPI(singletonList(param));

        verify(paramsDao).update(argThat(new CollectionOf<>(param)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, 42));

        assertThat(getParamsFromCache()).isEmpty();
    }


    @Test
    public void cachedOwnerAddNewParamFromAPI() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        // Owner в кеше, меняется
        putToOwnerCache(owner);

        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());

        saveParamsFromAPI(singletonList(param));
        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), owner.getParamQuantity() + 1);
        verify(paramOwnersDao).updateParamQuantities(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).update(any(), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamOwnersFromCache()).containsExactly(expectedNewOwner);
    }


    @Test
    public void notCachedOwnerAddNewParamFromAPI() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        // Owner только в базе, не в кеше, меняется
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(param.getOwnerKey()))))
                .thenReturn(singletonList(owner));

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), owner.getParamQuantity() + 1);
        saveParamsFromAPI(singletonList(param));

        verify(paramOwnersDao).updateParamQuantities(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).update(any(), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamOwnersFromCache()).isEmpty();
    }

    @Test
    public void newOwnerAddNewParamFromAPI() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(true);
        // Owner отсутствует в базе, создаётся
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey()))))
                .thenReturn(emptyList());
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(param.getOwnerKey()))))
                .thenReturn(emptyList());

        ParamOwner expectedNewOwner = new ParamOwner(owner.getKey(), 1);
        saveParamsFromAPI(singletonList(param));

        verify(paramOwnersDao).update(argThat(new CollectionOf<>(expectedNewOwner)), any());
        verify(paramOwnersDao, never()).updateParamQuantities(any(), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), false, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveNoMessages();

        assertThat(getParamOwnersFromCache()).isEmpty();
    }

    @Test
    public void persistsTwoParamsWhenOneIsNewAndAnotherIsUpdated() {
        when(bignessService.isBig(paramModification.getOwnerKey().getCounterId())).thenReturn(true);
        ArgumentCaptor<Collection<Param>> paramCaptor = ArgumentCaptor
                .forClass((Class<Collection<Param>>) (Class) Collection.class);

        Param newParam = new Param(new ParamOwnerKey(32, 32), "new_path", "value", 0d, 1L);
        when(paramsDao.selectByKeys(argThat(new CollectionOf<>(param.getKey(), newParam.getKey()))))
                .thenReturn(singletonList(param));
        when(bignessService.isBig(newParam.getOwnerKey().getCounterId())).thenReturn(false);
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(newParam.getOwnerKey().getCounterId())).thenReturn(32);

        saveParamsFromCore(asList(paramModification, newParam));

        verify(paramsDao, atLeastOnce()).update(paramCaptor.capture(), any());

        List<Param> params = new ArrayList<>();
        paramCaptor.getAllValues().stream().flatMap(Collection::stream).forEach(params::add);

        gigaDownstreamStub.assertHaveOnlyMessages(new UserParamLBCHRow(paramModification, LocalDateTime.now(), false, YandexConsistentHash.getShard(paramModification.getOwnerKey().getUserId())),
                new UserParamLBCHRow(newParam, LocalDateTime.now(), false, YandexConsistentHash.getShard(newParam.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(newParam, LocalDateTime.now(), false, 32));


        assertThat(params).containsExactlyInAnyOrder(paramModification, newParam);
    }

    @Test
    public void deleteTest() {
        when(bignessService.isBig(param.getOwnerKey().getCounterId())).thenReturn(false);
        when(countersServerNanoLayerIdByCounterState.getNanoLayerId(param.getOwnerKey().getCounterId())).thenReturn(42);
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(ownerKey)))).thenReturn(singletonList(owner));
        putToParamCache(param);
        ParamOwner expectedOwner = new ParamOwner(ownerKey, owner.getParamQuantity() - 1);

        deleteParams(singletonList(param));

        verify(paramsDao).delete(argThat(new CollectionOf<>(param)));
        verify(paramOwnersDao).selectByKeys(argThat(new CollectionOf<>(ownerKey)));
        verify(paramOwnersDao).update(argThat(new CollectionOf<>(expectedOwner)), any());

        gigaDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), true, YandexConsistentHash.getShard(param.getOwnerKey().getUserId())));
        nanoDownstreamStub.assertHaveExactlyOneMessage(new UserParamLBCHRow(param, LocalDateTime.now(), true, 42));

        assertThat(getParamsFromCache()).isEmpty();
    }
}
