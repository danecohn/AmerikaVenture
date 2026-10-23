# AltStack Venture

**AltStack LLC · An alternative stack for everyone.**


An AltStack LLC browser based on stable Firefox 158.0.1. Venture pairs a charcoal-and-crimson browser interface with a custom Amerika start page, its own compass emblem, and shortcuts to Amerika Social and AltOffice.

## Builds and source

This distribution rebuilds Firefox's packaged JavaScript/CSS/Fluent branding resources over **unmodified Mozilla stable engine binaries**. It does not claim to compile a new Gecko engine. The build checks the download against Mozilla’s published SHA512SUMS, replaces the browser’s visible branding, new-tab page and interface colors, adds Amerika distribution metadata and policies, and preserves Mozilla’s license notices. Windows executable icons/version resources and macOS bundle metadata are also replaced. The script and all modified resources are in this repository; the exact corresponding upstream source archive and repository are recorded in `upstream.json` and in each package’s `AMERIKA-SOURCE.json`.

The six download targets are Windows x64/ARM64, macOS Intel/Apple Silicon, and Linux x64/ARM64. macOS uses Mozilla’s universal engine package, labeled by the selected download target. Development packages are not commercially code-signed or notarized. The macOS package is ad-hoc signed locally by its build runner.

```sh
python scripts/build.py --target linux-arm64
```

Run on the target OS for Windows or macOS. Linux archives can be assembled for either CPU on Linux, but must be tested on the matching CPU. The scripts use only Python’s standard library; prebuilt original Amerika icons are versioned in `assets/`. Windows extraction needs 7-Zip; macOS uses hdiutil and codesign. Packages and SHA256 sidecars appear in `release/`.

On Linux extract the archive and run `./install-linux.sh` inside it. This installs for the current user under `~/.local/opt/amerika-venture` and adds an application launcher. Existing Firefox installations and profiles are separate.

## Updates

**Updates are manual in this first release.** Mozilla’s automatic application updater is disabled because it would replace the branded distribution. Install new Venture releases promptly when they include Firefox security updates. Each build pins an upstream version in `upstream.json`; maintainers must update it, review resource-layout changes, build and test all platforms, and publish the replacement packages. No background updater or automatic update guarantee is claimed.

Safe Browsing, site isolation, the content sandbox, TLS validation and ordinary Firefox security defaults are retained. Mozilla telemetry and studies are disabled by distribution policy. The start page has no analytics or browsing-history access; its clock runs locally. A submitted start-page search goes to DuckDuckGo, and app shortcuts open their named sites.

## Licensing

Modified browser resources and new code: MPL-2.0 (`LICENSE`). Bundled Firefox components retain their original licenses and notices. Firefox is a trademark of the Mozilla Foundation; Venture is a separately branded distribution by AltStack LLC, with no Mozilla endorsement claimed. Source: https://github.com/mozilla-firefox/firefox and the exact source archive in `upstream.json`.
