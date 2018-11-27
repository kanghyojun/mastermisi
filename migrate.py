#!/usr/bin/env python3
import pathlib
import typing

from alembic.config import CommandLine
from ormeasy.common import import_all_modules

from mastermisi.app import App
from mastermisi.orm import get_alembic_config


class Migrate(CommandLine):

    def main(self, argv: typing.Optional[typing.Sequence[str]] = None) -> None:
        options = self.parser.parse_args(argv)
        if not options.config:
            raise ValueError('--config MUST be required.')
        config_path = pathlib.Path(options.config)
        if not config_path.exists():
            raise ValueError('{!s} is inexist path.'.format(config_path))
        app_config = App.from_path(config_path)
        if not hasattr(options, "cmd"):
            self.parser.error("too few arguments")
        else:
            import_all_modules('mastermisi')
            self.run_cmd(get_alembic_config(app_config), options)


def main(argv=None, prog=None, **kwargs):
    Migrate(prog=prog).main(argv=argv)


if __name__ == '__main__':
    main()
