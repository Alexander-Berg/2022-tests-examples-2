package com.yandex.tv.setupwizard.navigation

import com.yandex.tv.setupwizard.navigation.NavigationGraphValidator.Node
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasItems
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class NavigationGraphValidatorReachableNodesTest {

    lateinit var validator: NavigationGraphValidator

    @Before
    fun setup() {
        validator = NavigationGraphValidator()
    }

    @Test
    fun `two nodes connected in one direction, both should be reachable`() {
        val a = Node("A")
        val b = Node("B")

        a.transitions.add(b)

        val reachable = validator.getReachableNodes(a)

        assertThat(reachable, hasItems(a, b))
        assertThat(reachable.size, equalTo(2))
    }

    @Test
    fun `two nodes connected in both directions, both should be reachable`() {
        val a = Node("A")
        val b = Node("B")

        a.transitions.add(b)
        b.transitions.add(a)

        val reachable = validator.getReachableNodes(a)

        assertThat(reachable, hasItems(a, b))
        assertThat(reachable.size, equalTo(2))
    }

    @Test
    fun `two nodes not connected, only first should be reachable`() {
        val a = Node("A")
        val b = Node("B")

        val reachable = validator.getReachableNodes(a)

        // from contains docs:
        // For a positive match, the examined iterable must be of the same length as the number of specified items.
        assertThat(reachable, contains(a))
    }

    @Test
    fun `three nodes connected in one direction, all should be reachable`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(c)

        val reachable = validator.getReachableNodes(a)

        assertThat(reachable, hasItems(a, b, c))
        assertThat(reachable.size, equalTo(3))
    }

    @Test
    fun `three nodes connected in one direction, only last should be reachable from last`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(c)

        val reachable = validator.getReachableNodes(c)

        assertThat(reachable, contains(c))
    }

    @Test
    fun `three nodes connected in both directions, each has extra leafs, all should be reachable`() {

        val allNodes = mutableListOf<Node>()
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        allNodes.add(a)
        allNodes.add(b)
        allNodes.add(c)

        a.transitions.add(b)
        b.transitions.add(a)

        b.transitions.add(c)
        c.transitions.add(b)

        repeat(10) { index ->
            val aLeaf = Node("A-$index")
            val bLeaf = Node("B-$index")
            val cLeaf = Node("C-$index")

            allNodes.add(aLeaf)
            allNodes.add(bLeaf)
            allNodes.add(cLeaf)

            a.transitions.add(aLeaf)
            b.transitions.add(bLeaf)
            c.transitions.add(cLeaf)
        }

        val reachable = validator.getReachableNodes(a)

        assertThat(reachable, hasItems(*allNodes.toTypedArray()))
        assertThat(reachable.size, equalTo(allNodes.size))
    }
}
