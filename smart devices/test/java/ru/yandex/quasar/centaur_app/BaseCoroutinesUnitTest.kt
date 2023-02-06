package ru.yandex.quasar.centaur_app

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.TestCoroutineDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Before
import ru.yandex.quasar.centaur_app.coroutines.CentaurCoroutineScope
import ru.yandex.quasar.centaur_app.coroutines.TestScope

open class BaseCoroutinesUnitTest {
    protected val testDispatcher = TestCoroutineDispatcher()
    protected val coroutineScope: CentaurCoroutineScope = TestScope(testDispatcher)

    @Before
    open fun setup() {
        CentaurApp.isInTestHarness = true
        Dispatchers.setMain(testDispatcher)
    }

    @After
    open fun tearDown() {
        Dispatchers.resetMain()
        testDispatcher.cleanupTestCoroutines()
    }
}
