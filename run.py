import traceback
import argparse
import logging
import logging.handlers
import os
from platform import platform
from vboxapi import VirtualBoxManager
from time import sleep

log_path = os.path.dirname(os.path.abspath(__file__))
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'

logger = logging.getLogger("run_sh")

p = platform()

if 'Windows' in p:
    hdlr = logging.FileHandler(log_path + os.sep + 'run_test.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

elif 'Linux' in p:
    handler = logging.handlers.SysLogHandler(address='/var/log/syslog')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

#https://github.com/mjdorma/pyvbox/issues/35


def wait(w):
    w.waitForCompletion(-1)


def start(target, repo, report, branch):
    TARGET_NAME = target
    report_file = report
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    mach = vbox.findMachine(TARGET_NAME)
    session = vbm.getSessionObject(vbox)

    if mach:
        #mach.lockMachine(session, 1)
        if  mach.state == vbm.constants.MachineState_Running:
            logger.info("Machine already running")
        else:
            w = mach.launchVMProcess(session, "gui", "")
            w.waitForCompletion(-1)
            logger.info("Sleep 40 sec for the start VM ...")
            sleep(40)

        if session.state == vbm.constants.SessionState_Locked:
            logger.info("session loked, sessionPID: " + str(mach.sessionPID))
            session.unlockMachine()

        #session.unlockMachine()

        logger.info("cloning repo")
        clone_repo(session, mach, vbm, repo, branch)
        logger.info("Wait while repo cloning ...")
        sleep(10)
        logger.info("run test")
        logger.info("Wait while test not ended ...")
        run_test(session, mach, vbm, report_file, TARGET_NAME)
        logger.info("Done")
        return True


def stop(mgr, machine, session):
    mach = machine

    if session.state == mgr.constants.SessionState_Locked:
        logger.info("session loked, sessionPID: " + str(mach.sessionPID))
        session.unlockMachine()

    if mach:
        mach.lockMachine(session, 1)
        console = session.console
        # progress = console.restoreSnapshot(mach.currentSnapshot)
        progress = console.powerDown()
        progress.waitForCompletion(60)
        #session.unlockMachine()
        logger.info("Stop machine")
        sleep(5)
        return True


def restore_basic_snap(target):
    vbm = VirtualBoxManager()
    vbox = vbm.vbox
    machine = vbox.findMachine(target)
    session = vbm.openMachineSession(machine)
    stop(vbm, machine, session)

    if session.state == vbm.constants.SessionState_Locked:
        logger.info("session locked, sessionPID: " + str(machine.sessionPID))
        session.unlockMachine()

    machine.lockMachine(session, 1)
    m = session.machine
    if m:
        logger.info("Restore snapshot")
        w = m.restoreSnapshot(m.currentSnapshot)
        w.waitForCompletion(-1)
        session.unlockMachine()

        return True


def clone_repo(session , machine, mgr, repo, branch):

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
        #args = ["/usr/bin/git", "clone", "https://github.com/teror4uks/testtask.git" ,"/home/t4ks/testtask"] # first element WTF!!!!!!!
        #gp = gs.processCreate('/bin/ls', args, [], [vbm.constants.ProcessCreateFlag_WaitForStdOut], 0)
        args = ["/usr/bin/git", "clone", "-b", branch, repo, "/home/t4ks/testtask"]
        gp = gs.processCreate('/usr/bin/git', args, None, [vbm.constants.ProcessCreateFlag_WaitForStdOut , vbm.constants.ProcessCreateFlag_WaitForStdErr], t)

        try:
            gps = gs.processes
            for i in gps:
                gp_foo = i
                logger.info("Arguments: " + str(gp_foo.arguments))
                logger.info("Ex path: " + str(gp_foo.executablePath))
                logger.info("PID: " + str(gp_foo.PID))
                logger.info("Status: " + str(gp_foo.status))
        except:
            print traceback.format_exc()
            pass

        foo = []
        foo.append(vbm.constants.ProcessWaitForFlag_StdOut)
        foo.append(vbm.constants.ProcessCreateFlag_WaitForStdErr)

        waitResult = gp.waitForArray(foo, t)
        stdOut = gp.read(1, 10000, t)
        logger.info("stdOut: " + str(stdOut))
        stdErr = gp.read(2, 10000, t)
        logger.info("stdErr: " + str(stdErr))
        if waitResult == vbm.constants.ProcessWaitResult_StdOut:
            logger.info("Process Load finished")
        session.unlockMachine()
    except:
        print traceback.format_exc()



def run_test(session, machine, mgr, report_path, target):
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
            logger.info("stdOut: " + str(stdOut))
        except:
            print traceback.format_exc()

        try:
            stdErr = gp.read(2, 10000000, t)
            logger.info("stdErr: " + str(stdErr))
        except:
            logger.info(traceback.format_exc())

        logger.info("waitResult: " + str(waitResult))
        if waitResult == vbm.constants.ProcessWaitResult_StdOut:
            logger.info("Process Load finished")

        logger.info("Copy report in " + report_file)
        sleep(7)
        gs.fileCopyFromGuest("/home/t4ks/testtask/report.xml", report_file, [vbm.constants.FileCopyFlag_NoReplace])

        session.unlockMachine()

        logger.info("End test... ")
        restore_basic_snap(target)
    except:
        logger.info(traceback.format_exc())

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

    parser.usage = "--target <machine> --repo <git repo> [--branch] <default master> --dreport <absolute pasth for report file>"

    options = parser.parse_args()

    if options.target is None:
        logger.critical("add target")
        common_result += 1

    if options.repo is None:
        logger.critical('add repo')
        common_result += 1

    if options.report is None:
        logger.critical('add directory for report')
        common_result += 1

    print('Check input parameters - COMPLETED')

    if common_result == 0:
        try:
            start(options.target, options.repo, options.report, options.branch)
        except:
            print 'Not actual parametrs'

    return common_result

if __name__ == '__main__':
    #start()
    exit(cli())
