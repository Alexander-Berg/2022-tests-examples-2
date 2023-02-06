# -*- coding: utf-8 -*-

import collections

from library.python.vault_client import VaultClient
from library.python.vault_client.utils import noneless_dict


class TestVaultClient(VaultClient):
    __test__ = False

    def switch(self, uids=None, abc_ids=None, staff_ids=None, return_raw=False):
        """Exchanges ids for real objects from cache.

        Args:
            uids: Passport UIDs
            abc_ids: ABC ids
            staff_ids: staff_ids
            return_raw: If set to True raw response will be returned instead of processed one

        Returns:
            Lists of objects with user names and IDs from Staff and ABC
            or raw response depending on return_raw parameter.

        Raises:
            ClientError: An error occurred doing request
        """
        url = self.host + '/switch/'
        if isinstance(uids, collections.Iterable):
            uids = ','.join(map(lambda x: str(x), uids or []))
        if isinstance(abc_ids, collections.Iterable):
            abc_ids = ','.join(map(lambda x: str(x), abc_ids or []))
        if isinstance(staff_ids, collections.Iterable):
            staff_ids = ','.join(map(lambda x: str(x), staff_ids or []))

        params = noneless_dict({
            'uids': uids,
            'abc_ids': abc_ids,
            'staff_ids': staff_ids,
        })

        r = self._call_native_client('get', url, params=params, skip_auth=True)
        if return_raw:
            return r  # pragma: no cover

        data = self.validate_response(r)
        return data

    def suggest(self, query, limit=None, return_raw=False):
        """Search objects by query.

        Args:
            query: Query
            return_raw: If set to True raw response will be returned instead of processed one

        Returns:
            Lists of objects from Staff and ABC
            or raw response depending on return_raw parameter.

        Raises:
            ClientError: An error occurred doing request
        """
        url = self.host + '/suggest/'

        params = noneless_dict({
            'query': query.encode('utf-8'),
            'limit': limit,
        })

        r = self._call_native_client('get', url, params=params, skip_auth=True)
        if return_raw:
            return r  # pragma: no cover

        data = self.validate_response(r)
        return data

    def suggest_tvm(self, query, abc_state=None, limit=None, return_raw=False):
        """Search objects by query.

        Args:
            query: Query
            abc_state: 'granted' or 'deprived'
            limit:
            return_raw: If set to True raw response will be returned instead of processed one

        Returns:
            Lists of TVM apps
            or raw response depending on return_raw parameter.

        Raises:
            ClientError: An error occurred doing request
        """
        url = self.host + '/suggest/tvm/'

        params = noneless_dict({
            'query': query.encode('utf-8'),
            'abc_state': abc_state,
            'limit': limit,
        })

        r = self._call_native_client('get', url, params=params, skip_auth=True)
        if return_raw:
            return r  # pragma: no cover

        data = self.validate_response(r)
        return data

    def get_tags(self, return_raw=False):
        """Get all tags for an user.

        Args:
            return_raw: If set to True raw response will be returned instead of processed one

        Returns:
            A list of tags or raw response depending on return_raw parameter.

        Raises:
            ClientError: An error occurred doing request
        """
        url = self.host + '/1/tags/'

        r = self._call_native_client('get', url)
        if return_raw:
            return r  # pragma: no cover

        data = self.validate_response(r)
        return data

    def suggest_tags(self, text, page=None, page_size=None, return_raw=False):
        """Find tags by text.

        Args:
            text: Query string
            page: Page number
            page_size: page size
            return_raw: If set to True raw response will be returned instead of processed one

        Returns:
            A list of tags or raw response depending on return_raw parameter.

        Raises:
            ClientError: An error occurred doing request
        """
        url = self.host + '/1/tags/suggest/'
        data = noneless_dict({
            'text': text,
            'page': page,
            'page_size': page_size,
        })

        r = self._call_native_client('get', url, data=data, skip_auth=True)
        if return_raw:
            return r  # pragma: no cover

        data = self.validate_response(r)
        return data['tags']

    def get_golovan_global_stats(self):
        """Get global metrics for a yasmagent

        Returns:
            A list of metrics

        Raises:
            ClientError: An error occurred doing request
        """
        r = self._call_native_client(
            'get',
            self.host + '/golovan/global/',
            skip_auth=True,
        )
        return r

    def get_tvm_grants(self):
        """Get tvm_grants

        Returns:
            A list of TVM Apps

        Raises:
            ClientError: An error occurred doing request
        """
        r = self._call_native_client(
            'get',
            self.host + '/grants/',
            skip_auth=True,
        )
        return r
