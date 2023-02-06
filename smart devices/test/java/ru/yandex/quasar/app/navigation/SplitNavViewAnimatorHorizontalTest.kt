package ru.yandex.quasar.app.navigation

import org.junit.Assert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.robolectric.ParameterizedRobolectricTestRunner
import ru.yandex.quasar.app.R
import ru.yandex.quasar.app.navigation.IsSameAnimation.Companion.sameAnimation
import ru.yandex.quasar.app.ui.views.navigation.*
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_LEFT
import ru.yandex.quasar.app.webview.mordovia.DIRECTION_RIGHT
import ru.yandex.quasar.fakes.FakeResources

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontalTest_Given_BothAvailable_When_DirectionChanges(
    private val previous: DirectionsState,
    private val current: DirectionsState
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT))),
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)))
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setTextAlpha, previous.direction)
        val fadeInTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 300, navView::setTextAlpha, current.direction)

        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0.5F, 600, navView::setArrowAlpha, previous.direction)
        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0.5F, 1F, 300, navView::setArrowAlpha, current.direction)

        val arrowAnimation = SerialAnimation(fadeOutArrowAnimator.toSingle(), fadeInArrowAnimator.toSingle())

        val expected = TogetherAnimation(fadeOutTextAnimator.toSingle(), fadeInTextAnimator.toSingle(), arrowAnimation)

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontalTest_Given_OnlyLeftAvailable_When_DirectionChangesAndBothAvailable(
    private val previous: DirectionsState,
    private val current: DirectionsState
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)))
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setTextAlpha, previous.direction)
        val fadeInTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 300, navView::setTextAlpha, current.direction)

        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0.5F, 600, navView::setArrowAlpha, previous.direction)
        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 600, navView::setArrowAlpha, current.direction)

        val changeWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, R.dimen.left_right_spotter_width, 600, subject::changeHorizontalSpotterWidth)

        val expected = TogetherAnimation(
            fadeOutArrowAnimator.toSingle(),
            fadeInArrowAnimator.toSingle(),
            changeWidthAnimator.toSingle(),
            SerialAnimation(
                fadeOutTextAnimator.toSingle(),
                fadeInTextAnimator.toSingle()
            )
        )

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontalTest_Given_OnlyRightAvailable_When_DirectionChangesAndBothAvailable(
    private val previous: DirectionsState,
    private val current: DirectionsState
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT)))
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setTextAlpha, previous.direction)
        val fadeInTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 300, navView::setTextAlpha, current.direction)

        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0.5F, 600, navView::setArrowAlpha, previous.direction)
        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 600, navView::setArrowAlpha, current.direction)

        val changeWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, R.dimen.left_right_spotter_width, 600, subject::changeHorizontalSpotterWidth)

        val jumpOutAnimator = SplitNavViewAnimatorBase.OvershootAnimator(R.dimen.spotter_arrow_padding_before_jump_out, R.dimen.horizontal_arrow_margin, 600, subject::leftArrowJumpOutMove)

        val expected = TogetherAnimation(
            jumpOutAnimator.toSingle(),
            fadeOutArrowAnimator.toSingle(),
            fadeInArrowAnimator.toSingle(),
            changeWidthAnimator.toSingle(),
            SerialAnimation(
                fadeOutTextAnimator.toSingle(),
                fadeInTextAnimator.toSingle()
            )
        )

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontalTest_Given_OnlyRightAvailable_When_BothBecomeAvailable(
    private val previous: DirectionsState,
    private val current: DirectionsState
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)))
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 0.5F, 600, navView::setArrowAlpha, DIRECTION_LEFT)

        val changeWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, R.dimen.left_right_spotter_width, 600, subject::changeHorizontalSpotterWidth)
        val jumpOutAnimator = SplitNavViewAnimatorBase.OvershootAnimator(R.dimen.spotter_arrow_padding_before_jump_out, R.dimen.horizontal_arrow_margin, 600, subject::leftArrowJumpOutMove)

        val expected = TogetherAnimation(fadeInArrowAnimator.toSingle(), changeWidthAnimator.toSingle(), jumpOutAnimator.toSingle())

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontalTest_Given_OnlyLeftAvailable_When_BothBecomeAvailable(
    private val previous: DirectionsState,
    private val current: DirectionsState
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT)))
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 0.5F, 600, navView::setArrowAlpha, DIRECTION_RIGHT)
        val changeWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, R.dimen.left_right_spotter_width, 600, subject::changeHorizontalSpotterWidth)

        val expected = TogetherAnimation(fadeInArrowAnimator.toSingle(), changeWidthAnimator.toSingle())

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontal_Given_BothAvailable_When_OneBecomesUnavailable(
    private val previous: DirectionsState,
    private val current: DirectionsState,
    private val spotterWidth: Int
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), R.dimen.left_spotter_width),
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), R.dimen.right_spotter_width)
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutDirection = previous.available.and(current.available.inv())
        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setArrowAlpha, fadeOutDirection)

        val changeWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, spotterWidth, 600, subject::changeHorizontalSpotterWidth)

        val expected = SerialAnimation(fadeOutArrowAnimator.toSingle(), changeWidthAnimator.toSingle())

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontal_Given_BothAvailable_When_OneBecomesUnavailableAndCurrentDirectionChanges(
    private val previous: DirectionsState,
    private val current: DirectionsState,
    private val spotterWidth: Int
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), R.dimen.right_spotter_width),
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT.or(DIRECTION_LEFT)), DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), R.dimen.left_spotter_width)
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutDirection = previous.available.and(current.available.inv())

        val fadeOutTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setTextAlpha, fadeOutDirection)
        val fadeInTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 600, navView::setTextAlpha, current.direction)

        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setArrowAlpha, fadeOutDirection)
        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0.5F, 1F, 600, navView::setArrowAlpha, current.direction)

        val spotterWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, spotterWidth, 600, subject::changeHorizontalSpotterWidth)

        val arrowAnimator = SerialAnimation(fadeOutArrowAnimator.toSingle(),
            TogetherAnimation(fadeInArrowAnimator.toSingle(), spotterWidthAnimator.toSingle()))
        val textAnimator = SerialAnimation(fadeOutTextAnimator.toSingle(), fadeInTextAnimator.toSingle())

        val expected = TogetherAnimation(arrowAnimator, textAnimator)

        assertThat(animations, sameAnimation(expected))
    }
}

