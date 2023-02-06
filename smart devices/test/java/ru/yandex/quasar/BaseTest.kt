package ru.yandex.quasar

import org.junit.Before
import org.mockito.MockitoAnnotations

abstract class BaseTest {

    @Before
    fun initMocks() {
        MockitoAnnotations.initMocks(this)
    }
}