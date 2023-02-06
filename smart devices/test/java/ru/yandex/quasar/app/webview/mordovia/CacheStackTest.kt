package ru.yandex.quasar.app.webview.mordovia

import android.graphics.Bitmap
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import ru.yandex.quasar.app.webview.cache.MemoryCacheStack

class CacheStackTest {
    private lateinit var memoryCacheStack: MemoryCacheStack

    @Before
    fun setUp() {
        memoryCacheStack = MemoryCacheStack()
    }

    @Test
    fun given_emptyCacheStack_when_last_then_returnNull() {
        assertNull(memoryCacheStack.last("TestScenario"))
    }

    @Test
    fun given_emptyCacheStack_when_first_then_returnNull() {
        assertNull(memoryCacheStack.first("TestScenario"))
    }

    @Test
    fun given_nonEmptyCacheStack_when_last_then_returnTheLatestSnapshot() {
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot1)
        memoryCacheStack.push(scenario, snapshot2)

        assertEquals(snapshot2, memoryCacheStack.last(scenario))
    }

    @Test
    fun given_nonEmptyCacheStack_when_first_then_returnTheOldestSnapshot() {
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot1)
        memoryCacheStack.push(scenario, snapshot2)

        assertEquals(snapshot1, memoryCacheStack.first(scenario))
    }

    @Test
    fun given_emptyCacheStack_when_dropLast_then_nothingChanged() {
        memoryCacheStack.dropLast("TestScenario")
    }

    @Test
    fun given_emptyCacheStack_when_dropFirst_then_nothingChanged() {
        memoryCacheStack.dropFirst("TestScenario")
    }

    @Test
    fun given_emptyCacheStack_when_dropSecond_then_nothingChanged() {
        memoryCacheStack.dropSecond("TestScenario")
    }

    @Test
    fun given_emptyCacheStack_when_push_then_snapshotSaved() {
        val snapshot: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot)
        assertEquals(snapshot, memoryCacheStack.last(scenario))
    }

    @Test
    fun given_nonEmptyCacheStack_when_dropLast_then_lastSnapshotDropped() {
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot1)
        memoryCacheStack.push(scenario, snapshot2)

        memoryCacheStack.dropLast(scenario)

        assertEquals(snapshot1, memoryCacheStack.last(scenario))
    }

    @Test
    fun given_nonEmptyCacheStack_when_dropFirst_then_firstSnapshotDropped() {
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot1)
        memoryCacheStack.push(scenario, snapshot2)

        memoryCacheStack.dropFirst(scenario)

        assertEquals(snapshot2, memoryCacheStack.first(scenario))
    }

    @Test
    fun given_nonEmptyCacheStack_when_dropSecond_then_secondSnapshotDropped() {
        val snapshot1: Bitmap = mock()
        val snapshot2: Bitmap = mock()
        val snapshot3: Bitmap = mock()
        val scenario = "TestScenario"
        memoryCacheStack.push(scenario, snapshot1)
        memoryCacheStack.push(scenario, snapshot2)
        memoryCacheStack.push(scenario, snapshot3)

        memoryCacheStack.dropSecond(scenario)

        // If second element had been dropped, first and last must remain untouched
        assertEquals(snapshot1, memoryCacheStack.first(scenario))
        assertEquals(snapshot3, memoryCacheStack.last(scenario))

        // make sure second element had been dropped
        memoryCacheStack.dropFirst(scenario)
        assertEquals(snapshot3, memoryCacheStack.first(scenario))
    }

    @Test
    fun given_nonEmptyCacheStack_when_dropLastWhileNotEmpty_then_droppedWithoutException() {
        val scenario = "TestScenario"
        val snapshotsCount = 5
        val snapshots = mutableListOf<Bitmap>()
        for (i in 0..snapshotsCount) {
            val snapshot: Bitmap = mock()
            snapshots.add(snapshot)
            memoryCacheStack.push(scenario, snapshot)
        }

        for (i in 0..snapshotsCount) {
            memoryCacheStack.dropLast(scenario)
        }

        // make sure stack is empty and reading from it doesn't generate exception
        assertNull(memoryCacheStack.last(scenario))
        memoryCacheStack.dropLast(scenario)
    }

    @Test
    fun given_nonEmptyCacheStack_when_dropFirstWhileNotEmpty_then_droppedWithoutException() {
        val scenario = "TestScenario"
        val snapshotsCount = 5
        val snapshots = mutableListOf<Bitmap>()
        for (i in 0..snapshotsCount) {
            val snapshot: Bitmap = mock()
            snapshots.add(snapshot)
            memoryCacheStack.push(scenario, snapshot)
        }

        for (i in 0..snapshotsCount) {
            memoryCacheStack.dropFirst(scenario)
        }

        // make sure stack is empty and reading from it doesn't generate exception
        assertNull(memoryCacheStack.first(scenario))
        memoryCacheStack.dropFirst(scenario)
    }

    @Test
    fun given_cacheStackWithOneElement_when_dropSecond_then_nothingDropped() {
        val scenario = "TestScenario"
        val snapshot: Bitmap = mock()
        memoryCacheStack.push(scenario, snapshot)

        memoryCacheStack.dropSecond(scenario)

        assertEquals(snapshot, memoryCacheStack.first(scenario))
    }

    @Test
    fun given_differentScenarios_when_dropLastAtOneScenario_otherScenariosRemainUntouched() {
        val scenario1 = "TestScenario1"
        val scenario2 = "TestScenario2"
        val scenario3 = "TestScenario3"
        val scenarioSnapshots = mapOf<String, List<Bitmap>>(
            scenario1 to listOf(mock(), mock()),
            scenario2 to listOf(mock(), mock()),
            scenario3 to listOf(mock(), mock())
        )

        for (scenario in scenarioSnapshots) {
            for (snapshot in scenario.value) {
                memoryCacheStack.push(scenario.key, snapshot)
            }
        }

        memoryCacheStack.dropLast(scenario1)

        assertEquals(scenarioSnapshots.getValue(scenario1)[0], memoryCacheStack.first(scenario1))
        assertEquals(scenarioSnapshots.getValue(scenario1)[0], memoryCacheStack.last(scenario1))

        assertEquals(scenarioSnapshots.getValue(scenario2)[0], memoryCacheStack.first(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario2)[1], memoryCacheStack.last(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario3)[0], memoryCacheStack.first(scenario3))
        assertEquals(scenarioSnapshots.getValue(scenario3)[1], memoryCacheStack.last(scenario3))
    }

    @Test
    fun given_differentScenarios_when_dropFirstAtOneScenario_otherScenariosRemainUntouched() {
        val scenario1 = "TestScenario1"
        val scenario2 = "TestScenario2"
        val scenario3 = "TestScenario3"
        val scenarioSnapshots = mapOf<String, List<Bitmap>>(
            scenario1 to listOf(mock(), mock()),
            scenario2 to listOf(mock(), mock()),
            scenario3 to listOf(mock(), mock())
        )

        for (scenario in scenarioSnapshots) {
            for (snapshot in scenario.value) {
                memoryCacheStack.push(scenario.key, snapshot)
            }
        }

        memoryCacheStack.dropFirst(scenario1)

        assertEquals(scenarioSnapshots.getValue(scenario1)[1], memoryCacheStack.first(scenario1))
        assertEquals(scenarioSnapshots.getValue(scenario1)[1], memoryCacheStack.last(scenario1))

        assertEquals(scenarioSnapshots.getValue(scenario2)[0], memoryCacheStack.first(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario2)[1], memoryCacheStack.last(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario3)[0], memoryCacheStack.first(scenario3))
        assertEquals(scenarioSnapshots.getValue(scenario3)[1], memoryCacheStack.last(scenario3))
    }

    @Test
    fun given_differentScenarios_when_dropSecondAtOneScenario_otherScenariosRemainUntouched() {
        val scenario1 = "TestScenario1"
        val scenario2 = "TestScenario2"
        val scenario3 = "TestScenario3"
        val scenarioSnapshots = mapOf<String, List<Bitmap>>(
            scenario1 to listOf(mock(), mock()),
            scenario2 to listOf(mock(), mock()),
            scenario3 to listOf(mock(), mock())
        )

        for (scenario in scenarioSnapshots) {
            for (snapshot in scenario.value) {
                memoryCacheStack.push(scenario.key, snapshot)
            }
        }

        memoryCacheStack.dropSecond(scenario1)

        assertEquals(scenarioSnapshots.getValue(scenario1)[0], memoryCacheStack.first(scenario1))
        assertEquals(scenarioSnapshots.getValue(scenario1)[0], memoryCacheStack.last(scenario1))

        assertEquals(scenarioSnapshots.getValue(scenario2)[0], memoryCacheStack.first(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario2)[1], memoryCacheStack.last(scenario2))
        assertEquals(scenarioSnapshots.getValue(scenario3)[0], memoryCacheStack.first(scenario3))
        assertEquals(scenarioSnapshots.getValue(scenario3)[1], memoryCacheStack.last(scenario3))
    }
}
