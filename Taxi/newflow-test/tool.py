import argparse
import getpass

from cargo_newflow import utils
from cargo_newflow import reporter as reporter_lib
from cargo_newflow.clients import cargo_claims, cargo_waybill


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--type', choices=('waybill', 'segment'), default='waybill',
    )
    parser.add_argument(
        '--segment', dest='type', action='store_const', const='segment',
    )
    parser.add_argument(
        '--waybill', dest='type', action='store_const', const='waybill',
    )
    parser.add_argument('object_id', help='Object id')
    args = parser.parse_args()

    reporter = reporter_lib.ConsoleReporter()
    username = getpass.getuser()
    net_address = utils.guess_address()
    claims_client = cargo_claims.CargoClaimsClient(user=username, net_address=net_address)
    waybill_client = cargo_waybill.CargoWaybillClient(user=username, net_address=net_address)

    if args.type == 'waybill':
        waybill_id = args.object_id
    elif args.type == 'segment':
        segment_id = args.object_id
        segment = waybill_client.segment_info(segment_id)
        reporter.section(f'trying to get waybill id from segment {segment_id}')
        waybill_id = (
            segment['dispatch'].get('chosen_waybill', {}).get('external_ref')
        )
        if waybill_id is None:
            raise RuntimeError(f'No waybill chosen for segment {segment_id}')
    else:
        raise RuntimeError(f'Unhandled cargo object type {args.type!r}')

    waybill = waybill_client.waybill_info(waybill_id)
    reporter.section(f'waybill {waybill_id}', doc=waybill)

    segment_ids = sorted(
        {item['segment_id'] for item in waybill['waybill']['points']},
    )
    claim_ids = set()
    for segment_id in segment_ids:
        segment = waybill_client.segment_info(segment_id)
        reporter.section(
            f'segment {segment_id} (cargo-dispatch view)', doc=segment,
        )

        segment = claims_client.get_segment_info(segment_id)
        reporter.section(
            f'segment {segment_id} (cargo-claimsview)', doc=segment,
        )
        claim_ids.add(segment['diagnostics']['claim_id'])

    for claim_id in sorted(claim_ids):
        claim = claims_client.get_claim_full(claim_id)
        reporter.section(f'claim {claim_id}', doc=claim)


if __name__ == '__main__':
    main()
