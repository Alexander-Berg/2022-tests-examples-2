package com.yandex.tv.setupwizard.navigation

import com.yandex.tv.setupwizard.navigation.NavigationGraphValidator.Node
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.notNullValue
import org.hamcrest.Matchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class NavigationGraphValidatorPathTest {

    lateinit var validator: NavigationGraphValidator

    @Before
    fun setup() {
        validator = NavigationGraphValidator()
    }

    @Test
    fun `two nodes connected in one direction, path should exist`() {
        val a = Node("A")
        val b = Node("B")

        a.transitions.add(b)

        val path = validator.getPath(a, b)

        assertThat(path, `is`(notNullValue()))
    }

    @Test
    fun `two nodes connected in both directions, path should exist`() {
        val a = Node("A")
        val b = Node("B")

        a.transitions.add(b)
        b.transitions.add(a)

        val path = validator.getPath(a, b)

        assertThat(path, `is`(notNullValue()))
    }

    @Test
    fun `two nodes not connected, path should not exist`() {
        val a = Node("A")
        val b = Node("B")

        val path = validator.getPath(a, b)

        assertThat(path, `is`(nullValue()))
    }

    @Test
    fun `three nodes connected in one direction, path should exist`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(c)

        val path = validator.getPath(a, c)

        assertThat(path, `is`(notNullValue()))
    }

    @Test
    fun `three nodes connected in one direction, reverse path should not exist`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(c)

        val path = validator.getPath(c, a)

        assertThat(path, `is`(nullValue()))
    }

    @Test
    fun `three nodes connected in one direction, path contain nodes in right order`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(c)

        val path = validator.getPath(a, c)!!

        assertThat(path[0], `is`(a))
        assertThat(path[1], `is`(b))
        assertThat(path[2], `is`(c))
    }


    @Test
    fun `three nodes connected in both directions, path should exist`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(a)

        b.transitions.add(c)
        c.transitions.add(b)

        val path = validator.getPath(a, c)

        assertThat(path, `is`(notNullValue()))
    }

    @Test
    fun `three nodes connected in both directions, each has extra leafs, path should exist`() {
        val a = Node("A")
        val b = Node("B")
        val c = Node("C")

        a.transitions.add(b)
        b.transitions.add(a)

        b.transitions.add(c)
        c.transitions.add(b)

        repeat(10) { index ->
            a.transitions.add(Node("A-$index"))
            b.transitions.add(Node("B-$index"))
            c.transitions.add(Node("C-$index"))
        }

        val path = validator.getPath(a, c)

        assertThat(path, `is`(notNullValue()))
    }
}
