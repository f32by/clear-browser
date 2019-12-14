# clear-browser
A custom chromium build inspired by ungoogled-chromium but keep some Google services working.

Current version: `80.0.3987.7`.

Usually keep updated with latest **Dev** version.

# Features

> All patches are in `patches` folder.

Removed `Safe Browsing`.

Removed privacy tracker in Settings.

Changed UI default color (some modifications from Brave browser [here](https://github.com/brave/brave-core/blob/master/browser/themes/theme_properties.cc)).

Resized top chrome UI.


# Installation

Download binaries from [Releases](https://github.com/hellotanuky/clear-browser/Releases).

If you want to use Chrome Sync, you have to setup Google API key first. Please follow
[this link](https://www.chromium.org/developers/how-tos/api-keys) to get your own key.


# Build from sources

Tested on macOS 10.15.

## macOS

1. Install `Xcode 10` or higher version.
2. Clone this project: `git clone https://github.com/hellotanuky/clear-browser`
3. Open a terminal and cd to project folder: `cd clear-browser`
4. Build Chromium with patches: `./scripts/build.py build`
5. Wait patiently.

**Optionally:**  If you want to use ccache,
use `brew install ccache` to install it and pass `--ccache` to `build.py`. This will
automatically append `cc_wrapper="ccache"`to `args.gn`.

## Windows

_IT IS BUGGY_ and WIP.

## Ubuntu

still WIP.

# Known Issues

If you use existing profile from `ungoogled-chromium`, you may encounter password sync failure. To solve this, create a new profile.

`1Password` is unavailable since it forces browser signature check. Instead you can use
`1Password X` but it requires a valid subscription.

# Development

PRs are always welcome :)
