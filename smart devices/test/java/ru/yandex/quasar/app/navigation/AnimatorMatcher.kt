package ru.yandex.quasar.app.navigation

import android.animation.Animator
import org.hamcrest.Matchers.hasItem
import org.hamcrest.Description
import org.hamcrest.Matcher
import org.hamcrest.TypeSafeMatcher
import ru.yandex.quasar.app.ui.views.navigation.*

class IsSameAnimation(
    private val expected: ComplexAnimation
) : TypeSafeMatcher<ComplexAnimation>() {

    override fun describeTo(description: Description?) {
        description?.appendText(expected.toString())
    }

    override fun matchesSafely(item: ComplexAnimation?): Boolean {
        if (item == null) {
            return false
        }

        if (item.animators.size != expected.animators.size) {
            return false
        }

        if (item.javaClass != expected.javaClass) {
            return false
        }

        if (item is SingleAnimation && expected is SingleAnimation) {
            return isSameAnimation(item.animator, expected.animator)
        } else if (item is SerialAnimation && expected is SerialAnimation) {
            return item.animators.zip(expected.animators).all { sameAnimation(it.first)!!.matches(it.second) }
        } else if (item is TogetherAnimation && expected is TogetherAnimation) {
            return item.animators.all { hasItem(sameAnimation(it)).matches(expected.animators) }
        } else {
            throw java.lang.Exception("Unknown animation type")
        }
    }

    private fun isSameAnimation(a: Animator, b: Animator): Boolean {
        when (a) {
            is SplitNavViewAnimatorBase.OvershootAnimator ->
                return b is SplitNavViewAnimatorBase.OvershootAnimator
                    && a.startValue == b.startValue
                    && a.endValue == b.endValue
                    && a.duration == b.duration
                    && a.valueSetter == b.valueSetter
            is SplitNavViewAnimatorBase.ChangeDirectionAnimator ->
                return b is SplitNavViewAnimatorBase.ChangeDirectionAnimator
                    && a.startValue == b.startValue
                    && a.endValue == b.endValue
                    && a.direction == b.direction
                    && a.duration == b.duration
                    && a.valueSetter == b.valueSetter
            else -> throw Exception("Unknown animation type")
        }
    }

    companion object {
        fun sameAnimation(expected: ComplexAnimation): Matcher<ComplexAnimation>? {
            return IsSameAnimation(expected)
        }
    }
}
