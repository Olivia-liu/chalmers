"""
Install a crontab rule to run at system boot

E.g.::
    
    @reboot /path/to/python /path/to/chalmers start -a
    
FIXME: There may be cases where the reboot command does not work 
correctly.
 
 * http://unix.stackexchange.com/questions/109804/crontabs-reboot-only-works-for-root
 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import Popen, check_output, CalledProcessError, PIPE
import sys

from chalmers import errors
import os


python_exe = sys.executable
chalmers_script = sys.argv[0]
chalmers_tab_entry = '@reboot %s %s start -a' % (python_exe, chalmers_script)

log = logging.getLogger('chalmers.reboot')

def get_crontab():
    try:
        output = check_output(['crontab', '-l']).strip()
    except CalledProcessError as err:
        if err.returncode != 1:
            raise errors.ChalmersError("Could not read crontab")
        return []

    return output.split('\n')

def set_crontab(tab):

    new_cron_tab = '\n'.join(tab) + '\n'

    p0 = Popen(['crontab'], stdin=PIPE)
    p0.communicate(input=new_cron_tab)

class CronService(object):
    """
    Install a @reboot insruction to the user's local cron table
    """

    def __init__(self, target_user):
        if target_user is not False:
            msg = ("Not implemented: chalmers can not detect "
                   "the init system for your unix machine "
                   "(upstart, systemd or sysv)")
            raise errors.ChalmersError(msg)
        self.target_user = target_user

    @classmethod
    def use_if_not_root(cls, subcls, target_user):
        if target_user is False:
            return object.__new__(cls, target_user)
        else:
            if os.getuid() != 0:
                raise errors.ChalmersError("You can not install a posix service for "
                                           "user %s without root privileges. "
                                           "Run this command again with sudo")
            return object.__new__(subcls, target_user)

    def install(self):
        tab_lines = get_crontab()

        if chalmers_tab_entry in tab_lines:
            log.info("Chalmers crontab instruction already exists")
        else:
            log.info("Adding chalmers instruction to crontab")
            tab_lines.append(chalmers_tab_entry)

            set_crontab(tab_lines)

            log.info("All chalmers programs will now run on boot")


    def uninstall(self):

        tab_lines = get_crontab()

        if chalmers_tab_entry in tab_lines:
            log.info("Removing chalmers instruction from crontab")
            tab_lines.remove(chalmers_tab_entry)

            set_crontab(tab_lines)

        else:
            log.info("Chalmers crontab instruction does not exist")

    def status(self):

        tab_lines = get_crontab()

        if chalmers_tab_entry in tab_lines:
            log.info("Chalmers is setup to start on boot")
        else:
            log.info("Chalmers will not start on boot")

