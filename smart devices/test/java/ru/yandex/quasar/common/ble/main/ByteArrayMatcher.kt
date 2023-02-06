package ru.yandex.quasar.common.ble.main

import org.hamcrest.Description
import org.hamcrest.Matcher
import org.hamcrest.TypeSafeMatcher

class IsSameByteArrayMatcher(
        private val expected: ByteArray
) : TypeSafeMatcher<ByteArray>() {
    override fun describeTo(description: Description?) {
        description?.appendText(expected.contentToString())
    }

    override fun matchesSafely(item: ByteArray?): Boolean {
        if(item == null) {
            return false
        }

        if(item.size != expected.size) {
            return false
        }

        return expected.toList() == item.toList()
    }

    companion object {
        fun sameByteArray(expected: ByteArray): Matcher<ByteArray> {
            return IsSameByteArrayMatcher(expected)
        }
    }
}
