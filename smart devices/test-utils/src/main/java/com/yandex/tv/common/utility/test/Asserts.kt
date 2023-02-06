package com.yandex.tv.common.utility.test

import android.os.Bundle
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo

fun assertBundlesEqual(one: Bundle?, another: Bundle?) {
    assertThat(one?.size(), equalTo(another?.size()))
    one?.keySet()?.forEach {
        val oneValue = one.get(it)
        val anotherValue = another?.get(it)
        if (oneValue is Bundle && anotherValue is Bundle) {
            assertBundlesEqual(oneValue, anotherValue)
        } else {
            assertThat(oneValue, equalTo(anotherValue))
        }
    }
}
