import subprocess
import threading
import sys
from typing import Tuple

def run_live(cmd: list[str]) -> Tuple[int, str, str]:
    """
    Run subprocess and stream stdout/stderr live to the terminal while
    capturing outputs. Returns (returncode, stdout_str, stderr_str).
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    out_lines: list[str] = []
    err_lines: list[str] = []

    def _reader(stream, collector, out_file):
        try:
            for line in iter(stream.readline, ''):
                if line == '':
                    break
                collector.append(line)
                out_file.write(line)
                out_file.flush()
        finally:
            try:
                stream.close()
            except Exception:
                pass

    t_out = threading.Thread(target=_reader, args=(proc.stdout, out_lines, sys.stdout), daemon=True)
    t_err = threading.Thread(target=_reader, args=(proc.stderr, err_lines, sys.stderr), daemon=True)
    t_out.start()
    t_err.start()

    rc = proc.wait()

    t_out.join()
    t_err.join()

    return rc, "".join(out_lines).rstrip("\n"), "".join(err_lines).rstrip("\n")