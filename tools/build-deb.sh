#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
# Build the edukasaun-desktop-menu .deb from this repository.
#   sh tools/build-deb.sh            -> dist/edukasaun-desktop-menu_<version>_all.deb
# The version comes from DEBIAN/control, so bump it there, DEB_VERSION in
# eduka_common.py and the first entry of packaging/changelog for each release.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PKG=$(sed -n 's/^Package: *//p' "$ROOT/DEBIAN/control")
VER=$(sed -n 's/^Version: *//p' "$ROOT/DEBIAN/control")
LIBVER=$(sed -n 's/^DEB_VERSION = "\(.*\)"/\1/p' "$ROOT/usr/lib/edukasaun-desktop/eduka_common.py")
if [ "$VER" != "$LIBVER" ]; then
    echo "Version mismatch: DEBIAN/control=$VER eduka_common.py=$LIBVER" >&2
    exit 1
fi

OUT="$ROOT/dist"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$OUT"

# Only package payload directories; README files, docs/, tools/ and .git
# stay out.
cp -a "$ROOT/DEBIAN" "$ROOT/etc" "$ROOT/usr" "$STAGE/"
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGE" -name '*.pyc' -delete

# Debian documentation: changelog (this is a native package) and the
# manual pages of every command, compressed the way dpkg expects.
DOC="$STAGE/usr/share/doc/$PKG"
mkdir -p "$DOC" "$STAGE/usr/share/man/man1"
CHANGELOG_VER=$(sed -n '1s/^[^ ]* (\([^)]*\)).*/\1/p' "$ROOT/packaging/changelog")
if [ "$CHANGELOG_VER" != "$VER" ]; then
    echo "packaging/changelog starts with $CHANGELOG_VER, DEBIAN/control says $VER" >&2
    exit 1
fi
gzip -9n < "$ROOT/packaging/changelog" > "$DOC/changelog.gz"
python3 "$ROOT/tools/gen-manpages.py" "$STAGE/usr/share/man/man1"
gzip -9n "$STAGE"/usr/share/man/man1/*.1

# Git stores these files as 0644; dpkg needs executable maintainer scripts
# and programs.
find "$STAGE" -type d -exec chmod 0755 {} +
find "$STAGE" -type f -exec chmod 0644 {} +
chmod 0755 "$STAGE"/usr/bin/*
chmod 0755 "$STAGE"/usr/lib/edukasaun-desktop/live-autologin
chmod 0755 "$STAGE"/usr/lib/edukasaun-desktop/eduka-sddm-apply
chmod 0755 "$STAGE"/usr/lib/edukasaun-desktop/eduka-parental-apply "$STAGE"/usr/lib/edukasaun-desktop/eduka-parental-daemon
for s in preinst postinst prerm postrm; do
    [ -f "$STAGE/DEBIAN/$s" ] && chmod 0755 "$STAGE/DEBIAN/$s"
done

# Syntax-check every Python program before packaging.
for f in "$STAGE"/usr/bin/* "$STAGE"/usr/lib/edukasaun-desktop/*.py "$STAGE"/usr/lib/edukasaun-desktop/eduka-parental-*; do
    if head -n1 "$f" | grep -q python; then
        python3 - "$f" <<'PY'
import ast, sys
ast.parse(open(sys.argv[1], encoding='utf-8').read(), sys.argv[1])
PY
    fi
done
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +

# Keep Installed-Size (KiB) accurate.
SIZE=$(du -sk --exclude=DEBIAN "$STAGE" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: $SIZE/" "$STAGE/DEBIAN/control"

# md5sums lets `debsums`/`dpkg --verify` check the installed files; dpkg
# keeps the checksums of conffiles itself.
(cd "$STAGE" && find etc usr -type f -print0 | sort -z | xargs -0 md5sum > DEBIAN/md5sums.all
 sed 's|^/||' DEBIAN/conffiles > DEBIAN/conffiles.rel
 awk 'NR==FNR {skip[$0]=1; next} !(substr($0, 35) in skip)' DEBIAN/conffiles.rel DEBIAN/md5sums.all > DEBIAN/md5sums
 rm -f DEBIAN/conffiles.rel DEBIAN/md5sums.all)
chmod 0644 "$STAGE/DEBIAN/md5sums" "$STAGE/DEBIAN/conffiles"

DEB="$OUT/${PKG}_${VER}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$DEB"
echo "Built $DEB"
