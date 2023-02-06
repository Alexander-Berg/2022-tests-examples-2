package ru.yandex.quasar.app.navigation

import android.animation.Animator
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.ui.views.navigation.DirectionsState
import ru.yandex.quasar.app.ui.views.navigation.SplitNavViewAnimatorBase
import ru.yandex.quasar.app.ui.views.navigation.SplitNavViewAnimatorVertical
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_DOWN
import ru.yandex.quasar.view.SplitNavDirectionsViewConfig

@RunWith(RobolectricTestRunner::class)
class SplitNavViewAnimatorBaseTest {
    @Test
    fun when_spotterAnimationsAreEnabled_then_animationsAreStarted() {
        // Arrange
        val config: SplitNavDirectionsViewConfig = mock()
        whenever(config.enableSpotterAnimations).thenReturn(true)
        val animator:SplitNavViewAnimatorBase = SplitNavViewAnimatorVertical(mock(), config)
        val animation: Animator = mock()

        // Act
        animator.playAnimations(animation, DirectionsState(DIRECTION_DOWN, DIRECTION_DOWN))

        // Assert
        verify(animation).start()
    }

    @Test
    fun when_spotterAnimationsAreDisabled_then_animationsAreNeverStarted() {
        // Arrange
        val config: SplitNavDirectionsViewConfig = mock()
        whenever(config.enableSpotterAnimations).thenReturn(false)
        val animator:SplitNavViewAnimatorBase = SplitNavViewAnimatorVertical(mock(), config)
        val animation: Animator = mock()

        // Act
        animator.playAnimations(animation, DirectionsState(DIRECTION_DOWN, DIRECTION_DOWN))

        // Assert
        verify(animation, never()).start()
        verify(animation).end()
    }
}
