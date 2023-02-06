package ru.yandex.quasar.app.navigation

import android.content.Context
import android.content.SharedPreferences
import android.view.View
import android.view.animation.Animation
import android.view.animation.AnimationUtils
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.powermock.core.classloader.annotations.PrepareForTest
import org.powermock.modules.junit4.PowerMockRunner
import ru.yandex.quasar.app.ui.views.navigation.DownArrowJumpAnimator

@RunWith(PowerMockRunner::class)
@PrepareForTest(AnimationUtils::class)
class DownArrowJumpAnimatorTest {

    class TestParams(
        val enabled: Boolean,
        val navigationWasUsed: Boolean,
        val persistJumpState: Boolean,
        val shouldJump: Boolean
    )

    @Test
    @PrepareForTest(AnimationUtils::class)
    fun given_differentInputValues_when_start_then_jumpsAccordingly() {

        val paramsList = listOf(
            TestParams(true, true, true, false),
            TestParams(true, true, false, true),
            TestParams(true, false, true, true),
            TestParams(true, false, false, true),
            TestParams(false, true, true, false),
            TestParams(false, true, false, false),
            TestParams(false, false, true, false),
            TestParams(false, false, false, false)
        )

        for(testParams in paramsList) {
            // Arrange
            val context: Context = mock()
            val sharedPrefs: SharedPreferences = mock()
            whenever(sharedPrefs.getBoolean(any(), any())).thenReturn(testParams.navigationWasUsed)

            val jumpDownAnimation: Animation = mock()

            whenever(context.getSharedPreferences(any(), any())).thenReturn(sharedPrefs)
            val animator = DownArrowJumpAnimator(context, testParams.enabled, testParams.persistJumpState, jumpDownAnimation)

            // Act
            val button: View = mock()
            animator.start(button)

            // Assert
            if(testParams.shouldJump) {
                verify(button).startAnimation(jumpDownAnimation)
            } else {
                verify(button, never()).startAnimation(jumpDownAnimation)
            }
        }
    }
}
