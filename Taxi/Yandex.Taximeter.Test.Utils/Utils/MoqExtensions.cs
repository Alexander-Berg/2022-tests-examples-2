using System;
using System.Threading.Tasks;
using Moq.Language.Flow;

namespace Yandex.Taximeter.Test.Utils.Utils
{
    public static class MoqExtensions
    {
        public static IReturnsResult<TMock> ReturnsAsync<TMock, TResult>(this ISetup<TMock, Task<TResult>> setup,
            TResult value) where TMock : class
        {
            return setup.Returns(() => Task.FromResult(value));
        }

        public static IReturnsResult<TMock> ReturnsAsync<TMock, TArg, TResult>(this ISetup<TMock, Task<TResult>> setup,
           Func<TArg, TResult> func) where TMock : class
        {
            return setup.Returns((TArg arg) => Task.FromResult(func(arg)));
        }

        public static IReturnsResult<TMock> ReturnsAsync<TMock, TArg1, TArg2, TResult>(this ISetup<TMock, Task<TResult>> setup,
           Func<TArg1, TArg2, TResult> func) where TMock : class
        {
            return setup.Returns((TArg1 arg1, TArg2 arg2) => Task.FromResult(func(arg1, arg2)));
        }
    }
}