
import time
import traceback
from vboxapi import VirtualBoxManager

# https://github.com/mjdorma/pyvbox/issues/35

BASIC_SNAPSHOT = 'clear'
TARGET_NAME = 'ubuntu-server-1404'


def wait(w):
    w.waitForCompletion(-1)


def start():
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    mach = vbox.findMachine(TARGET_NAME)

    session = vbm.getSessionObject(vbox)
    if mach:
        #mach.lockMachine(session, 1)
        w = mach.launchVMProcess(session, "gui", "")
        w.waitForCompletion(-1)
        session.unlockMachine()
        return True


def stop():
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    mach = vbox.findMachine(TARGET_NAME)

    session = vbm.getSessionObject(vbox)
    if mach:
        mach.lockMachine(session, 1)
        console = session.console
        # progress = console.restoreSnapshot(mach.currentSnapshot)
        progress = console.powerDown()
        progress.waitForCompletion(60)
        session.unlockMachine()
        return True


def restore_basic_snap():
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    mach = vbox.findMachine(TARGET_NAME)
    session = vbm.openMachineSession(mach)

    mach = session.machine
    wait(mach.restoreSnapshot(mach.currentSnapshot))
    session.unlockMachine()

    return True


def run_test():
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    session = vbm.getSessionObject(vbox)
    mach = vbox.findMachine(TARGET_NAME)
    try:
        mach.lockMachine(session, 1)

        console = session.console

        guest = console.guest
        # gs = session.console.guest.createSession('t4ks', 'Qwerty123', '', '')

        t = 50 * 1000

        gs = guest.createSession('t4ks', 'Qwerty123', '', 'rungit')

        gs_state_result = gs.waitForArray([vbm.constants.GuestSessionWaitForFlag_Start], t)
        print gs_state_result

        #args = ["-l", "-a"]
        args = ["/usr/bin/git", "clone", "https://github.com/SurveyMonkey/pyteamcity" ,"/home/t4ks/pyteamcity"] # first element WTF!!!!!!!
        #gp = gs.processCreate('/bin/ls', args, [], [vbm.constants.ProcessCreateFlag_WaitForStdOut], 0)
        gp = gs.processCreate('/usr/bin/git', args, None, [vbm.constants.ProcessCreateFlag_WaitForStdOut , vbm.constants.ProcessCreateFlag_WaitForStdErr], t)
        gps = gs.processes

        for i in gps:
            gp_foo = i
            print "Arguments: ", gp_foo.arguments
            print "Ex path: ", gp_foo.executablePath
            print "PID: ", gp_foo.PID
            print "Status: " , gp_foo.status

        foo = []
        foo.append(vbm.constants.ProcessWaitForFlag_StdOut)
        foo.append(vbm.constants.ProcessCreateFlag_WaitForStdErr)

        waitResult = gp.waitForArray(foo, t)
        stdOut = gp.read(1, 10000, t)
        print "stdOut: ", stdOut
        stdErr = gp.read(2, 10000, t)
        print "stdErr: ", stdErr
        if waitResult == vbm.constants.ProcessWaitResult_StdOut:
            print "Process Load finished"

    except:
        print traceback.format_exc()

#start()
#stop()
run_test()
