# -*- coding: utf-8 -*-
"""
Работа с процессами. Нужна для закрытия и проверки состояния процессов Chrome.
"""
import logging
import os
import signal
from time import sleep

import psutil

from chromoy.settings import (DEFAULT_PROCESSES_KILL_TIMEOUT,
                              MAX_ATTEMPTS_TO_CATCH_EXECUTED_PROCESS,
                              TIME_TO_WAIT_PROCESS_EXECUTION)

MAIN_LOGGER = logging.getLogger('main.log')


# check_processes
def check_pid_status(pid, is_raising_if_exists=False):
    MAIN_LOGGER.info('\n_________process [%d] ____________', pid)

    # check current process exists
    try:
        parent_process = psutil.Process(pid)
        MAIN_LOGGER.warning('Found process "%s" with %s status.',
                            parent_process.name(), parent_process.status())
        MAIN_LOGGER.info('Output connections:')
        for process in parent_process.connections():
            MAIN_LOGGER.warning(process)
    except psutil.NoSuchProcess:
        parent_process = None
        MAIN_LOGGER.info('No such PPID [%d]. All have been killed.', pid)

    # check children exist
    try:
        if not parent_process:
            raise psutil.NoSuchProcess(pid)
        MAIN_LOGGER.info('Output children:')
        child_processes = parent_process.children()
    except psutil.NoSuchProcess:
        child_processes = []

    for process in child_processes:
        MAIN_LOGGER.warning('Found process "%s" with %s status.', process.name(), process.status())
    else:
        MAIN_LOGGER.info('(!) No children from pid [%d]. All have been killed.', pid)

    if (child_processes or parent_process) and is_raising_if_exists:
        raise ProcessLookupError('Still have some children process')


def log_on_terminate(process):
    MAIN_LOGGER.info("process {} terminated".format(process.pid))


# kill_pid_tree
def kill_pid_tree(
        pid,
        sig=signal.SIGTERM, include_parent=True,
        timeout=DEFAULT_PROCESSES_KILL_TIMEOUT,
        on_terminate=log_on_terminate
):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a alive processes list.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    parent = None
    children = []

    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")

    # иногда процесс не испевает создаться, а его уже нужно кильнуть
    for attempt in range(MAX_ATTEMPTS_TO_CATCH_EXECUTED_PROCESS):
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            break
        except psutil.NoSuchProcess:

            MAIN_LOGGER.warning('Sleeping then trying to catch process PID {}'.format(pid))
            sleep(TIME_TO_WAIT_PROCESS_EXECUTION)

    if parent is None:
        MAIN_LOGGER.warning('Parent process PID {} is not exist'.format(pid))
        return

    if include_parent:
        children.append(parent)

    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            MAIN_LOGGER.warning('Child process PID %s is not exist', p.pid)

    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    if alive:
        # send SIGKILL
        for p in alive:
            MAIN_LOGGER.warning("process {} survived SIGTERM; trying SIGKILL" % p)
            p.kill()
        gone, alive = psutil.wait_procs(alive, timeout=timeout, callback=on_terminate)

        if alive:
            # give up
            for p in alive:
                MAIN_LOGGER.fatal("process {} survived SIGKILL; giving up" % p)

    return alive
