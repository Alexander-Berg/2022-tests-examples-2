package ru.yandex.quasar.glagol.impl

import org.junit.Test

class ExtraDataTransformerTest {

    @Test
    fun testSoftwareVersionTransform() {
        val map = mutableMapOf(
            Pair("ololo", "ololo"),
            Pair(KEY_SOFTWARE_VERSION, "2.74.5.7.1014551844.20210709.40")
        )
        ExtraDataTransformer.transformExtra(map)

        assert(map[KEY_SOFTWARE_VERSION_INT] == "74")
        assert(map[KEY_SOFTWARE_VERSION] == "2.74.5.7.1014551844.20210709.40")


        val map2 = mutableMapOf(
            Pair("ololo", "ololo"),
            Pair(KEY_SOFTWARE_VERSION, "1.9999.5.7.1014551844.20210709.40")
        )
        ExtraDataTransformer.transformExtra(map2)

        assert(map2[KEY_SOFTWARE_VERSION_INT] == "9999")
        assert(map2[KEY_SOFTWARE_VERSION] == "1.9999.5.7.1014551844.20210709.40")
    }

    @Test
    fun testEmptySoftwareVersion() {
        val map = mutableMapOf(Pair("ololo", "ololo"))
        ExtraDataTransformer.transformExtra(map)
        assert(!map.contains(KEY_SOFTWARE_VERSION))
        assert(!map.contains(KEY_SOFTWARE_VERSION_INT))
    }

    companion object {
        const val KEY_SOFTWARE_VERSION = "softwareVersion"
        const val KEY_SOFTWARE_VERSION_INT = "softwareVersionInt"
    }
}
