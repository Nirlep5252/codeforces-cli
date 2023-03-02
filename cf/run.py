import click
import time
import os
import subprocess
from rich.console import Console
from utils import get_config
from typing import Optional, List, Union

console = Console()


def run_cmd(ext: str, file: str) -> Optional[Union[str, List[str]]]:
    is_linux = os.name == "posix"
    if ext == "py":
        return f"python3 {file}" if is_linux else f"py {file}"
    elif ext == "cpp":
        return [f"g++ {file}", ("./a.out" if is_linux else "a.exe")]
    elif ext == "c":
        return [f"gcc {file}", ("./a.out" if is_linux else "a.exe")]
    else:
        console.print("[bold red]ERROR: [/]The file extension is not supported.\n")


@click.command()
@click.argument("file", required=True)
def run(file: str):
    """
    Check the sample test cases for a problem.
    """
    slash = "/" if os.name == "posix" else "\\"

    data = get_config(console)
    if data is None:
        return

    cf_dir = data.get("dir")
    if cf_dir is None:
        console.print("[bold red]ERROR: [/]The default directory for parsing is not set.\nPlease run the `cf config` command.")
        return

    cf_dir = os.path.abspath(cf_dir)
    current_dir = os.getcwd()
    if not current_dir.startswith(cf_dir) and current_dir != cf_dir:
        console.print("[bold red]ERROR: [/]The current directory is not a contest directory.\n")
        return

    c_id = current_dir.split(slash)[-1]
    if not c_id.isdigit():
        console.print("[bold red]ERROR: [/]The current directory is not a contest directory.\n")
        return

    if not os.path.isfile(file):
        console.print("[bold red]ERROR: [/]The file does not exist.\n")
        return

    p_id = file.split(".")[0].lower()
    p_ext = file.split(".")[-1]

    all_inputs = sorted([f for f in os.listdir(current_dir) if f.endswith(".input.test") and f.startswith(p_id)])
    all_outputs = sorted([f for f in os.listdir(current_dir) if f.endswith(".output.test") and f.startswith(p_id)])

    total_passed = 0

    console.print(f"[bold blue]INFO: [/]Checking {len(all_inputs)} testcase(s)...\n")
    for i in range(len(all_inputs)):
        inp = all_inputs[i]
        out = all_outputs[i]

        cmd = run_cmd(p_ext, file)
        if cmd is None:
            return

        if type(cmd) == list:
            res = subprocess.run(cmd[0].split())
            if res.returncode != 0:
                console.print(f"[bold red]COMPILATION ERROR[/] ON TEST CASE {i + 1}\n")
                continue
            cmd = cmd[1]

        if type(cmd) == str:
            t1 = time.perf_counter() * 1000
            try:
                with open(inp) as f:
                    # BUG: for problems that have multiple inputs, this can confuse the user
                    # however, a good competitive programmar won't be confused by this :)
                    res = subprocess.run(cmd.split(), input=f.read().strip(), capture_output=True, text=True, timeout=10)  # type: ignore
            except subprocess.TimeoutExpired:
                console.print(f"[bold red]DEFAULT TIME LIMIT EXCEEDED (10 seconds)[/] ON TEST CASE {i + 1}\n")
                continue
            t2 = time.perf_counter() * 1000

            if res.returncode != 0:
                console.print(f"[bold red]RUNTIME ERROR[/] ON TEST CASE {i + 1}: {res.stderr}\n")
                continue

            with open(out) as f:
                if res.stdout.strip() == f.read().strip():
                    console.print(f"[bold green]PASSED[/] ON TEST CASE {i + 1}: {t2 - t1:.2f}ms\n")
                    total_passed += 1
                else:
                    console.print(f"[bold red]FAILED[/] ON TEST CASE {i + 1}\n")
                    console.print(f"\nYour Output:\n{res.stdout.strip()}\n\nExpected Output:\n{open(out).read().strip()}\n")

    console.print(f"[bold blue]INFO: [/]Passed {total_passed}/{len(all_inputs)} testcases.\n")
    if total_passed == len(all_inputs):
        console.print("[bold green]SUCCESS: [/]All testcases passed!\nYou can submit using the `cf submit` command.\n")
