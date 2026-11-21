#!/usr/bin/env python3
"""Builds the production package: dist/dnaproplans-production.zip

The zip holds wrangler.jsonc, DEPLOY.md and public/ (the files Cloudflare serves).
Usage: python3 tools/package.py
"""
import pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PKG = DIST / "dnaproplans-production"
PUBLIC_FILES = ["styles.css", "main.js", "consent.js", "favicon.svg", "apple-touch-icon.png", "robots.txt", "sitemap.xml", "version.txt"]
PUBLIC_DIRS = ["images", "icons", "fonts"]

subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), str(ROOT)], check=True, stdout=subprocess.DEVNULL)
shutil.rmtree(DIST, ignore_errors=True)
(PKG / "public").mkdir(parents=True)
for f in sorted(ROOT.glob("*.html")):
    shutil.copy2(f, PKG / "public" / f.name)
for f in PUBLIC_FILES:
    shutil.copy2(ROOT / f, PKG / "public" / f)
for d in PUBLIC_DIRS:
    shutil.copytree(ROOT / d, PKG / "public" / d)
shutil.copy2(ROOT / "wrangler.jsonc", PKG / "wrangler.jsonc")
shutil.copy2(ROOT / "DEPLOY.md", PKG / "DEPLOY.md")
shutil.make_archive(str(DIST / "dnaproplans-production"), "zip", DIST, "dnaproplans-production")
n = sum(1 for p in (PKG / "public").rglob("*") if p.is_file())
print(f"{DIST / 'dnaproplans-production.zip'}: {n} public files, build {(ROOT / 'version.txt').read_text().strip()}")
