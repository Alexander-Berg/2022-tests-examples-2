package ru.yandex.metrika.util.collections;

import org.junit.Test;

import static java.lang.Integer.toBinaryString;
import static org.hamcrest.core.Is.is;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertThat;

/**
 * Created by kyrylhol on 2/10/14.
 */
public class BinaryTrieTest {

    @Test(expected = IllegalArgumentException.class)
    public void testBinaryTrieWrongString1() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        trie.replace("01010111-", "1");
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBinaryTrieWrongString2() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        trie.replace("01010111", "1");
        trie.replace("01010111", "2");
        trie.replace("01010111", "3");
        trie.replace("01010111", "4");
        trie.replace("01010110", "5");
        trie.replace("0101/0111", "1");
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBinaryTrieReplaceNull() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        trie.replace("01010111", "1");
        trie.replace("01010111", "2");
        trie.replace(null, "1");
    }

    @Test
    public void testBinaryTrieReplace1() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        String oldValue = trie.replace("01010111", "1");
        assertNull(oldValue);
        oldValue = trie.replace("01010111", "2");
        assertThat(oldValue, is("1"));
    }

    @Test
    public void testBinaryTrieReplace2() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        for (int i = 0; i < 256; i++) {
            String oldValue = trie.replace(toBinaryString(i), String.valueOf(i));
            assertNull(oldValue);
        }
        for (int i = 0; i < 256; i++) {
            String oldValue = trie.replace(toBinaryString(i), "-" + i);
            assertThat(oldValue, is(String.valueOf(i)));
        }
        for (int i = 0; i < 256; i++) {
            String oldValue = trie.replace(toBinaryString(i), "+" + i);
            assertThat(oldValue, is("-" + i));
        }
    }

    @Test
    public void testContainsPrefixOf1() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        trie.replace("01", "1");
        trie.replace("010", "2");
        trie.replace("011", "3");
        trie.replace("0101", "5");
        assertThat(trie.containsPrefixOf("011111"), is("3"));
    }

    @Test
    public void testContainsPrefixOf2() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        trie.replace("1", "1");
        trie.replace("11", "11");
        trie.replace("111", "1111");
        trie.replace("1111", "1111");
        trie.replace("11111", "11111");
        trie.replace("111111", "111111");
        trie.replace("1111111", "1111111");
        assertNull(trie.containsPrefixOf("0"));
        assertNull(trie.containsPrefixOf("00"));
        assertNull(trie.containsPrefixOf("000"));
        assertNull(trie.containsPrefixOf("0000"));
        assertNull(trie.containsPrefixOf("00000"));
        assertNull(trie.containsPrefixOf("000000"));
        assertNull(trie.containsPrefixOf("0000000"));
        assertNull(trie.containsPrefixOf("0"));
        assertNull(trie.containsPrefixOf("01"));
        assertNull(trie.containsPrefixOf("011"));
        assertNull(trie.containsPrefixOf("0111"));
        assertNull(trie.containsPrefixOf("01111"));
        assertNull(trie.containsPrefixOf("011111"));
        assertNull(trie.containsPrefixOf("0111111"));
    }

    @Test
    public void testContainsPrefixOf3() {
        BinaryTrie<String> trie = new BinaryTrie<>();
        for (int i = 0; i < 256; i++) {
            trie.replace(toBinaryString(i), String.valueOf(i));
        }
        for (int i = 0; i < 256; i++) {
            assertThat(trie.containsPrefixOf(toBinaryString(i)), is(String.valueOf(i)));
        }
    }

}
