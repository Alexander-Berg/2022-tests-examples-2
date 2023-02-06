import datetime
import json
import os
from typing import Optional

from sampling.pipeline import fixture_generator


class JsonlSampler:
    def __init__(
            self,
            sample_name: str,
            file_name: str,
            date: datetime.date,
            token_path: str,
            options: Optional[dict] = None,
    ):
        assert options
        self._template = options['template_name']
        self._output = options['file_name']
        self._samples = options['samples']

    async def sample_data(self) -> bool:
        template_file = open(self._template)
        input_data = '\n'.join(template_file.readlines())
        template_file.close()
        if os.path.exists(self._output):
            os.rename(self._output, self._output + '.bak')
        generator = iter(fixture_generator.fixture_pipeline(input_data))
        output = open(self._output, 'w+')
        for _ in range(self._samples):
            data = next(generator)
            print(data)
            output.write(json.dumps(data) + '\n')
        output.close()
        return True
