import argparse
import yt.wrapper as ytw
import datetime


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy', default='arnold')
    parser.add_argument('--sbr-logs', help='table with fresh sbr metric logs', default='//home/robot-metrics/sbr_fresh/sbr_fresh')
    parser.add_argument('--days', help='how many days will be used', default=30, type=int)
    args = parser.parse_args()
    return args


class FilterMap(object):
    def __init__(self, date_from):
        self.date_from = date_from

    def __call__(self, rec):
        if rec['judgements']['robot_coverage_web_fresh'] != 'OLD' and rec['date'] > self.date_from and rec['judgements']['light_relevance'] == 'RELEVANT':
            yield {
                'Url': rec['url'],
                'Status': rec['judgements']['robot_coverage_web_fresh']
            }


def main(args):
    ytw.config.set_proxy(args.proxy)

    date_from = (datetime.datetime.now() - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
    with ytw.TempTable() as tmp_table:
        ytw.run_map(FilterMap(date_from), args.sbr_logs, tmp_table)

        all_urls = set()
        crawled = set()

        for row in ytw.read_table(tmp_table):
            all_urls.add(row['Url'])
            if row['Status'] == 'CRAWLED':
                crawled.add(row['Url'])

        for url in all_urls:
            print '{}\tfresh:ru:1\t{:.8f}'.format(url, 1. / len(all_urls))

        for url in crawled:
            print '{}\tfresh_crawled:ru:1\t{:.8f}'.format(url, 1. / len(crawled))


if __name__ == '__main__':
    main(parse_args())
