# ishtar on AOSPA beryl — local manifests

Local manifests for building AOSPA `beryl` (Android 16) for the Xiaomi 13 Ultra
(`ishtar`) on a rented build server. Planning, decisions and evidence live in the
workspace repository `ahmetxa/ishtar` (ledger `DEC-22`, `DEC-24`, `DEC-25`,
`IMPL-90`, `IMPL-91`; Main-Planing Phase 7).

**Status: ready for a first build attempt, not yet built (2026-09-11).** Every
project below resolves, and every former open item is either closed with a
source or deferred with a named build-time detector and a fallback.

## How this file works with AOSPA's own dependency list

AOSPA's `lunch` runs `vendor/aospa/build/tools/barista.py`, which reads
`vendor/aospa/products/ishtar/beans.xml` (plus `products/platforms/kalama.xml`
and `kalama-kernel.xml`) and writes the 67 projects it names into
`.repo/local_manifests/baristablend.xml`, then syncs them. On `beryl` those beans
still point `ishtar` at `vauxite` (Android 15) branches.

Local manifests load in alphabetical order, so `ishtar-beryl.xml` loads after
`baristablend.xml`. For each project it replaces, it first drops barista's
entry with `<remove-project path="..." optional="true">` (optional, because
`baristablend.xml` does not exist yet at the first `repo sync`) and then pins
the `beryl`-era source at the same path, keeping the beans' `linkfile`s. The
other 54 beans projects come from barista unchanged; `repo manifest -r` after
the build records the commits they resolved to.

## Base

`repo init -u https://github.com/AOSPA/manifest -b beryl`, verified at
`7dfc0650e27ec43b1d5cedf5e74213cf8667f2c2` (2026-05-24). Beans read from
`AOSPA/android_vendor_aospa` `beryl` at `6133f29c0f99e2587fe188eb6909596d6f813b7b`.

## Pinned projects (resolved 2026-09-11)

| Path | Repository | Branch | Commit | Replaces beans entry |
|---|---|---|---|---|
| `device/xiaomi/ishtar` | `ahmetxa/android_device_xiaomi_ishtar` | `beryl` | `d48816fb14984939f7152106f5352536619999b2` | `AOSPA/android_device_xiaomi_ishtar` `vauxite` |
| `device/xiaomi/sm8550-common` | `xiaomi-8550/android_device_xiaomi_sm8550-common` | `beryl` | `a0a7042263ff429afce199a945e50a9279f19822` | `AOSPA/…sm8550-common` `vauxite` |
| `hardware/xiaomi` | `AOSPA/android_hardware_xiaomi` | `beryl` | `1a3e75d36079e8ba9d1b324acdf5201157a307a6` | same repository, `vauxite` |
| `device/xiaomi/sepolicy` | `AOSPA/android_device_xiaomi_sepolicy` | `beryl` | `8dcddf5ef0402c373431696e4589c59d55a51740` | same repository, `vauxite` |
| `kernel_platform/msm-kernel` | `xiaomi-8550/android_kernel_xiaomi_sm8550` | `beryl` | `1c509b39a15692c9cfadbdd0d9154cc52f068254` | `AOSPA/android_kernel_xiaomi_sm8550` `vauxite` |
| `kernel_platform/common` | `xiaomi-8550/android_kernel_qcom_sm8550` | `beryl` | `b11e56025b7f8ae115189d38afcc85d16d84aac6` | `AOSPA/android_kernel_qcom_sm8550` `vauxite` |
| `vendor/qcom/opensource/display-drivers` | `xiaomi-8550/vendor_qcom_opensource_display-drivers` | `xiaomi-8550` | `c9c51bab11e6855adddb83b19e649b42396494d5` | `AOSPA/…display-drivers` `xiaomi-8550` |
| `hardware/qcom/display` | `xiaomi-8550/android_hardware_qcom_display` | `beryl-8550` | `bd3c17848e939d99707f5bfd2b7b6dcd1fb08863` | `AOSPA/…display` `vauxite-8550` |
| `vendor/qcom/opensource/audio-hal/primary-hal` | `xiaomi-8550/android_hardware_qcom_audio` | `beryl-8550` | `7c4ef02ccfe63f3288ce4701736c27fac40f4a3b` | `AOSPA/…audio` `vauxite-8550` |
| `vendor/qcom/opensource/pal` | `xiaomi-8550/android_vendor_qcom_opensource_arpal-lx` | `beryl-8550` | `5b305caa5cea49a73fe99c3fc11ea44b7a39a5b3` | `AOSPA/…arpal-lx` `vauxite-8550` |
| `vendor/xiaomi/ishtar` | `xiaomi-8550/proprietary_vendor_xiaomi_ishtar` | `beryl` | `f92e7a907d4e46f65f2ffca2efc24f227e07a28a` | `ThankYouMario/…ishtar` `vauxite` |
| `vendor/xiaomi/sm8550-common` | `xiaomi-8550/proprietary_vendor_xiaomi_sm8550-common` | `beryl` | `e0d20e8f29042e07ab778accab444bbbd4fb6040` | `ThankYouMario/…sm8550-common` `vauxite` |
| `vendor/xiaomi/camera` | `gitlab.com/ThankYouMario/proprietary_vendor_xiaomi_camera` | `beryl-sm8550-leica` | `b87ebc1c170da580945640015efd1ebe3f0f3999` | same repository, `vauxite-sm8550-leica` |

