import { FetchError } from './fetchData';

import { formatFetchErrorMessage } from './formatFetchErrorMessage';

describe('formatFetchErrorMessage', () => {
  it('returns pure error message when type of error is not `response`', () => {
    const networkError: FetchError = {
      _tag: 'network',
      message: 'foo',
      url: 'yandex.ru'
    };

    const parserError: FetchError = {
      _tag: 'parser',
      message: 'foo',
      url: 'yandex.ru'
    };

    expect(formatFetchErrorMessage(networkError)).toBe('foo');
    expect(formatFetchErrorMessage(parserError)).toBe('foo');
  });

  it('returns concatenation of code an message when error type is `response`', () => {
    const error: FetchError = {
      _tag: 'response',
      message: 'foo',
      url: 'yandex.ru',
      status: 404
    };

    expect(formatFetchErrorMessage(error)).toBe('404 foo');
  });
});
