# ishtar on AOSPA beryl — local manifests

Local manifests for building AOSPA `beryl` (Android 16) for the Xiaomi 13 Ultra
(`ishtar`) on a rented build server. Planning, decisions and evidence live in the
private workspace repository `ahmetxa/ishtar` (ledger `DEC-24`, Main-Planing
Phase 7).

**Status: INCOMPLETE — not buildable yet.** The pinned projects below resolve;
the open items at the bottom must be closed before a server is rented.

## Why only one repository is copied

Every `beryl` input already exists publicly under `xiaomi-8550`. A build server
downloads those at datacenter speed, so copying multi-gigabyte blob repositories
into this account would not shorten the rental. Reproducibility comes from
pinning each project to a full commit id instead. The only repository hosted
here is the device tree, because it carries a project change.

## Pinned projects (resolved 2026-09-10)

| Path | Repository | Branch | Commit | Note |
|---|---|---|---|---|
| `device/xiaomi/ishtar` | `ahmetxa/android_device_xiaomi_ishtar` | `beryl` | `d48816fb14984939f7152106f5352536619999b2` | Upstream `xiaomi-8550` `df05661` plus one commit: `aon_front.pb` as a symlink entry |
| `device/xiaomi/sm8550-common` | `xiaomi-8550/android_device_xiaomi_sm8550-common` | `beryl` | `a0a7042263ff429afce199a945e50a9279f19822` | Upstream tip |
| `vendor/xiaomi/ishtar` | `xiaomi-8550/proprietary_vendor_xiaomi_ishtar` | `beryl` | `f92e7a907d4e46f65f2ffca2efc24f227e07a28a` | Upstream tip, about 1.9 GB |
| `vendor/xiaomi/sm8550-common` | `xiaomi-8550/proprietary_vendor_xiaomi_sm8550-common` | `beryl` | `e0d20e8f29042e07ab778accab444bbbd4fb6040` | Upstream tip |

The trees' blob lists name their source firmware: `OS2.0.101.0.VMAMIXM` for
`ishtar`, `OS2.0.100.0.VMCMIXM` (from `fuxi`) for the common tree.

## Open items

1. **`hardware/xiaomi`.** The trees reference it; `xiaomi-8550/android_hardware_xiaomi`
   has no `beryl` branch (it has `vauxite` and `calcite`). Which one builds with
   `beryl` is not yet known.
2. **`device/xiaomi/sepolicy`.** The common tree includes
   `device/xiaomi/sepolicy/SEPolicy.mk`; `xiaomi-8550/device_xiaomi_sepolicy`
   has only `uvite`.
3. **Kernel.** `xiaomi-8550/android_kernel_qcom_sm8550` (`b11e560`) and
   `xiaomi-8550/android_kernel_xiaomi_sm8550` (`1c509b3`) have `beryl` branches,
   but the paths the build expects them at, and the QCOM driver and devicetree
   repositories that go with them, are not yet determined.
4. **QCOM overrides.** `xiaomi-8550` carries `android_hardware_qcom_display` and
   `android_vendor_qcom_opensource_arpal-lx` on `beryl-8550`. Whether they must
   replace projects from AOSPA's own manifest is not yet determined.
5. **`vendor/xiaomi/camera`.** Included only if present
   (`inherit-product-if-exists`); the `xiaomi-8550` repository for it is empty.
   Probably not needed.
6. **Server distribution.** Decide from the AOSPA build requirements before
   renting (workspace ledger `DEC-22`).
7. **Shallow sync** for the 1.9 GB vendor repository is untested.

`calcite` is evaluated only after `beryl` builds and boots.

## Use (on the build server, once the open items are closed)

```sh
gh auth login          # the device tree repository is private
gh auth setup-git
repo init -u https://github.com/AOSPA/manifest -b beryl
git clone https://github.com/ahmetxa/android_local_manifests .repo/local_manifests
repo sync --current-branch --no-tags -j4
./rom-build.sh ishtar
```

The `repo init`, `repo sync` and `rom-build.sh` lines are AOSPA's documented
commands; on a large server raise `-j`.

## Checking

```sh
python3 check.py
```

Resolves every project against GitHub: the commit must exist, be a full id, and
lie on its `upstream` branch. It also says when a branch has moved past its pin.
Needs an authenticated `gh` (set `GH=/path/to/gh` if it is not on `PATH`).
