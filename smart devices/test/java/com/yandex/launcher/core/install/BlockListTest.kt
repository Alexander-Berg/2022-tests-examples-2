package com.yandex.launcher.core.install

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.core.install.BlockList
import org.hamcrest.Matchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test

class BlockListTest : BaseRobolectricTest() {

    @Test
    fun `put hash to BlockList, BlockList contains hash`() {
        val blockList = BlockList(updateContext, "test")

        blockList.addHash("a")

        assertThat(blockList.contains("a"), equalTo(true))
    }

    @Test
    fun `put hash to first BlockList, second BlockList doesn't contain hash`() {
        val first = BlockList(updateContext, "first")
        val second = BlockList(updateContext, "second")

        first.addHash("a")

        assertThat(second.contains("a"), equalTo(false))
    }

    @Test
    fun `put hash to first BlockList, second BlockList has same prefsName, second contains hash`() {
        val first = BlockList(updateContext, "common")
        val second = BlockList(updateContext, "common")

        first.addHash("a")

        assertThat(second.contains("a"), equalTo(true))
    }
}
