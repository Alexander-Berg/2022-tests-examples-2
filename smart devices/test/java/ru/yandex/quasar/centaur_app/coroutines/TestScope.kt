package ru.yandex.quasar.centaur_app.coroutines

import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LifecycleRegistry
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestCoroutineScope
import org.mockito.Mockito.mock
import ru.yandex.quasar.centaur_app.metrica.IMetricaReporter
import ru.yandex.quasar.centaur_app.utils.extensions.repeatOnLifecycleSafe
import kotlin.coroutines.CoroutineContext

class TestScope(
    override val coroutineContext: CoroutineContext
): CentaurCoroutineScope {
    private val scope = TestCoroutineScope(coroutineContext)
    private val lifecycleTest = LifecycleRegistry(mock(LifecycleOwner::class.java)).apply {
        currentState = Lifecycle.State.STARTED
    }

    override fun launch(block: suspend CoroutineScope.() -> Unit): Job {
        return scope.launch {
            block.invoke(this)
        }
    }

    override fun repeatOnLifecycleSafe(
        metrica: IMetricaReporter,
        callPlacePointer: String,
        lifecycleState: Lifecycle.State,
        block: suspend CoroutineScope.() -> Unit
    ) = scope.launch {
        lifecycleTest.repeatOnLifecycleSafe(metrica, callPlacePointer, lifecycleState) {
            launch {
                block.invoke(this)
            }
        }
    }
}
