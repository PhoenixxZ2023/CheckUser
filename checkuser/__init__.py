from checkuser.checker import check_user, kill_user
from checkuser.checker import CheckerUserManager

from checkuser.checker.ovpn import OpenVPNManager
from checkuser.checker.ssh import SSHManager

from checkuser.web import Server

from checkuser.utils import base_cli

__version__ = '2.2.6'
__author__ = 'Glemison C. Dutra'
__email__ = 'glemyson20@gmail.com'

base_cli.description = 'Checker for OpenVPN and SSH'
base_cli.prog = 'checker v' + __version__

base_cli.add_argument(
    '-v',
    '--version',
    action='version',
    version='%(prog)s',
)
