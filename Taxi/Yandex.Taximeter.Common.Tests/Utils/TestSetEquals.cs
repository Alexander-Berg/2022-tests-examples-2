using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;

public class SetEqualsTest
{
    private static bool Equals(HashSet<string> set1, SortedSet<string> set2)
    {
        return (set1.IsNullOrEmpty() && set2.IsNullOrEmpty()) ||
               (!set1.IsNullOrEmpty() &&
                set1.SetEquals(set2 == null ? new HashSet<string>() : new HashSet<string>(set2)));
    }

    [Fact]
    public void TestSortedSetConstruction()
    {
        var set1 = new SortedSet<string>(new[] {"123"}); 
        var set2 = new SortedSet<string>{"123"};

        set1.SetEquals(set2).Should().Be(true);
    }

    [Fact]
    public void TestSetEquals()
    {
        HashSet<string> set1 = null;
        SortedSet<string> set2 = null;

        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string>();
        set2 = null;
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = null;
        set2 = new SortedSet<string>();
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string>();
        set2 = new SortedSet<string>();
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string> { "1" };
        set2 = null;
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = null;
        set2 = new SortedSet<string> { "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "1" };
        set2 = new SortedSet<string>();
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string>();
        set2 = new SortedSet<string> { "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "1" };
        set2 = new SortedSet<string> { "1" };
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string> { "1" };
        set2 = new SortedSet<string> { "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "1", "2" };
        set2 = new SortedSet<string> { "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "2" };
        set2 = new SortedSet<string> { "1", "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "1", "2" };
        set2 = new SortedSet<string> { "2" };
        
        Equals(set1, set2).Should().Be(false);
        
        set1 = new HashSet<string> { "1", "2" };
        set2 = new SortedSet<string> { "1", "2" };
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string> { "2", "1" };
        set2 = new SortedSet<string> { "1", "2" };
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string> { "1", "1", "2" };
        set2 = new SortedSet<string> { "1", "2" };
        
        Equals(set1, set2).Should().Be(true);
        
        set1 = new HashSet<string> { "1", "2", "3" };
        set2 = new SortedSet<string> { "1", "2" };
        
        Equals(set1, set2).Should().Be(false);
    }
}