import os

from .mode import LOCAL, Local
from .arg_parse import encode_args, ARGS_DATA
from .mount import MountLocal


def launch_shell(
    command,
    mode=LOCAL,
    dry=False,
    mount_points=None,
    ):
    if mount_points is None:
        mount_points = []
    mode.launch_command(command, dry=dry)


def launch_python(
        target,
        python_cmd='python',
        mode=LOCAL,
        mount_points=None,
        args=None,
        env=None,
        dry=False,
        fake_display=False,
        target_mount_dir='target',
        verbose=False,
        use_cloudpickle=False,
        target_mount=None,
):
    """

    :param target: Path to script to run.
    :param python_cmd:
    :param mode:
    :param mount_points:
    :param args:
    :param env:
    :param dry:
    :param fake_display:
    :param target_mount_dir:
    :param verbose:
    :param use_cloudpickle:
    :param target_mount: If set, ignore target and just use this as the target.
    :return:
    """
    if args is None:
        args = {}
    if mount_points is None:
        mount_points = []

    if target_mount is None:
        # mount
        target_dir = os.path.dirname(target)
        if not target_mount_dir:
            target_mount_dir = target_dir
        target_mount_dir = os.path.join(target_mount_dir, os.path.basename(target_dir))
        if isinstance(mode, Local):
            target_mount = MountLocal(local_dir=target_dir)
        else:
            target_mount = MountLocal(local_dir=target_dir, mount_point=target_mount_dir)
    mount_points = mount_points + [target_mount]
    target_full_path = os.path.join(target_mount.docker_mount_dir(), os.path.basename(target))

    command = make_python_command(
        target_full_path,
        args=args,
        python_cmd=python_cmd,
        fake_display=fake_display,
        use_cloudpickle=use_cloudpickle,
    )
    mode.launch_command(command, mount_points=mount_points, dry=dry, verbose=verbose)
    return target_mount

HEADLESS = 'xvfb-run -a -s "-ac -screen 0 1400x900x24 +extension RANDR"'
def make_python_command(
        target,
        python_cmd='python',
        args=None,
        fake_display=False,
        use_cloudpickle=False,
):

    if fake_display:
        cmd = '{headless} {python_cmd} {target}'.format(headless=HEADLESS, python_cmd=python_cmd, target=target)
    else:
        cmd = '%s %s' % (python_cmd, target)

    args_encoded = encode_args(args, cloudpickle=use_cloudpickle)
    if args:
        cmd = '%s=%s %s' % (ARGS_DATA, args_encoded, cmd)
    return cmd

