import { expect } from 'chai';
import { parseTkit } from '../lib/util';

describe('grep-task', () => {
    describe('parseTkit', () => {
        const lines = `
        2020-10-22T13:20:05.720Z stdout whatever
        2020-10-22T13:20:05.720Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:05.719Z	unixtime=1603372806	hostname=linux-ubuntu-16-04-xenial	message="'[copy-ether]: start at Thu Oct 22 2020 16:20:05 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:05.721Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:05.721Z	unixtime=1603372806	hostname=linux-ubuntu-16-04-xenial	message="'[copy-etherPerl]: start at Thu Oct 22 2020 16:20:05 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:25.180Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:25.180Z	unixtime=1603372825	hostname=linux-ubuntu-16-04-xenial	message="'[copy-ether]: end at Thu Oct 22 2020 16:20:25 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:25.181Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:25.180Z	unixtime=1603372825	hostname=linux-ubuntu-16-04-xenial	message="'[build-ether]: start at Thu Oct 22 2020 16:20:25 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:27.041Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:27.041Z	unixtime=1603372827	hostname=linux-ubuntu-16-04-xenial	message="'[copy-etherPerl]: end at Thu Oct 22 2020 16:20:27 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:27.041Z stdout tskv	ololoe="11"
        2020-10-22T13:20:27.041Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:27.041Z	unixtime=1603372827	hostname=linux-ubuntu-16-04-xenial	message="'[build-etherPerl]: start at Thu Oct 22 2020 16:20:27 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:35.049Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:35.049Z	unixtime=1603372835	hostname=linux-ubuntu-16-04-xenial	message="'[build-etherPerl]: end at Thu Oct 22 2020 16:20:35 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:35.049Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:35.049Z	unixtime=1603372835	hostname=linux-ubuntu-16-04-xenial	message="'[pack-PORTAL_ETHER_FRONT_TARBALL]: start at Thu Oct 22 2020 16:20:35 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:20:53.599Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:20:53.599Z	unixtime=1603372854	hostname=linux-ubuntu-16-04-xenial	message="'[pack-PORTAL_ETHER_FRONT_TARBALL]: end at Thu Oct 22 2020 16:20:53 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:25:58.919Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:25:58.918Z	unixtime=1603373159	hostname=linux-ubuntu-16-04-xenial	message="'[build-ether]: end at Thu Oct 22 2020 16:25:58 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:25:58.919Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:25:58.918Z	unixtime=1603373159	hostname=linux-ubuntu-16-04-xenial	message="'[s3-deploy-ether]: start at Thu Oct 22 2020 16:25:58 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:25:58.919Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:25:58.919Z	unixtime=1603373159	hostname=linux-ubuntu-16-04-xenial	message="'[pack-PORTAL_ETHER_TMPL_TARBALL]: start at Thu Oct 22 2020 16:25:58 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:26:17.458Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:26:17.456Z	unixtime=1603373177	hostname=linux-ubuntu-16-04-xenial	message="'[pack-PORTAL_ETHER_TMPL_TARBALL]: end at Thu Oct 22 2020 16:26:17 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:27:12.396Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:27:12.396Z	unixtime=1603373232	hostname=linux-ubuntu-16-04-xenial	message="'[s3-deploy-ether]: end at Thu Oct 22 2020 16:27:12 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:27:12.397Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:27:12.397Z	unixtime=1603373232	hostname=linux-ubuntu-16-04-xenial	message="'[nanny-deploy]: start at Thu Oct 22 2020 16:27:12 GMT+0300 (Moscow Standard Time)'"
        2020-10-22T13:27:18.302Z stdout tskv	tskv_format=graph	group=unknown	timestamp=2020-10-22T13:27:18.302Z	unixtime=1603373238	hostname=linux-ubuntu-16-04-xenial	message="'[nanny-deploy]: end at Thu Oct 22 2020 16:27:18 GMT+0300 (Moscow Standard Time)'"`;

        it('находит строки', () => {
            expect(parseTkit(lines.split('\n')))
                .to.deep.equal({
                    'build-ether': 333738,
                    'build-etherPerl': 8008,
                    'copy-ether': 19461,
                    'copy-etherPerl': 21320,
                    'nanny-deploy': 5905,
                    'pack-PORTAL_ETHER_FRONT_TARBALL': 18550,
                    'pack-PORTAL_ETHER_TMPL_TARBALL': 18537,
                    's3-deploy-ether': 73478,
                });
        });
    });
});
