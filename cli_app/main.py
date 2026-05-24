"""Entrypoint for the CLI DB client."""
import asyncio


async def main():
    await run_repl()


async def run_repl():
    from cli.repl import repl_loop

    await repl_loop()


if __name__ == "__main__":
    asyncio.run(main())
