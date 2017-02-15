import traceback
import argparse
import os
import logging
from vboxapi import VirtualBoxManager
from time import sleep

# https://github.com/mjdorma/pyvbox/issues/35

def wait(w):
    w.waitForCompletion(-1)


def start():
    report_file = "D:\\testtask\\report.xml"
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    mach = vbox.findMachine(TARGET_NAME)
    session = vbm.getSessionObject(vbox)

    if mach:
        #mach.lockMachine(session, 1)
        w = mach.launchVMProcess(session, "gui", "")
        w.waitForCompletion(-1)
        state = mach.state
        print "State: " , state  #MachineState_
        session.unlockMachine()
        print "Sleep 40 sec for the start VM ..."
        sleep(40)
        print "cloning repo"
        clone_repo(session, mach, vbm)
        print "Wait while repo cloning ..."
        sleep(10)
        print "run test"
        print "Wait while test not ended ..."
        run_test(session, mach, vbm, report_file)
        print "Done"
        return True


def stop(mgr, machine, session):
    mach = machine

    if session.state == mgr.constants.SessionState_Locked:
        print "session loked, sessionPID: ", mach.sessionPID
        session.unlockMachine()

    if mach:
        mach.lockMachine(session, 1)
        console = session.console
        # progress = console.restoreSnapshot(mach.currentSnapshot)
        progress = console.powerDown()
        progress.waitForCompletion(60)
        #session.unlockMachine()
        print "Stop machine"
        sleep(5)
        return True


def restore_basic_snap():
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    machine = vbox.findMachine(TARGET_NAME)
    session = vbm.openMachineSession(machine)
    stop(vbm, machine, session)

    if session.state == vbm.constants.SessionState_Locked:
        print "session locked, sessionPID: ", machine.sessionPID
        session.unlockMachine()

    machine.lockMachine(session, 1)
    m = session.machine
    if m:
        print "Restore snapshot"
        w = m.restoreSnapshot(m.currentSnapshot)
        w.waitForCompletion(-1)
        session.unlockMachine()

        return True


def clone_repo(session , machine, mgr):

    vbm = mgr
    mach = machine
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
        args = ["/usr/bin/git", "clone", "https://github.com/teror4uks/testtask.git" ,"/home/t4ks/testtask"] # first element WTF!!!!!!!
        #gp = gs.processCreate('/bin/ls', args, [], [vbm.constants.ProcessCreateFlag_WaitForStdOut], 0)
        gp = gs.processCreate('/usr/bin/git', args, None, [vbm.constants.ProcessCreateFlag_WaitForStdOut , vbm.constants.ProcessCreateFlag_WaitForStdErr], t)

        try:
            gps = gs.processes
            for i in gps:
                gp_foo = i
                print "Arguments: ", gp_foo.arguments
                print "Ex path: ", gp_foo.executablePath
                print "PID: ", gp_foo.PID
                print "Status: ", gp_foo.status
        except:
            print traceback.format_exc()
            pass

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
        session.unlockMachine()
    except:
        print traceback.format_exc()



def run_test(session, machine, mgr, report_path):
    report_file = report_path
    mach = machine
    vbm = mgr
    #vbm = VirtualBoxManager()
    #vbox = vbm.vbox
    #session = vbm.getSessionObject(vbox)
    #mach = vbox.findMachine(TARGET_NAME)
    try:
        mach.lockMachine(session, 1)

        console = session.console

        guest = console.guest
        # gs = session.console.guest.createSession('t4ks', 'Qwerty123', '', '')

        t = 50 * 1000

        gs = guest.createSession('t4ks', 'Qwerty123', '', 'runtest')

        gs_state_result = gs.waitForArray([vbm.constants.GuestSessionWaitForFlag_Start], t)
        print gs_state_result

        args = []
        #gs.directoryOpen("/home/t4ks/testtask", '', [vbm.constants.DirectoryOpenFlag_None])
        #print "directories", gs.directories
        gp = gs.processCreate("/home/t4ks/testtask/run_test.sh", args, ["WORKING_DIR=/home/t4ks/testtask"], [vbm.constants.ProcessCreateFlag_WaitForStdOut , vbm.constants.ProcessCreateFlag_WaitForStdErr], t)

        try:
            gps = gs.processes
            for i in gps:
                gp_foo = i
                print "Arguments: ", gp_foo.arguments
                print "Ex path: ", gp_foo.executablePath
                print "PID: ", gp_foo.PID
                print "Status: ", gp_foo.status
        except:
            print traceback.format_exc()
            pass

        foo = []
        foo.append(vbm.constants.ProcessWaitForFlag_StdOut)
        foo.append(vbm.constants.ProcessCreateFlag_WaitForStdErr)

        waitResult = gp.waitForArray(foo, t)
        try:
            stdOut = gp.read(1, 10000000, t)
            print "stdOut: ", stdOut
        except:
            print traceback.format_exc()

        try:
            stdErr = gp.read(2, 10000000, t)
            print "stdErr: ", stdErr
        except:
            print traceback.format_exc()

        print "waitResult: ", waitResult
        if waitResult == vbm.constants.ProcessWaitResult_StdOut:
            print "Process Load finished"

        print "Copy report in ", report_file
        sleep(7)
        gs.fileCopyFromGuest("/home/t4ks/testtask/report.xml", report_file, [vbm.constants.FileCopyFlag_NoReplace])

        session.unlockMachine()

        print "End test... "
        restore_basic_snap()
    except:
        print traceback.format_exc()

    return 0



def cli():
    common_result = 0

    # --- Input parameters
    parser = argparse.ArgumentParser()


    parser.description = 'Script for start and run test in target machine'

    parser.add_argument('-t', '--target', dest='target', default=None,
                      help='target machine')

    parser.add_argument('-r', '--repo', dest='repo', default=None,
                      help='source repo')

    parser.add_argument('-b', '--branch', dest='branch', default='master',
                      help='branch in source repo')

    parser.add_argument('-d', '--dreport', dest='report', default=None,
                        help='directory for save report')

    (options, args) = parser.parse_args()

    if options.target is None:
        logging.critical("add target")
        common_result += 1

    if options.repo is None:
        logging.critical('add repo')
        common_result += 1

    if options.repo is None:
        logging.critical('add directory for report')
        common_result += 1


    print('Check input parameters - COMPLETED')

    if common_result == 0:
        try:
            (options.path, options.locale, options.destination)
        except Exception as e:
            print(e)

    return common_result

TARGET_NAME = 'ubuntu-server-1404'
BASIC_SNAPSHOT = 'clear'
REPO = ''
BRANCH = 'master'
REPORT_FOLDER = ''


if __name__ == '__main__':
    try:
        start()
    except:
        print traceback.format_exc()