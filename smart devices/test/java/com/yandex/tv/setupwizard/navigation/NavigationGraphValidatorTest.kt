package com.yandex.tv.setupwizard.navigation

import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.notNullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.`when`
import org.mockito.Mockito.mock
import org.mockito.kotlin.any
import org.robolectric.RobolectricTestRunner
import java.lang.RuntimeException

@RunWith(RobolectricTestRunner::class)
class NavigationGraphValidatorTest {

    lateinit var validator: NavigationGraphValidator

    @Before
    fun setup() {
        validator = NavigationGraphValidator()
    }

    @Test
    fun `three connected source nodes, should stay connected after conversion`() {

        val a = NavigationGraph.Node().apply {
            name = "A"
            transitions = mutableMapOf()
        }
        val b = NavigationGraph.Node().apply {
            name = "B"
            transitions = mutableMapOf()
        }
        val c = NavigationGraph.Node().apply {
            name = "C"
            transitions = mutableMapOf()
        }

        a.transitions[b.name] = Destination(b.name, null, false)
        b.transitions[c.name] = Destination(c.name, null, false)

        val sourceGraph = NavigationGraph().apply {
            nodes[a.name] = a
            nodes[b.name] = b
            nodes[c.name] = c
        }

        val nodes = validator.getNodes(sourceGraph)

        val convertedA = nodes.first { it.name == "A" }
        val convertedB = nodes.first { it.name == "B" }
        val convertedC = nodes.first { it.name == "C" }

        assertThat(convertedA.transitions[0], equalTo(convertedB))
        assertThat(convertedB.transitions[0], equalTo(convertedC))
    }

    @Test
    fun `three connected source nodes, contains initial and final, graph should be converted without exceptions`() {

        val a = NavigationGraph.Node().apply {
            name = "A"
            transitions = mutableMapOf()
        }
        val b = NavigationGraph.Node().apply {
            name = "B"
            transitions = mutableMapOf()
        }
        val c = NavigationGraph.Node().apply {
            name = "C"
            transitions = mutableMapOf()
        }

        val sourceGraph = NavigationGraph().apply {
            nodes[a.name] = a
            nodes[b.name] = b
            nodes[c.name] = c
        }

        sourceGraph.initialScreen = a.name
        sourceGraph.finalScreen = c.name

        validator.getGraph(sourceGraph)
    }

    @Test
    fun `three connected source nodes, contains initial, lack of final, graph should be converted with exceptions`() {

        val a = NavigationGraph.Node().apply {
            name = "A"
            transitions = mutableMapOf()
        }
        val b = NavigationGraph.Node().apply {
            name = "B"
            transitions = mutableMapOf()
        }
        val c = NavigationGraph.Node().apply {
            name = "C"
            transitions = mutableMapOf()
        }

        val sourceGraph = NavigationGraph().apply {
            nodes[a.name] = a
            nodes[b.name] = b
            nodes[c.name] = c
        }

        sourceGraph.initialScreen = a.name

        val exception = kotlin.runCatching { validator.getGraph(sourceGraph) }
            .exceptionOrNull()
        assertThat(exception, `is`(notNullValue()))
    }

    @Test
    fun `three connected source nodes, lack of initial, contains final, graph should be converted with exceptions`() {

        val a = NavigationGraph.Node().apply {
            name = "A"
            transitions = mutableMapOf()
        }
        val b = NavigationGraph.Node().apply {
            name = "B"
            transitions = mutableMapOf()
        }
        val c = NavigationGraph.Node().apply {
            name = "C"
            transitions = mutableMapOf()
        }

        val sourceGraph = NavigationGraph().apply {
            nodes[a.name] = a
            nodes[b.name] = b
            nodes[c.name] = c
        }

        sourceGraph.finalScreen = c.name

        val exception = kotlin.runCatching { validator.getGraph(sourceGraph) }
            .exceptionOrNull()
        assertThat(exception, `is`(notNullValue()))
    }

    @Test
    fun `three connected source nodes, initial points on non-existent node, graph should be converted with exceptions`() {

        val a = NavigationGraph.Node().apply {
            name = "A"
            transitions = mutableMapOf()
        }
        val b = NavigationGraph.Node().apply {
            name = "B"
            transitions = mutableMapOf()
        }
        val c = NavigationGraph.Node().apply {
            name = "C"
            transitions = mutableMapOf()
        }

        val sourceGraph = NavigationGraph().apply {
            nodes[a.name] = a
            nodes[b.name] = b
            nodes[c.name] = c
        }

        sourceGraph.initialScreen = "NON-EXISTENT NODE NAME"
        sourceGraph.finalScreen = c.name

        val exception = kotlin.runCatching { validator.getGraph(sourceGraph) }
            .exceptionOrNull()
        assertThat(exception, `is`(notNullValue()))
    }

    @Test
    fun `getGraph throws exception, baseValidation should re-throw`() {

        val validator = mock(NavigationGraphValidator::class.java)
        `when`(validator.validateBasic(any())).thenCallRealMethod()
        `when`(validator.getGraph(any())).thenThrow(RuntimeException("getGraph failure"))

        val exception = kotlin.runCatching { validator.validateBasic(NavigationGraph())}
            .exceptionOrNull()

        assertThat(exception, `is`(notNullValue()))
    }
}
