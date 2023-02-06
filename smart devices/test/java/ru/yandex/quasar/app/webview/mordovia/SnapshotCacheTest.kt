package ru.yandex.quasar.app.webview.mordovia

import android.graphics.Bitmap
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import ru.yandex.quasar.app.configs.ExternalConfigObservable
import ru.yandex.quasar.app.configs.MordoviaHomeScreenConfig
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.app.webview.cache.SnapshotCache

class SnapshotCacheTest {
    private lateinit var snapshotCache: SnapshotCache
    private val configObservable: ExternalConfigObservable = mock()
    private val homeScenario = "homeScenario"

    init {
        val stationConfig: StationConfig = mock()
        val systemConfig: SystemConfig = mock()
        val mordoviaHomeScreenConfig = MordoviaHomeScreenConfig.fromConfig(
            mapOf(
                "url" to "testUrl",
                "scenario" to homeScenario
            )
        )
        val experiments: JSONObject = mock()
        whenever(experiments.has("mordovia_snapshot_mem_cache")).thenReturn(true)
        whenever(experiments.has("mordovia_snapshot_disk_cache")).thenReturn(true)

        whenever(configObservable.current).thenReturn(stationConfig)
        whenever(stationConfig.systemConfig).thenReturn(systemConfig)
        whenever(systemConfig.experiments).thenReturn(experiments)
        whenever(systemConfig.mordoviaHomeScreenConfig).thenReturn(mordoviaHomeScreenConfig)
    }

    @Before
    fun setUp() {
        snapshotCache = SnapshotCache(mock(), configObservable, mock())
    }

    @Test
    fun given_emptyCache_when_acquire_then_returnNull() {
        assertNull(snapshotCache.acquire("TestScenario", false))
    }

    @Test
    fun given_emptyCache_when_acquireAndInvalidate_then_returnNull() {
        assertNull(snapshotCache.acquire("TestScenario", true))
    }

    @Test
    fun given_emptyCache_when_invalidate_then_noException() {
        snapshotCache.invalidate("TestScenario")
    }

    @Test
    fun given_emptyCache_when_invalidateFirstSaved_then_noException() {
        snapshotCache.invalidateFirstSaved("TestScenario", false)
    }

    @Test
    fun given_emptyCache_when_invalidateFirstSavedAndKeepHomeSnapshot_then_noException() {
        snapshotCache.invalidateFirstSaved(homeScenario, true)
    }

    @Test
    fun given_emptyCache_when_save_then_snapshotSaved() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        snapshotCache.save(scenario, snapshot)
        assertEquals(snapshot, snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_snapshotCache_when_AcquireWithoutInvalidate_then_snapshotHadNotBeenDeleted() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        snapshotCache.save(scenario, snapshot)

        snapshotCache.acquire(scenario, false)

        // snapshot hadn't been deleted
        assertEquals(snapshot, snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_snapshotCache_when_AcquireWithInvalidate_then_snapshotHadBeenDeleted() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        snapshotCache.save(scenario, snapshot)

        snapshotCache.acquire(scenario, true)

        // snapshot had been deleted
        assertNull(snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_snapshotCache_when_Invalidate_then_snapshotHadBeenDeleted() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        snapshotCache.save(scenario, snapshot)

        snapshotCache.invalidate(scenario)

        assertNull(snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_snapshotCache_when_invalidateFirstSaved_then_lastSnapshotHadNotChanged() {
        val scenario = "TestScenario"
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        snapshotCache.save(scenario, snapshot1)
        snapshotCache.save(scenario, snapshot2)

        snapshotCache.invalidateFirstSaved(scenario)

        assertEquals(snapshot2, snapshotCache.acquire(scenario, false))

        // make sure first element has been deleted
        snapshotCache.invalidate(scenario)
        assertNull(snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_differentSnapshots_when_acquireOne_then_acquiredCorrectly() {
        val scenario1 = "TestScenario1"
        val scenario2 = "TestScenario2"
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        snapshotCache.save(scenario1, snapshot1)
        snapshotCache.save(scenario2, snapshot2)

        assertEquals(snapshot1, snapshotCache.acquire(scenario1, false))
        assertEquals(snapshot2, snapshotCache.acquire(scenario2, false))
    }

    @Test
    fun given_differentSnapshots_when_invalidateOne_then_otherWasNotChanged() {
        val scenario1 = "TestScenario1"
        val scenario2 = "TestScenario2"
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        snapshotCache.save(scenario1, snapshot1)
        snapshotCache.save(scenario2, snapshot2)

        assertEquals(snapshot1, snapshotCache.acquire(scenario1, true))
        assertEquals(snapshot2, snapshotCache.acquire(scenario2, false))
    }

    @Test
    fun given_blockedAcquiring_when_acquire_then_returnNull() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        snapshotCache.save(scenario, snapshot)
        snapshotCache.cacheAcquiringBlocked = true

        assertNull(snapshotCache.acquire(scenario, false))
    }

    @Test
    fun given_snapshotCache_when_InvalidateAll_then_returnNull() {
        val scenario = "TestScenario"
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        snapshotCache.save(scenario, snapshot1)
        snapshotCache.save(scenario, snapshot2)

        snapshotCache.invalidate(scenario)
        snapshotCache.invalidate(scenario)

        assertNull(snapshotCache.acquire(scenario, false))
    }
}
