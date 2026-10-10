import os

from mindas_terminal import tasks


def P(pid, ppid=1, name="x", cpu=0.0, rss=0, cmd="", user="u", gpu=0):
    return tasks.Proc(pid, ppid, name, user, cpu, 0.0, rss, 1, "running", cmd or name, gpu)


PROCS = [P(10, 1, "bash", 1.0, 100), P(11, 10, "python", 90.0, 5000, "python train.py", gpu=4000),
         P(12, 11, "nvcc", 5.0, 300), P(20, 1, "sshd", 0.1, 50)]


def test_sort_and_filter():
    assert [p.pid for p in tasks.arrange(PROCS, "cpu")] == [11, 12, 10, 20]
    assert [p.pid for p in tasks.arrange(PROCS, "name", reverse=False)][0] == 10
    assert [p.pid for p in tasks.arrange(PROCS, query="train")] == [11]
    assert [p.pid for p in tasks.arrange(PROCS, "gpu")][0] == 11


def test_descendants_of_terminal_shells():
    assert tasks.descendants(PROCS, {10}) == {10, 11, 12}


def test_protected_processes():
    assert tasks.protected(os.getpid())
    assert tasks.protected(1)
    assert tasks.protected(999999) is None
    assert tasks.end(os.getpid()).startswith("refused")


def test_collect_sees_this_process():
    assert any(p.pid == os.getpid() for p in tasks.collect())


def test_total_cpu_is_bounded():
    assert tasks.total_cpu(PROCS, 4) == (1.0 + 90.0 + 5.0 + 0.1) / 4
    assert tasks.total_cpu([P(1, cpu=900.0)], 4) == 100.0


def test_human():
    assert tasks.human(512) == "512B"
    assert tasks.human(3 * 1024**3) == "3.0G"
