package ru.yandex.quasar.centaur_app

import org.junit.BeforeClass

open class BaseTest {

    companion object {
        @BeforeClass
        @JvmStatic
        fun setUp() {
            CentaurApp.isInTestHarness = true
        }
    }
}
