#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Download translations from Weblate and place them in the source tree.

For each component in a Weblate category (branch):
  1. List available translations (languages)
  2. Download PO files
  3. Place them in the correct locale directory
  4. Stage files with git add

The Weblate server URL must be provided in one of the following ways:
configure it in the weblate client config file, pass --url, or set the
WEBLATE_URL environment variable.

Usage:
    python3 download_translations_weblate.py \
        --project contributor-guide \
        --category master \
        --url https://weblate.example.org
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

from weblate_utils import SimpleIniConfig
from weblate_utils import slugify_branch
from weblate_utils import WeblateSetup


def component_to_target(comp_slug):
    """Map component slug to (target_dir_base, po_filename).

    This is the reverse of upload_pot_weblate.py's pot_to_component_slug().

    Django modules:
        horizon-django       -> (horizon/locale, django.po)
        openstack-dashboard-djangojs
            -> (openstack_dashboard/locale, djangojs.po)
    Releasenotes:
        releasenotes -> (releasenotes/source/locale,
                         releasenotes.po)
    Doc components:
        doc          -> (doc/source/locale, doc.po)
        doc-code-and-documentation
            -> (doc/source/locale,
                doc-code-and-documentation.po)
    """
    # Django module pattern: {module}-(django|djangojs)
    m = re.match(r'^(.+)-(django|djangojs)$', comp_slug)
    if m:
        module_slug = m.group(1)
        domain = m.group(2)
        module_name = module_slug.replace('-', '_')
        return os.path.join(module_name, "locale"), f"{domain}.po"

    # Releasenotes
    if comp_slug == "releasenotes":
        return (
            os.path.join("releasenotes", "source", "locale"),
            "releasenotes.po",
        )

    # Doc components (default): doc, doc-admin, etc.
    return (
        os.path.join("doc", "source", "locale"),
        f"{comp_slug}.po",
    )


def list_translations(setup, project_slug, comp_path):
    """List non-source languages for a component."""
    languages = []
    path = f"components/{project_slug}/{comp_path}/translations/"
    while path:
        resp = setup._get(path)
        if resp.status_code != 200:
            print(
                f"  [warn] list translations failed: "
                f"HTTP {resp.status_code}"
            )
            break
        data = resp.json()
        for t in data.get("results", []):
            lang = t.get("language", {}).get("code", "")
            if lang and lang not in ("en", "en_US"):
                languages.append(lang)
        next_url = data.get("next")
        if next_url:
            path = next_url.split("/api/", 1)[-1]
        else:
            path = None
    return languages


def download_po(setup, project_slug, comp_path, language, output_file):
    """Download a PO file for a specific language."""
    url = setup._api_url(
        f"translations/{project_slug}/{comp_path}/{language}/file/"
    )
    try:
        resp = setup.session.get(
            url, headers=setup.headers, verify=setup.verify, stream=True
        )
    except AttributeError:
        import requests
        resp = requests.get(
            url, headers=setup.headers, verify=setup.verify, stream=True
        )
    if resp.status_code == 200 and len(resp.content) > 0:
        with open(output_file, 'wb') as f:
            f.write(resp.content)
        return True
    else:
        print(
            f"  [warn] download failed for {language}: "
            f"HTTP {resp.status_code}"
        )
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download translations from Weblate"
    )
    parser.add_argument("--config", default="~/.config/weblate")
    parser.add_argument(
        "--project", required=True,
        help="Weblate project slug",
    )
    parser.add_argument(
        "--category", required=True,
        help="Branch name (e.g., master)",
    )
    parser.add_argument(
        "--url", default=os.environ.get("WEBLATE_URL"),
        help="Weblate API URL. Overrides the config file and enables "
             "anonymous use without a config file or token (read-only "
             "access to public projects). Defaults to $WEBLATE_URL.",
    )
    args = parser.parse_args()

    # Download is read-only, so it can run anonymously. Resolve config from
    # the file when present; otherwise fall back to --url / $WEBLATE_URL.
    config_path = os.path.expanduser(args.config)
    if os.path.exists(config_path):
        wconfig = SimpleIniConfig(config_path)
        if args.url:
            wconfig.url = args.url.rstrip("/")
    elif args.url:
        wconfig = SimpleNamespace(url=args.url.rstrip("/"), key=None)
    else:
        parser.error(
            f"no config file at {config_path} and no --url/$WEBLATE_URL set"
        )
    setup = WeblateSetup(wconfig)
    if not getattr(wconfig, "key", None):
        print("[download] No API token; running anonymously (read-only).")

    category_slug = slugify_branch(args.category)
    project_slug = args.project

    # List all components in the project
    all_components = setup.list_components(project_slug)
    if not all_components:
        print(f"[download] No components found for project {project_slug}")
        sys.exit(1)

    # Filter to components in our target category
    target_cat_url = setup.get_category_url(project_slug, category_slug)
    components = []
    for c in all_components:
        comp_cat = c.get("category") or ""
        if comp_cat == target_cat_url:
            components.append(c)

    if not components:
        print(f"[download] No components in category '{category_slug}'")
        print(f"  (total components in project: {len(all_components)})")
        sys.exit(1)

    print(f"[download] Found {len(components)} component(s) "
          f"in {project_slug}/{category_slug}")

    results = {"downloaded": 0, "skipped": 0, "failed": 0}

    with tempfile.TemporaryDirectory() as work_dir:
        for comp in components:
            slug = comp.get("slug", "")
            if slug == "glossary":
                continue

            # Component API path includes category: category%2Fslug
            comp_path = f"{category_slug}%252F{slug}"
            print(f"\n--- {slug} ---")

            # List languages
            languages = list_translations(setup, project_slug, comp_path)
            if not languages:
                print("  No translations")
                results["skipped"] += 1
                continue

            print(f"  Languages: {', '.join(languages)}")

            # Map component to target directory
            target_base, po_filename = component_to_target(slug)

            for lang in languages:
                temp_file = os.path.join(work_dir, f"{slug}_{lang}.po")
                if download_po(
                    setup, project_slug, comp_path,
                    lang, temp_file,
                ):
                    target_dir = os.path.join(
                        target_base, lang, "LC_MESSAGES"
                    )
                    os.makedirs(target_dir, exist_ok=True)
                    dest = os.path.join(target_dir, po_filename)
                    # shutil.move handles the case where the tempdir and the
                    # source tree live on different filesystems.
                    shutil.move(temp_file, dest)
                    results["downloaded"] += 1
                else:
                    results["failed"] += 1

            # Git add locale files for this component
            locale_dir = target_base
            if os.path.isdir(locale_dir):
                subprocess.run(
                    ["git", "add", "--all", locale_dir],
                    check=False,
                )

    print(f"\n{'=' * 50}")
    print("Download complete:")
    print(f"  Downloaded: {results['downloaded']}")
    print(f"  Skipped:    {results['skipped']}")
    print(f"  Failed:     {results['failed']}")


if __name__ == "__main__":
    main()