The trees' blob lists name their source firmware: `OS2.0.101.0.VMAMIXM` for
`ishtar`, `OS2.0.100.0.VMCMIXM` (from `fuxi`) for the common tree.

## Former open items

1. **`hardware/xiaomi` — closed.** `xiaomi-8550/android_hardware_xiaomi` has no
   `beryl` branch, but `AOSPA/android_hardware_xiaomi` does (tip `1a3e75d`,
   2026-05-11). Detector: a Soong error under `hardware/xiaomi` or a missing
   `xiaomifingerprint_headers`. Fallback: the beans' `vauxite` (delete the two
   lines).
2. **`device/xiaomi/sepolicy` — closed.** `AOSPA/android_device_xiaomi_sepolicy`
   has `beryl`, at the same commit as `vauxite` (`8dcddf5`). Detector: a policy
   compile or `neverallow` failure. Fallback: none needed from the manifest;
   the failure is a device-tree fix.
3. **Kernel — closed; one project deferred.** The kernel is built from source:
   `sm8550-common` `e20b4dc` and `ishtar` `daef185` switched to inline
   `kernel_platform` building, and `rom-build.sh` runs
   `kernel_platform/build/android/prepare_vendor.sh` when `kernel_platform/`
   exists. The beans place the trees at `kernel_platform/msm-kernel` (Xiaomi
   kernel) and `kernel_platform/common` (QCOM kernel); both are pinned to their
   `beryl` tips above. The technology-pack drivers and devicetrees come from
   the beans: their AOSPA commits equal `xiaomi-8550`'s (camera-kernel,
   audio-kernel, mmrm, nfc, the four devicetrees) or contain them
   (touch-drivers), and `kernel_platform/build/kernel` `kailua` `6b67ab4`
   equals `xiaomi-8550`'s last commit before the `beryl` common-tree tip.
   **Deferred:** `display-drivers` has diverged between the two organisations,
   so it is pinned to `xiaomi-8550`'s last commit on or before 2026-05-13 (the
   `beryl` common-tree tip). Detector: a compile or `modpost` failure in
   `vendor/qcom/opensource/display-drivers` during the kernel stage. Fallback:
   the beans' AOSPA commit `09008c5afe3e039f3a0a45ee9bb895d991e4e52a` (delete
   the two lines).
4. **QCOM overrides — closed for display and audio; gps and media deferred.**
   `xiaomi-8550`'s `beryl-8550` branches (2025-09-03,
   `DISPLAY.LA.3.0.r1-13400` and `AUDIO.LA.8.0.r1-12500`) replace AOSPA's
   `vauxite-8550` (2024-07-17, 2025-02-27, 2024-03-31) at the beans' paths.
   **Deferred:** `hardware/qcom/gps` and `hardware/qcom/media` have no
   `beryl-8550` branch in either organisation, so the beans' `vauxite-8550`
   stays. Detector: a compile error under either path. Fallback: none staged;
   the build's stopping rule applies and the error is a replanning input.
5. **`vendor/xiaomi/camera` — closed.** It is not optional in practice: the
   beans sync it from `gitlab.com/ThankYouMario` whether or not
   `inherit-product-if-exists` would skip it. The empty repository is
   `xiaomi-8550`'s; the one the beans use is public and has
   `beryl-sm8550-leica` (`b87ebc1`, 2025-11-13), pinned above. Detector: a
   sync failure on that path. Fallback: the beans' `vauxite-sm8550-leica`
   (delete the two lines).
6. **Server distribution — closed.** Ubuntu 22.04 LTS on a Hetzner CCX53
   (`DEC-22`, `DEC-25`). AOSP requires a 64-bit Linux with glibc 2.17 or later
   and Ubuntu 18.04 or later for Android 11+, 64 GB RAM and 400 GB disk;
   Ubuntu 24.04's AppArmor restriction on unprivileged user namespaces breaks
   AOSP's `nsjail` sandbox without an extra `sysctl`.
7. **Shallow sync — deferred.** The three blob repositories carry
   `clone-depth="1"`, as AOSPA's own beans do, but a depth-1 fetch of a pinned
   commit is untested. Detector: `repo sync` errors for these paths naming an
   unadvertised object, "not our ref" or a missing remote ref. Fallback: delete
   `clone-depth="1"` from that project and sync it again; at most the full
   history is fetched (GitHub reports about 1.8 GiB for the `ishtar` vendor
   repository and 0.3 GiB for `sm8550-common`).

`calcite` is evaluated only after `beryl` builds and boots.

## Use (on the build server)

The workspace runbook `docs/build-environment.md` is the procedure; the core is:

```sh
set -euo pipefail
repo init -u https://github.com/AOSPA/manifest -b beryl
test "$(git -C .repo/manifests rev-parse HEAD)" = 7dfc0650e27ec43b1d5cedf5e74213cf8667f2c2
git clone https://github.com/ahmetxa/android_local_manifests .repo/local_manifests
repo sync --current-branch --no-tags -j"$(nproc)"
./rom-build.sh ishtar -z
```

`repo init`, `repo sync` and `rom-build.sh` are AOSPA's documented commands;
`-z` also writes the fastboot image package.

## Checking

```sh
python3 check.py
```

Resolves every project against GitHub or GitLab: the commit must exist, be a
full id, and lie on its `upstream` branch. It also enforces the barista rules
above: a project at a beans path needs a preceding optional `remove-project`,
and every `remove-project` needs a replacement after it. Needs an authenticated
`gh` (set `GH=/path/to/gh` if it is not on `PATH`).
