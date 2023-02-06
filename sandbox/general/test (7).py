from __future__ import print_function
import os
import yatest.common as yc
from sandbox.projects.WizardRuntimeBuild.ya_make import YaMake


def test_default():
    outdir = yc.output_path('json')
    os.mkdir(outdir)
    for (dirpath, dirnames, filenames) in os.walk(yc.source_path('sandbox/projects/WizardRuntimeBuild/ya_make/ut')):
        for f in filenames:
            if not f.endswith('.yamake'):
                continue
            outfname = os.path.join(outdir, f + '.json')
            try:
                yamake = YaMake.YaMake()
                yamake.parse(os.path.join(dirpath, f))
                with open(outfname, 'w') as out:
                    yamake.dump(out)
            except ValueError as e:
                with open(outfname, 'w') as out:
                    print("{}\n\n{}".format(type(e), str(e)), file=out)

    return yc.canonical_dir(outdir)


def test_wizard_fresh():
    outdir = yc.output_path('fresh')
    os.mkdir(outdir)
    root = 'search/wizard/data/fresh'
    for (dirpath, dirnames, filenames) in os.walk(yc.source_path(root)):
        for f in filenames:
            if f == 'ya.make':
                yamake = YaMake.YaMake()
                yamake.parse(os.path.join(dirpath, f))  # validate we have no exceptions
