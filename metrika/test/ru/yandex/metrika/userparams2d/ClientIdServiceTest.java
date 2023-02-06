package ru.yandex.metrika.userparams2d;

import java.util.Collection;
import java.util.List;

import javax.annotation.Nonnull;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.userparams.ParamOwner;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.ParamOwners2Dao;
import ru.yandex.metrika.userparams2d.cache.CacheContainer;
import ru.yandex.metrika.userparams2d.services.ClientIdService;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.Assert.assertNotEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.argThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class ClientIdServiceTest {

    private ClientIdService service;
    private final ParamOwnerKey ownerKey = new ParamOwnerKey(42, 420L);
    private final ParamOwner owner = new ParamOwner(ownerKey, "clientUserId", 1);
    private final ParamOwner ownerCopy = new ParamOwner(new ParamOwnerKey(ownerKey), "clientUserId", 0);
    private final ParamOwner ownerModification = new ParamOwner(new ParamOwnerKey(ownerKey), "clientUserId modified", 0);
    private final ParamOwners2Dao paramOwnersDao = mock(ParamOwners2Dao.class);
    private final CacheContainer cacheContainer = new CacheContainer();

    @Before
    public void init() {
        service = new ClientIdService(paramOwnersDao, cacheContainer);
    }

    private void saveClientIds(List<ParamOwner> owners) {
        service.saveClientIds(owners);
    }

    private void putToOwnerCache(ParamOwner owner) {
        cacheContainer.ownerCache.put(owner.getKey(), owner);
    }

    @Test
    public void doesNotPersistNorLookupsOwnerInDbWhenOwnerCachedAndUnmodified() {
        putToOwnerCache(owner);
        saveClientIds(singletonList(ownerCopy));
        verify(paramOwnersDao, never()).selectByKeys(any());
        verify(paramOwnersDao, never()).update(any(), any());
        verify(paramOwnersDao, never()).updateClientUserIds(any(), any());
        assertThat(getOwnersFromCache()).containsExactly(owner);
    }

    @Nonnull
    private Collection<ParamOwner> getOwnersFromCache() {
        return cacheContainer.getOwnerCache().asMap().values();
    }

    @Test
    public void updatesAndDoesNotLookupOwnerInDbWhenOwnerCachedAndModified() {
        putToOwnerCache(owner);
        assertNotEquals(owner.getParamQuantity(), ownerModification.getParamQuantity());
        saveClientIds(singletonList(ownerModification));
        verify(paramOwnersDao, never()).selectByKeys(any());
        verify(paramOwnersDao, never()).update(any(), any());
        verify(paramOwnersDao).updateClientUserIds(argThat(new CollectionOf<>(ownerModification)), any());
        assertThat(owner.getParamQuantity()).isEqualTo(ownerModification.getParamQuantity());
        assertThat(getOwnersFromCache()).containsExactly(ownerModification);
    }

    @Test
    public void doesNotPersistButLookupsOwnerInDbWhenOwnerNotCachedAndUnmodified() {
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(owner.getKey()))))
                .thenReturn(singletonList(owner));
        saveClientIds(singletonList(ownerCopy));
        verify(paramOwnersDao, never()).update(any(), any());
        verify(paramOwnersDao, never()).updateClientUserIds(any(), any());
        assertThat(getOwnersFromCache()).containsExactly(owner);
    }

    @Test
    public void updatesAndLookupsOwnerInDbWhenOwnerNotCachedButModified() {
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(owner.getKey()))))
                .thenReturn(singletonList(owner));
        assertThat(owner.getParamQuantity()).isNotEqualTo(ownerModification.getParamQuantity());
        saveClientIds(singletonList(ownerModification));
        verify(paramOwnersDao, never()).update(any(), any());
        verify(paramOwnersDao).updateClientUserIds(argThat(new CollectionOf<>(ownerModification)), any());
        assertThat(owner.getParamQuantity()).isEqualTo(ownerModification.getParamQuantity());
        assertThat(getOwnersFromCache()).containsExactly(ownerModification);
    }

    @Test
    public void persistsAndLookupsOwnerInDbWhenNewOwner() {
        when(paramOwnersDao.selectByKeys(argThat(new CollectionOf<>(owner.getKey()))))
                .thenReturn(emptyList());
        saveClientIds(singletonList(owner));
        verify(paramOwnersDao).update(argThat(new CollectionOf<>(owner)), any());
        verify(paramOwnersDao, never()).updateClientUserIds(any(), any());
        assertThat(getOwnersFromCache()).containsExactly(owner);
    }
}
