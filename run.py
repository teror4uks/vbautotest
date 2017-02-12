import time
from vboxapi import VirtualBoxManager, PlatformXPCOM
from vboxapi.VirtualBox_constants import VirtualBoxReflectionInfo


BASIC_SNAPSHOT = 'clear'
TARGET_NAME = 'ubuntu-server-1404'


vbm = VirtualBoxManager()
vbox = vbm.vbox
mach = vbox.findMachine(TARGET_NAME)
session = vbm.getSessionObject(vbox)


def wait(w):
    w.waitForCompletion(-1)


def start():
    if mach:
        # mach.lockMachine(session, 1)
        wait(mach.launchVMProcess(session, "gui", ""))
        session.unlockMachine()
        return True


def stop():
    if mach:
        mach.lockMachine(session, 1)
        console = session.console
        # progress = console.restoreSnapshot(mach.currentSnapshot)
        progress = console.powerDown()
        progress.waitForCompletion(60)
        session.unlockMachine()
        return True


def restore_basic_snap():
    mach = vbox.findMachine(TARGET_NAME)
    session = vbm.openMachineSession(mach)
    mach = session.machine
    wait(mach.restoreSnapshot(mach.currentSnapshot))
    session.unlockMachine()

    return True


def run_test():
    mach.lockMachine(session, 1)

    guest = session.console.guest
    # gs = session.console.guest.createSession('t4ks', 'Qwerty123', '', '')

    gs = guest.createSession('t4ks', 'Qwerty123', '', 'rungit')

    gs_state = gs.waitFor(vbm.constants.GuestSessionWaitForFlag_Start, 0)
    print gs_state

    args = ["-l", "-a"]
    gp = gs.processCreate('/bin/ls', args, [], [vbm.constants.ProcessCreateFlag_WaitForStdOut], 0)
    #args = ["clone", "https://github.com/teror4uks/testtask.git", "/home/t4ks/testtask"]
    #gp = gs.processCreate('/usr/bin/git', args, [], [vbm.constants.ProcessCreateFlag_WaitForStdOut,
    #                                                 vbm.constants.ProcessCreateFlag_WaitForStdErr], 0)

    gp_res = gp.waitFor(vbm.constants.ProcessWaitForFlag_StdOut, 10000)
    print gp_res

    # print gp.status
    out = gp.read(1, 100000, 10000)
    print out
    # gp.terminate()

    session.unlockMachine()



#start()
#stop()
run_test()
