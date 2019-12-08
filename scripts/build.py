#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import logging
import argparse
import platform
import subprocess
import urllib.request
from zipfile import ZipFile

PLATFORM = platform.system()

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))
CHROMIUM_ROOT = os.path.join(PROJECT_ROOT, 'chromium')
CHROMIUM_SRC_ROOT = os.path.join(CHROMIUM_ROOT, 'src')
VERSION_FILE = os.path.join(PROJECT_ROOT, 'config',  'version.txt')
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'args.gn')
PATCH_ROOT = os.path.join(PROJECT_ROOT, 'patches')
PATCH_SERIES_FILE = os.path.join(PATCH_ROOT, 'series')

DEPOT_TOOLS_PATH = os.path.join(PROJECT_ROOT, 'depot_tools')

GIT_EXECUTABLE = 'git.exe' if PLATFORM == 'Windows' else 'git'

DEPOT_TOOLS_GIT_URL = 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
DEPOT_TOOLS_ZIP_URL = 'https://storage.googleapis.com/chrome-infra/depot_tools.zip'
DEPOT_TOOLS_ZIP_PATH = os.path.join(PROJECT_ROOT, 'depot_tools.zip')

WINDOWS_VS_VERSION = '2019'
CUSTOM_ENV = None


def prepare_env():
    global CUSTOM_ENV

    path_sep = ';' if PLATFORM == 'Windows' else ':'

    if not CUSTOM_ENV:
        CUSTOM_ENV = os.environ.copy()
        CUSTOM_ENV['PATH'] = DEPOT_TOOLS_PATH + path_sep + CUSTOM_ENV['PATH']

        if PLATFORM == 'Windows':
            # Apply GN env
            CUSTOM_ENV['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
            CUSTOM_ENV['GYP_MSVS_VERSION'] = WINDOWS_VS_VERSION


def run_command_in_path(cmd, cwd=None, with_env=False, ignore_error=False):
    if with_env:
        prepare_env()
        ret = subprocess.call(cmd, cwd=cwd, env=CUSTOM_ENV, shell=True)
    else:
        ret = subprocess.call(cmd, cwd=cwd)

    if ret != 0:
        print('Command failed: {}'.format(cmd))
        if not ignore_error:
          exit(1)

    return ret

def get_depot_tools():
    """
    Download depot_tools to project root.
    """
    if PLATFORM == 'Windows':
        # Download
        urllib.request.urlretrieve(
            DEPOT_TOOLS_ZIP_URL, DEPOT_TOOLS_ZIP_PATH)
        # Unzip
        print('Extracting depot_tools...')
        with ZipFile(DEPOT_TOOLS_ZIP_PATH, 'r') as zipObj:
            zipObj.extractall(DEPOT_TOOLS_PATH)
    else:
        run_command_in_path([GIT_EXECUTABLE, 'clone', DEPOT_TOOLS_GIT_URL],
                            PROJECT_ROOT)


def check_xcode():
    ret = subprocess.call(['xcodebuild', '-version'])
    return ret == 0


def check_prerequisites():
    print('Checking prerequisites...')

    if PLATFORM == 'Linux':
        # check git
        pass
    elif PLATFORM == 'Darwin':
        # check Xcode
        if not check_xcode():
            raise 'Xcode is not installed. Please install Xcode 10.3. Note: \
                   Don\'t install Xcode 11 since Chromium does not support \
                   build with Xcode 11.'

        # If Xcode is installed, apparently git is installed.
        #
        # check depot_tools
        if os.path.exists(os.path.join(DEPOT_TOOLS_PATH, 'fetch')):
            print('depot_tools already installed.')
        else:
            print('Downloading depot_tools...')
            # Download depot_tools
            get_depot_tools()

    elif PLATFORM == 'Windows':
        if os.path.exists(os.path.join(DEPOT_TOOLS_PATH, 'fetch')):
            print('depot_tools already installed.')
        else:
            # Download depot_tools
            print('Downloading depot_tools...')
            get_depot_tools()

            # Run gclient once to install all tools
            run_command_in_path(os.path.join(
                DEPOT_TOOLS_PATH, 'gclient'), with_env=True)

    else:
        raise 'Unsupported platform.'


def fetch():
    # fetch source
    print('Fetching sources. This may take hours to finish.')

    if not os.path.exists(CHROMIUM_ROOT):
        os.mkdir(CHROMIUM_ROOT)

    # run_command_in_path(['fetch', 'chromium'], CHROMIUM_ROOT, with_env=True)
    # sync
    print('Syncing dependencies...')
    run_command_in_path(['gclient', 'sync'], CHROMIUM_SRC_ROOT, with_env=True)


def apply_patches(args=None):
    f = open(PATCH_SERIES_FILE, 'r')
    series = f.readlines()
    f.close()

    more_args = []
    if args:
        if hasattr(args, 'reverse') and args.reverse:
            # reverse all patches
            series.reverse()
            more_args.append('-R')

        if hasattr(args, 'dry_run') and args.dry_run:
            more_args.append('--dry-run')

    # apply patches
    for patch in series:
        pathfile = os.path.join(PATCH_ROOT, patch.replace('\n', ''))
        if pathfile == '':
            continue
        cmd = ['patch', '-p1', '--no-backup-if-mismatch',
               '-i', pathfile,
               '-d', CHROMIUM_SRC_ROOT]

        cmd += more_args

        run_command_in_path(cmd, with_env=True)


def checkout_our_version():
    f = open(VERSION_FILE, 'r')
    version = f.readline()
    print('Checking out version ', version, ' ...')
    f.close()
    # checkout
    ret = run_command_in_path([GIT_EXECUTABLE, 'checkout', '-b',
                         'luc_mod', version], CHROMIUM_SRC_ROOT, ignore_error=True)

    if ret != 0:
      print('Our branch already exists, overwritting...')
      run_command_in_path([GIT_EXECUTABLE, 'reset', '--hard', version], CHROMIUM_SRC_ROOT)
    
    # gclient sync
    run_command_in_path(['gclient', 'sync'], CHROMIUM_SRC_ROOT, with_env=True)

def prepare_args_gn(no_jumbo=False, ccache=False):
    print('Copying args.gn')
    f = open(CONFIG_FILE, 'r')
    args_gn = f.read()
    f.close()

    if no_jumbo:
        print('Remove jumbo_build option')
        args_gn = args_gn.replace('use_jumbo_build = true', 'use_jumbo_build = false')

    if ccache:
        print('Add ccache option')
        args_gn += '\ncc_wrapper = "ccache"\n'

    out_dir = os.path.join(CHROMIUM_SRC_ROOT, 'out', 'Default')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # write args.gn
    with open(os.path.join(out_dir, 'args.gn'), 'w') as f:
        f.write(args_gn)


def prepare_build():
    # gn gen
    print('gn gen...')
    run_command_in_path(['gn', 'gen', os.path.join('out', 'Default')], CHROMIUM_SRC_ROOT)


def build(args):
    # build
    print('Start building...')
    run_command_in_path(
        ['autoninja', '-C', os.path.join('out', 'Default'), 'chrome'], CHROMIUM_SRC_ROOT)


def __debug():
    prepare_env()
    for k, v in CUSTOM_ENV.items():
        print(k, ': ', v)


def main():
    __debug()

    parser = argparse.ArgumentParser()
    # parser.add_argument('--fetch-source', help='Fetch Chromium sources from Google.')
    # parser.add_argument('--apply-patch', help='Apply patches.')

    subparsers = parser.add_subparsers(title='less-ungoogled-chromium build script',
                                       description='', dest='command')
    subparsers.add_parser('fetch')

    patch_parser = subparsers.add_parser('patch', help='Apply patches.')
    patch_parser.add_argument(
        '--without-ui', help='Do not apply UI-related patches in patches/ui.', action='store_true')
    patch_parser.add_argument(
        '--dry-run', help='Run patch with --dry-run.', action='store_true')
    patch_parser.add_argument(
        '--reverse', help='Reverse-apply patches.', action='store_true')

    build_parser = subparsers.add_parser('build')
    build_parser.add_argument(
        '--no-jumbo', help='Do not use jumbo build. This will speed up increment build.', action='store_true')
    build_parser.add_argument('--ccache', help='Use ccache to speed up increment build.', action='store_true')
    build_parser.add_argument(
        '--compile-only', help='Just build chromium without fetching any sources.', action='store_true')

    args = parser.parse_args()

    check_prerequisites()

    if args.command == 'fetch':
        fetch()
    elif args.command == 'patch':
        apply_patches(args)
    elif args.command == 'build':
        if not args.compile_only:
            fetch()
            checkout_our_version()
            apply_patches(args)
            prepare_args_gn(no_jumbo=args.no_jumbo, ccache=args.ccache)
            prepare_build()
        build(args)


if __name__ == '__main__':
    main()
