import argparse
from typing import cast

from . import baseline
from ...settings import get_settings
from .common import initialize_plugin_settings


def add_scan_action(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = parent.add_parser(
        'scan',
        help='Creates a baseline by scanning a repository for secrets.',
        description=(
            'Scans a repository for secrets in code. The generated output is compatible with '
            '`detect-secrets-hook --baseline`.'
        ),
    )

    _add_adhoc_scanning(parser)
    _add_pragma_scanning(parser)
    _add_initialize_baseline_options(parser)

    return parser


def _add_adhoc_scanning(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--string',
        nargs='?',
        const=True,
        help=(
            'Scans an individual string, and displays configured plugins\' verdict.'
        ),
    )


def _add_pragma_scanning(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--only-allowlisted',
        action='store_true',
        help=(
            'Only scans the lines that are flagged with `allowlist secret`. This helps '
            'verify that individual exceptions are indeed non-secrets.'
        ),
    )


def _add_initialize_baseline_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'path',
        nargs='*',
        default='.',
        help=(
            'Scans the entire codebase and outputs a snapshot of '
            'currently identified secrets.'
        ),
    )

    group = parser.add_argument_group(title='scan options')
    group.add_argument(
        '--all-files',
        action='store_true',
        help='Scan all files recursively (as compared to only scanning git tracked files).',
    )
    baseline.add_baseline_option(
        cast(argparse.ArgumentParser, group),
        help='If provided, will update existing baseline by importing settings from it.',
    )
    group.add_argument(
        '--force-use-all-plugins',
        action='store_true',
        help=(
            'If a baseline is provided, detect-secrets will default to loading the plugins '
            'specified by that baseline. However, this may also mean it doesn\'t perform the '
            'scan with the latest plugins. If this flag is provided, it will always use the '
            'latest plugins'
        ),
    )
    group.add_argument(
        '--slim',
        action='store_true',
        help=(
            'Slim baselines are created with the intention of minimizing differences between '
            'commits. However, they are not compatible with the `audit` functionality, and '
            'slim baselines will need to be remade to be audited.'
        ),
    )


def parse_args(args: argparse.Namespace) -> None:
    if args.action != 'scan':
        return

    # NOTE: This is assumed to run *after* the baseline argument processor, and before
    # the plugin argument processor.
    if args.baseline is not None and args.force_use_all_plugins:
        get_settings().plugins.clear()
        initialize_plugin_settings(args)
