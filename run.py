from vboxapi import VirtualBoxManager

BASIC_SNAPSHOT = 'clear'
TARGET_NAME = 'ubuntu-server-1404'

vbm = VirtualBoxManager()
vbox = vbm.vbox
mach = vbox.findMachine(TARGET_NAME)

session = vbm.getSessionObject(vbox)
#progress = mach.launchVMProcess(session, "gui", "")
#progress.waitForCompletion(-1)

def wait(w):
    w.waitForCompletion(-1)


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

restore_basic_snap()
