import dataclasses
import difflib
import filecmp
import os

import pytest


@dataclasses.dataclass
class Comparison:
    errors: list = dataclasses.field(default_factory=list)
    diffs: list = dataclasses.field(default_factory=list)

    def make_report(self):
        msg = []
        if self.errors:
            msg.append('Errors:')
            msg.extend(self.errors)
        if self.diffs:
            msg.append('Diffs:')
            msg.extend(self.diffs)
        return '\n'.join(msg)

    def is_ok(self):
        return not self.errors and not self.diffs


@pytest.fixture
def compare_with_reference():
    def compare(refs_path, name, path):
        comparison = Comparison()
        this_ref_path = os.path.join(refs_path, name)
        for dirpath, _, filenames in os.walk(this_ref_path):
            if not filenames:
                continue
            rel_path = dirpath.split(this_ref_path)[-1].lstrip('/')
            gen_path = os.path.join(path, rel_path)
            _, mismatch, errors = filecmp.cmpfiles(
                dirpath, gen_path, filenames, shallow=False,
            )

            if errors:
                # pylint: disable=no-member
                comparison.errors.extend(
                    os.path.join(rel_path, filename) for filename in errors
                )

            if not mismatch:
                continue

            for filename in mismatch:
                reference_path = os.path.join(dirpath, filename)
                with open(reference_path, encoding='utf-8') as fin:
                    ref = fin.readlines()

                generate_path = os.path.join(gen_path, filename)
                with open(generate_path, encoding='utf-8') as fin:
                    gen = fin.readlines()
                filepath = os.path.join(rel_path, filename)
                # pylint: disable=no-member
                comparison.diffs.append(
                    '\n'.join(
                        list(
                            difflib.context_diff(
                                ref,
                                gen,
                                fromfile=os.path.join('ref', filepath),
                                tofile=os.path.join('gen', filepath),
                            ),
                        ),
                    ),
                )

        return comparison

    return compare
