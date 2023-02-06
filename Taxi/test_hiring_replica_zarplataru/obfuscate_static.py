#!python

"""Obfuscate static, replace phones and personal info from apps."""

import argparse
import json
import random
import uuid


def main(argv=None):
    args = _parse_args(argv)
    for filename in args.filenames:
        with open(filename) as fileobj:
            data = json.load(fileobj)
        print(filename)
        _obfuscate(data)
        pretty = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        if not args.run:  # --dry-run
            print(pretty)
        else:
            with open(filename, 'w') as fileobj:
                print(pretty, file=fileobj)


def _parse_args(argv):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('filenames', metavar='static.json', nargs='+')
    args = parser.parse_args(argv)
    return args


def _obfuscate(data):
    for resume in data['resumes']:
        _replace_names(resume)
        _replace_emails(resume)
        _replace_phones(resume)
        _replace_pictures(resume)


def _replace_names(resume):
    if resume['contact'].get('name'):
        resume['contact']['name'] = 'Ivan Ivanov Ivanovich'
    if resume['contact'].get('firstname'):
        resume['contact']['firstname'] = 'Ivan'
    if resume['contact'].get('lastname'):
        resume['contact']['lastname'] = 'Ivanov'
    if resume['contact'].get('patronymic'):
        resume['contact']['patronymic'] = 'Ivanovich'


def _replace_emails(resume):
    randint = random.randrange(10 ** 6)
    if resume['contact'].get('email'):
        resume['contact']['email'] = 'example%s@yandex.ru' % randint


def _replace_phones(resume):
    randint = random.randrange(10 ** 6)
    for obj in resume['contact'].get('phones', []):
        obj['phone'] = '+7 (%03d) %03d-%02d-%02d' % (
            random.randrange(1, 10 ** 3 + 1),
            random.randrange(1, 10 ** 3 + 1),
            random.randrange(1, 10 ** 2 + 1),
            random.randrange(1, 10 ** 2 + 1),
        )
        resume['contact']['email'] = 'example%s@yandex.ru' % randint


def _replace_pictures(resume):
    if resume.get('photo', {}).get('url'):
        resume['photo']['url'] = (
            'https://cdn.zp.ru/job/attaches/2019/06/64/cb/%s.jpg'
            % uuid.uuid4().hex
        )


if __name__ == '__main__':
    main()
