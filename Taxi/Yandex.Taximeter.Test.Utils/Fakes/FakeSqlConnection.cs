using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Npgsql;
using Yandex.Taximeter.Core.Log;
using Yandex.Taximeter.Core.Services.Sql;

namespace Yandex.Taximeter.Test.Utils.Fakes
{
    public class FakeSqlConnectionFactory: ISqlConnectionFactory
    {
        private readonly IDictionary<SqlConnectionTarget, FakeSqlConnection> _connections = new Dictionary<SqlConnectionTarget, FakeSqlConnection>();
        
        public ISqlConnection GetConnection(SqlConnectionTarget target, bool logSql = false)
        {
            return _connections.SafeGet(target);
        }
        
        public IDictionary<string, PoolCounters> GetCounters()
        {
            return new Dictionary<string, PoolCounters>();
        }

        public FakeSqlConnection SetupConnection(SqlConnectionTarget target)
        {
            return _connections[target] = new FakeSqlConnection();
        }
        public FakeSqlConnection SetupConnection(SqlDatabase database, SqlReplica replica, int shard)
        {
            return SetupConnection(new SqlConnectionTarget(database, replica, shard));
        }
    }

    public class FakeSqlConnection : ISqlConnection, ISqlTransaction
    {
        public List<string> Queries { get; } = new List<string>();
        
        public List<IDictionary<string, object>> Parameters { get; } = new List<IDictionary<string, object>>();
        
        private readonly List<object[]> _results = new List<object[]>(); 
        
        public virtual void Dispose()
        {
        }

        public void SetupResult(params object[] results)
        {
            _results.Add(results);
        }

        public virtual IAsyncEnumerable<T> QueryAsync<T>(string sql, Func<IDataRecord, T> converter, object parameters = null, int timeout = 0)
        {
            Queries.Add(sql);
            Parameters.Add(parameters.ToDictionary());
            var idx = Queries.Count - 1;
            if (_results.Count > idx) return _results[idx].Cast<T>().ToAsyncEnumerable();
            return AsyncEnumerable.Empty<T>();
        }

        public virtual async Task<T> ExecuteScalarAsync<T>(string sql, object parameters = null, int timeout = 0,
            CancellationToken cancellationToken = default)
        {
            Queries.Add(sql);
            Parameters.Add(parameters.ToDictionary());
            var idx = Queries.Count - 1;
            if (_results.Count > idx) return _results[idx].Cast<T>().First();
            return default;
        }

        public virtual async Task<int> ExecuteNonQueryAsync(string sql, object parameters = null, int timeout = 0,
            CancellationToken cancellationToken = default)
        {
            Queries.Add(sql);
            Parameters.Add(parameters.ToDictionary());
            var idx = Queries.Count - 1;
            if (_results.Count > idx) return _results[idx].Cast<int>().First();
            return 0;
        }

        public virtual async Task<ISqlTransaction> BeginTransactionAsync(IsolationLevel isolationLevel = IsolationLevel.Unspecified, CancellationToken cancellationToken = default)
        {
            return this;
        }

        public async Task CommitAsync(CancellationToken cancellationToken = default)
        {
        }

        public async Task RollbackAsync(CancellationToken cancellationToken = default)
        {
        }
    }
}