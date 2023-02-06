package com.yandex.tv.setupwizard.navigation

import com.yandex.tv.setupwizard.R
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(application = android.app.Application::class, manifest="src/main/AndroidManifest.xml", sdk = [24])
class NavigationGraphTest {

    lateinit var validator: NavigationGraphValidator

    @Before
    fun setup() {
        validator = NavigationGraphValidator()
    }

    @Test
    fun `pass module xml graph to validator, should not throw exceptions`() {
        val graph = NavigationGraphCreator.create(RuntimeEnvironment.application, R.xml.module_suw_navigation)
        validator.validate(graph, isModule = true)
    }

    @Test
    fun `pass tv xml graph to validator, should not throw exceptions`() {
        val graph = NavigationGraphCreator.create(RuntimeEnvironment.application, R.xml.tv_suw_navigation)

        validator.validate(graph, isModule = false)
    }

}
