import click
from dataclasses import dataclass
from importlib import import_module
from functools import cached_property


@dataclass(frozen=True, slots=True)
class Actor:
    file: str
    table: str
    fields: list[str]
    records: list[dict[str, any]]


@dataclass(frozen=True, slots=True)
class Filter:
    """Defines criteria for filtering records."""

    field: str
    operator: str
    value: str

    def __str__(self) -> str:
        return f"{self.field} {self.operator} {self.value}"


class OrderCommands(click.Group):
    """Top-level command group for managing orders."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Returns a list of available subcommands in the declared order."""

        return self.commands


class LazyGroup(click.Group):
    """
    A resilient group that dynamically imports its subcommand implementation
    when needed. Ensures the CLI doesn't fail due to broken subcommands
    during startup.
    """

    def __init__(self, import_name: str, **kwargs: any) -> None:
        """Initializes the LazySubcommand with its import name."""

        self._import_name: str = import_name
        super().__init__(**kwargs)

    @cached_property
    def _impl(self) -> click.Group:
        """Lazily imports the subcommand implementation on first use."""

        module_name, subcommand_name = self._import_name.split(":", 1)
        return getattr(import_module(module_name), subcommand_name)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        return self._impl.get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> list[str]:
        return self._impl.list_commands(ctx)

    def invoke(self, ctx: click.Context) -> None:
        """Invokes the subcommand group itself for potential default actions."""

        return self._impl.invoke(ctx)

    def get_usage(self, ctx: click.Context) -> str:
        return self._impl.get_usage(ctx)

    def get_params(self, ctx: click.Context) -> list[click.Parameter]:
        return self._impl.get_params(ctx)
