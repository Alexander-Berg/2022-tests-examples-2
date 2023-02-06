import pathlib
from typing import List

import jinja2


class BaseError(Exception):
    pass


class AlreadyExistError(BaseError):
    pass


class UnknownTemplateError(BaseError):
    pass


class EmptyInputError(BaseError):
    pass


class CaseGenerator:
    """
    Copies files from templates folder to cases folder.
    If template file has ".j2" extension
      then it renders this file using jinja2.
    """

    SIMULATOR_DIR = pathlib.Path(__file__).parent.parent.parent

    TEMPLATES_DIR = SIMULATOR_DIR / 'templates'
    CASES_DIR = SIMULATOR_DIR / 'cases'

    JINJA_EXT = '.j2'

    def __init__(self):
        self.available_templates: List[pathlib.Path] = [
            p for p in pathlib.Path(self.TEMPLATES_DIR).iterdir() if p.is_dir()
        ]
        self.renderer: jinja2.Environment = self._get_renderer()

    def _get_renderer(self) -> jinja2.Environment:
        renderer = jinja2.Environment(
            trim_blocks=True,
            keep_trailing_newline=True,
            loader=jinja2.FileSystemLoader(str(self.TEMPLATES_DIR)),
            undefined=jinja2.StrictUndefined,
            extensions=['jinja2.ext.loopcontrols'],
        )

        return renderer

    def _validate(self, case_name: str, template: str):
        if not case_name:
            raise EmptyInputError('case-name parameter is empty')

        if (self.CASES_DIR / case_name).exists():
            raise AlreadyExistError(
                f'Case {case_name} already exists in folder {self.CASES_DIR}',
            )

        if not template:
            raise EmptyInputError('template parameter is empty')

        if not (self.TEMPLATES_DIR / template).exists():
            raise UnknownTemplateError(
                f'Template {template} was not found'
                ' in folder {self.TEMPLATES_DIR}',
            )

    def _render(
            self,
            case_dir: pathlib.Path,
            template: str = 'default',
            **jinja_kwargs,
    ):
        template_dir = self.TEMPLATES_DIR / template

        for filename in template_dir.glob('**/*'):
            if filename.is_dir():
                continue

            case_file = case_dir / filename.relative_to(template_dir)
            print(f'Generating {case_file}...')

            case_file.parent.mkdir(parents=True, exist_ok=True)

            if filename.suffix == self.JINJA_EXT:
                case_file = case_file.with_suffix('')
                self.renderer.get_template(
                    str(filename.relative_to(self.TEMPLATES_DIR)),
                ).stream(**jinja_kwargs).dump(str(case_file))
            else:
                case_file.write_text(filename.read_text())

            print(f'File {case_file} was created')

    def generate(self, case_name: str, template: str = 'default'):
        print(f'Creating case "{case_name}" from "{template}"')

        # validate input
        self._validate(case_name=case_name, template=template)

        # create case directory
        case_dir = self.CASES_DIR / case_name
        pathlib.Path.mkdir(case_dir, exist_ok=False)

        # render template
        self._render(case_dir=case_dir, template=template, case_name=case_name)
