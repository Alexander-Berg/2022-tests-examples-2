using System;
using System.ComponentModel.DataAnnotations.Schema;
using System.Data;
using System.Data.Common;
using System.Linq;
using System.Runtime.InteropServices.ComTypes;
using FluentAssertions;
using Xunit;
using Yandex.Taximeter.Core.Extensions;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Models.Orders;
using Yandex.Taximeter.Core.Repositories.Sql;

namespace Yandex.Taximeter.Common.Tests.Extensions
{
    public class SqlClientExtensionsTest
    {
        private class TestData
        {
            [Column("int_val")]
            public int IntVal { get; set; }
            
            [Column("string_val")]
            public string StringVal { get; set; }
            
            [Column("date_val")]
            public DateTime DateVal { get; set; }
            
            [Column("enum_val")]
            public DiscountType EnumVal { get; set; }
        }
        
        [Fact]
        public void TestTypeMapping_Fields()
        {
            var typeMap = SqlTypeMap.Get<TestData>();
            typeMap.Select(x => x.ColumnName).Should().Equal(new[] {"int_val", "string_val", "date_val", "enum_val"});
            typeMap.Select(x => x.PropertyName).Should().Equal(new[] {"IntVal", "StringVal", "DateVal", "EnumVal"});
        }

        [Fact]
        public void TestTypeMapping_Read()
        {
            var typeMap = SqlTypeMap.Get<TestData>();
            var dataTable = new DataTable();
            foreach (var x in typeMap)
            {
                dataTable.Columns.Add(x.ColumnName, x.Property.PropertyType.IsEnum ? x.Property.PropertyType.GetEnumUnderlyingType() : x.Property.PropertyType);
            }

            var entry = new TestData
            {
                IntVal = 1,
                StringVal = "Hello",
                DateVal = new DateTime(2000, 01, 01),
                EnumVal = DiscountType.Процент
            };
            var row = typeMap.Select(x => x.Property.GetValue(entry)).ToArray();
            dataTable.LoadDataRow(row, LoadOption.OverwriteChanges);

            var reader = dataTable.CreateDataReader();
            reader.Read();
            var newEntry = reader.ConvertRecord<TestData>();
            newEntry.IntVal.Should().Be(entry.IntVal);
            newEntry.StringVal.Should().Be(entry.StringVal);
            newEntry.DateVal.Should().Be(entry.DateVal);
            newEntry.EnumVal.Should().Be(entry.EnumVal);
        }
    }
}