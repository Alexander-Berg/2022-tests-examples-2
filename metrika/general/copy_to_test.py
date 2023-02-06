import requests
import yt.wrapper as yt

yt_cluster = 'hahn'
yt_from_dir = '//home/radar_top_sites/production'
yt_to_dir = '//home/radar_top_sites/testing'

ch_url = 'http://localhost:25001'
ch_src_db = 'topsites'
ch_dst_db = 'topsites_test'
ch_table = 'topsites_segmentation_flat_d'

dry_run = True
force = False

yt_client = yt.YtClient(proxy=yt_cluster)

def ch_execute_query(query):
    response = requests.post(ch_url, data=query)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError(response.text)

def ch_key_exists(key):
    return len(ch_execute_query('select distinct Key from ' + ch_dst_db + '.' + ch_table + ' where Key = \'' + key + '\'').splitlines()) > 0

def ch_copy_snapshot(key):
    src_table = ch_src_db + '.' + ch_table
    dst_table = ch_dst_db + '.' + ch_table

    if not ch_key_exists(key):
        print 'ch copy key', key
        if not dry_run:
            ch_execute_query('insert into ' + dst_table + ' select * from ' + src_table + ' where Key = \'' + key + '\'')

def yt_copy_table(dir, table):
    from_path = yt_from_dir + '/' + dir + '/' + table
    to_path = yt_to_dir + '/' + dir + '/' + table

    if (not yt_client.exists(to_path)) or force:
        print 'yt copy from', from_path, 'to', to_path
        if not dry_run:
            yt_client.copy(from_path, to_path, force=force, recursive=True)

def copy_snapshot(snapshot, copy_ch):
    print 'copy snapshot', snapshot

    snapshot_path =yt_from_dir + '/report_snapshot/' + snapshot

    if copy_ch:
        ch_key = yt_client.get_attribute(snapshot_path, 'clickhouse_key')
        ch_copy_snapshot(ch_key)

    predicted_top_table_name = yt_client.get_attribute(snapshot_path, 'predicted_top_table_name')
    if predicted_top_table_name:
        yt_copy_table('predicted_top', predicted_top_table_name)
        yt_copy_table('optin_users', predicted_top_table_name)
        yt_copy_table('mob_optin_users', predicted_top_table_name)
        yt_copy_table('custom_optin_users', predicted_top_table_name)

    yt_copy_table('media_holdings_snapshot', snapshot)
    yt_copy_table('report_custom_coefficients', snapshot)
    yt_copy_table('segmentation_snapshot', snapshot)
    yt_copy_table('report_snapshot', snapshot)
    yt_copy_table('effective_marked_domains', snapshot)

def copy_snapshots():
    print 'copy snapshots'

    snapshots_dir = yt_from_dir + '/report_snapshot'
    snapshots = yt_client.list(snapshots_dir)

    for snapshot in snapshots:
        if (not yt_client.exists(yt_to_dir + '/report_snapshot/' + snapshot)) or force:
            try:
                status = yt_client.get_attribute(snapshots_dir + '/' + snapshot, 'snapshot_status')
            except yt.errors.YtHttpResponseError:
                status = 'UNKNOWN'

            if status == 'READY':
                copy_snapshot(snapshot, True)
            elif status == 'PREPARED':
                copy_snapshot(snapshot, False)

def yt_copy_dir(dir):
    print 'yt copy dir', dir

    from_subdir = yt_from_dir + dir
    to_subdir = yt_to_dir + dir

    tables = yt_client.list(from_subdir)

    for table in tables:
        from_path = from_subdir + '/' + table
        to_path = to_subdir + '/' + table

        if (not yt_client.exists(to_path)) or force:
            print 'yt copy from', from_path, 'to', to_path
            if not dry_run:
                yt_client.copy(from_path, to_path, force=force, recursive=True)

# data for api
copy_snapshots()

# data for calc
yt_copy_dir('/domain_markup/marked_domains')
yt_copy_dir('/titles/titles')
yt_copy_dir('/visible_thematics')
yt_copy_dir('/top_coefs_base')
yt_copy_dir('/top_crypta_coefs')

print 'end'
