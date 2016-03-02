import ConfigParser

import clg
import os
import yaml

from cli import exceptions
from cli import utils


def load_config_file():
    """Load config file order(ENV, CWD, USER HOME, SYSTEM).

    :return ConfigParser: config object
    """

    # create a parser with default path to InfraRed's main dir
    cwd_path = os.path.join(os.getcwd(), utils.IR_CONF_FILE)
    _config = ConfigParser.ConfigParser()

    env_path = os.getenv(utils.ENV_VAR_NAME, None)
    if env_path is not None:
        env_path = os.path.expanduser(env_path)
        if os.path.isdir(env_path):
            env_path = os.path.join(env_path, utils.IR_CONF_FILE)

    for path in (env_path, cwd_path, utils.USER_PATH, utils.SYSTEM_PATH):
        if path is not None and os.path.exists(path):
            _config.read(path)
            return _config

    conf_file_paths = "\n".join([cwd_path, utils.USER_PATH, utils.SYSTEM_PATH])
    raise exceptions.IRFileNotFoundException(
        conf_file_paths,
        "IR configuration not found. "
        "Please set it in one of the following paths:\n")


class SpecManager(object):
    """
    Holds everything related to specs.
    """

    SPEC_EXTENSION = '.spec'

    @classmethod
    def parse_args(cls, module_name, config, args=None):
        """
        Looks for all the specs for specified module
        and parses the commandline input arguments accordingly.

        :param module_name: the module name: installer|provisioner|tester
        """
        cmd = clg.CommandLine(cls._get_specs(module_name, config))
        return cmd.parse(args)

    @classmethod
    def _get_specs(cls, module_name, config):
        """
        Gets specs files as a dict from settings/<module_name> folder.
        :param module_name: the module name: installer|provisioner|tester
        """
        res = {}
        for spec_file in cls._get_all_specs(config, subfolder=module_name):
            spec = yaml.load(open(spec_file))
            utils.dict_merge(res, spec)
        return res

    @classmethod
    def _get_all_specs(cls, config, subfolder=None):
        root_dir = utils.validate_settings_dir(
            config.get('defaults', 'settings'))
        if subfolder:
            root_dir = os.path.join(root_dir, subfolder)

        res = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in [f for f in filenames
                             if f.endswith(cls.SPEC_EXTENSION)]:
                res.append(os.path.join(dirpath, filename))

        return res


config = load_config_file()
