package ru.yandex.quasar.app.navigation

import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.ui.views.navigation.DirectionsState
import ru.yandex.quasar.app.ui.views.navigation.SplitNavTextSwitcher
import ru.yandex.quasar.app.ui.views.navigation.SplitNavViewAnimatorBase
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_DOWN
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_LEFT
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_RIGHT
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_UP

@RunWith(RobolectricTestRunner::class)
class SplitNavTextSwitcherTest{
    @Test
    fun when_startAndStop_then_animatorContinuesAnimationFromPreviousState() {
        // Arrange
        val animator: SplitNavViewAnimatorBase = mock()
        val subject = SplitNavTextSwitcher(mock(), animator)

        subject.start()
        val oldDirections = DirectionsState(DIRECTION_RIGHT.or(DIRECTION_DOWN), DIRECTION_LEFT.or(DIRECTION_RIGHT).or(DIRECTION_DOWN))
        val newDirections = DirectionsState(DIRECTION_LEFT.or(DIRECTION_DOWN), DIRECTION_LEFT.or(DIRECTION_RIGHT).or(DIRECTION_DOWN))

        subject.restart(oldDirections.available)
        subject.manualSwitch(oldDirections.direction)

        reset(animator)

        // Act
        subject.stop()
        subject.manualSwitch(newDirections.direction)
        subject.start()

        // Assert
        verify(animator).switch(newDirections, oldDirections)
    }

    @Test
    fun when_periodicUpdateOccursForTheFirstTime_then_directionIsNotRotated() {
        // Arrange
        val animator: SplitNavViewAnimatorBase = mock()
        val subject = SplitNavTextSwitcher(mock(), animator)

        subject.start()
        val directions = DirectionsState(DIRECTION_RIGHT.or(DIRECTION_UP), DIRECTION_LEFT.or(DIRECTION_RIGHT).or(DIRECTION_DOWN).or(DIRECTION_UP))
        subject.directions = directions.copy()

        // Act
        subject.handleMessage(mock())

        // Assert
        verify(animator).switch(directions, DirectionsState(0, 0))
    }

    @Test
    fun when_periodicUpdateOccursForTheSecondTime_then_directionIsRotated() {
        // Arrange
        val animator: SplitNavViewAnimatorBase = mock()
        val subject = SplitNavTextSwitcher(mock(), animator)

        subject.start()
        val directions = DirectionsState(DIRECTION_RIGHT.or(DIRECTION_UP), DIRECTION_LEFT.or(DIRECTION_RIGHT).or(DIRECTION_DOWN).or(DIRECTION_UP))
        subject.directions = directions.copy()

        // Act
        subject.handleMessage(mock())
        reset(animator)
        subject.handleMessage(mock())

        //Assert
        val rotated = DirectionsState(DIRECTION_LEFT.or(DIRECTION_DOWN), DIRECTION_LEFT.or(DIRECTION_RIGHT).or(DIRECTION_DOWN).or(DIRECTION_UP))
        verify(animator).switch(rotated, directions)
    }
}
