# clear-browser
A custom chromium build inspired by ungoogled-chromium but keep some Google services working.

Current version: `79.0.3945.8`.

Update **randomly**.

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

Tested on macOS 10.15. Building on Windows is WIP.

## macOS

1. Install `Xcode 10`. **Do not use Xcode 11 since Chromium does not support Xcode 11.**
2. Clone this project: `git clone https://github.com/hellotanuky/clear-browser
3. Open a terminal and cd to project folder: `cd clear-browser`
4. Build Chromium with patches: `./scripts/build.py build`
5. Wait patiently.

**Optionally:**  If you want to use ccache,
use `brew install ccache` to install it and pass `--ccache` to `build.py`. This will
automatically append `cc_wrapper="ccache"`to `args.gn`.

## Windows

_IT IS BUGGY_ and WIP.

## Ubuntu

Planned to test on Ubuntu 19.10 but I'm too lazy to do so.

# Known Issues

If you use existing profile from `ungoogled-chromium`, you may encounter password sync failure. To solve this, create a new profile.

`1Password` is unavailable since it forces browser signature check. Instead you can use
`1Password X` but it requires a valid subscription.

# Development

PRs are always welcome :)