@RunWith(ParameterizedRobolectricTestRunner::class)
class SplitNavViewAnimatorHorizontal_Given_OnlyOneAvailable_When_ItBecomesUnavailableAndOtherBecomesAvailable(
    private val previous: DirectionsState,
    private val current: DirectionsState,
    private val spotterWidth: Int
) {

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun data() = listOf(
            arrayOf(DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), R.dimen.right_spotter_width),
            arrayOf(DirectionsState(DIRECTION_RIGHT, DIRECTION_RIGHT), DirectionsState(DIRECTION_LEFT, DIRECTION_LEFT), R.dimen.left_spotter_width)
        )
    }

    @Test
    fun check() {
        val navView: SplitNavDirectionsView = mock()
        val subject = SplitNavViewAnimatorHorizontal(navView, mock(), FakeResources())

        val animations = subject.createAnimations(current, previous)

        val fadeOutTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0F, 300, navView::setTextAlpha, previous.available)
        val fadeInTextAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0F, 1F, 300, navView::setTextAlpha, current.direction)

        val fadeOutArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(1F, 0.5F, 600, navView::setArrowAlpha, previous.available)
        val fadeInArrowAnimator = SplitNavViewAnimatorBase.ChangeDirectionAnimator(0.5F, 1F, 600, navView::setArrowAlpha, current.direction)

        val spotterWidthAnimator = SplitNavViewAnimatorBase.OvershootAnimator(0, spotterWidth, 600, subject::changeHorizontalSpotterWidth)


        val textAnimator = SerialAnimation(fadeOutTextAnimator.toSingle(),
            TogetherAnimation(
                fadeInTextAnimator.toSingle(),
                SerialAnimation(
                    spotterWidthAnimator.toSingle(),
                    fadeInArrowAnimator.toSingle()
                )
            )
        )

        val expected = TogetherAnimation(textAnimator, fadeOutArrowAnimator.toSingle())

        assertThat(animations, sameAnimation(expected))
    }
}
