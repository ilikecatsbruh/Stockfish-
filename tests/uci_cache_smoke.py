#!/usr/bin/env python3
"""Smoke-test that repeated searches in one UCI session remain usable.

The second search deliberately reuses the same position without Clear Hash or
ucinewgame, exercising Stockfish's persistent transposition table lifecycle.
"""
import subprocess
import sys
import time


def read_until(process, prefix, timeout=120):
    lines = []
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        line = process.stdout.readline()
        if not line:
            raise RuntimeError("engine exited before " + prefix)
        line = line.rstrip("\n")
        lines.append(line)
        if line.startswith(prefix):
            return lines
    raise TimeoutError("timed out waiting for " + prefix)


def main():
    engine = sys.argv[1] if len(sys.argv) > 1 else "./src/stockfish"
    process = subprocess.Popen(
        [engine], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    try:
        process.stdin.write("uci\n")
        process.stdin.flush()
        read_until(process, "uciok")
        process.stdin.write("isready\n")
        process.stdin.flush()
        read_until(process, "readyok")

        for search_number in (1, 2):
            process.stdin.write("position startpos\n")
            process.stdin.write("go depth 10\n")
            process.stdin.flush()
            output = read_until(process, "bestmove")
            bestmove = output[-1].split()
            if len(bestmove) < 2 or bestmove[1] == "(none)":
                raise RuntimeError(f"search {search_number} returned no move")
            print(f"search {search_number}: {bestmove[1]}")

        process.stdin.write("quit\n")
        process.stdin.flush()
        process.wait(timeout=10)
        print("Repeated-search UCI smoke test passed.")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
