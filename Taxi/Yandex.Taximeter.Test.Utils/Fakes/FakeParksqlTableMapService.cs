using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Yandex.Taximeter.Core.Helper;
using Yandex.Taximeter.Core.Services.Sql;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeParkSqlTableMapService : IParkSqlTableMapService
    {
        public IDictionary<(string, SqlDatabase), SqlTableMappingEntry> Mapping { get; }
            = new Dictionary<(string, SqlDatabase), SqlTableMappingEntry>();

        public ValueTask<IParkSqlTableMapping> GetMappingAsync()
            => new ValueTask<IParkSqlTableMapping>(new FakeParkSqlTableMapping(Mapping));

        public Task TryInitCacheAsync() => Task.CompletedTask;
    }

    public class FakeParkSqlTableMapping : IParkSqlTableMapping
    {
        private readonly IDictionary<(string, SqlDatabase), SqlTableMappingEntry> _mappings;

        public FakeParkSqlTableMapping(IDictionary<(string, SqlDatabase), SqlTableMappingEntry> mappings)
        {
            _mappings = mappings;
        }

        public IReadOnlyCollection<string> SeparateTableParks => throw new NotImplementedException();
        public IReadOnlyDictionary<string, int> TableShardMap => throw new NotImplementedException();

        public SqlTableMappingEntry GetParkMap(string parkId, SqlDatabase table)
            => _mappings.TryGetValue((parkId, table), out var entry)
                ? entry
                : new SqlTableMappingEntry("default_table", 0);

        public SqlTableMappingEntry GetCompositeMap(ulong tableNum, SqlDatabase table)
            => throw new NotImplementedException();
    }
}