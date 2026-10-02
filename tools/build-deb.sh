#!/bin/sh
# Build the edukasaun-desktop-menu .deb from this repository.
#   sh tools/build-deb.sh            -> dist/edukasaun-desktop-menu_<version>_all.deb
# The version comes from DEBIAN/control, so bump it there (and VERSION in
# eduka_common.py) for each release.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PKG=$(sed -n 's/^Package: *//p' "$ROOT/DEBIAN/control")
VER=$(sed -n 's/^Version: *//p' "$ROOT/DEBIAN/control")
LIBVER=$(sed -n 's/^VERSION = "\(.*\)"/\1/p' "$ROOT/usr/lib/edukasaun-desktop/eduka_common.py")
if [ "$VER" != "$LIBVER" ]; then
    echo "Version mismatch: DEBIAN/control=$VER eduka_common.py=$LIBVER" >&2
    exit 1
fi

OUT="$ROOT/dist"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$OUT"

# Only package payload directories; README files, tools/ and .git stay out.
cp -a "$ROOT/DEBIAN" "$ROOT/etc" "$ROOT/usr" "$STAGE/"
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGE" -name '*.pyc' -delete

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

# md5sums lets `debsums`/`dpkg --verify` check the installed files.
(cd "$STAGE" && find etc usr -type f -print0 | sort -z | xargs -0 md5sum > DEBIAN/md5sums)
chmod 0644 "$STAGE/DEBIAN/md5sums"

DEB="$OUT/${PKG}_${VER}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$DEB"
echo "Built $DEB"
