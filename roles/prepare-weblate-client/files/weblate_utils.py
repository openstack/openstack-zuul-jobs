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

"""Shared helpers for talking to the Weblate REST API.

This is the Weblate counterpart of ZanataUtils.py: the translation
scripts import the config reader and the API client from here instead of
each rolling its own.

Only the read-only calls the translation jobs need are provided. The
calls that create projects, categories and components live in the i18n
repository, which is where the upload side of the workflow is kept.
"""

import configparser
import json
import re

import requests


class SimpleIniConfig:
    """Read Weblate URL and API key from weblate.ini (wlc format)."""

    def __init__(self, inifile):
        config = configparser.ConfigParser(delimiters=("=",))
        config.read(inifile)
        self.url = config.get("weblate", "url").strip().rstrip("/")
        # API key is optional. Without it the client operates anonymously,
        # which Weblate allows for read-only access to public projects
        # (write operations like setup/upload will then fail with HTTP 401).
        self.key = None
        # Format 1: [weblate] section has key directly (Zuul template)
        if config.has_option("weblate", "key"):
            self.key = config.get("weblate", "key").strip() or None
        # Format 2: [keys] section maps URL -> token (wlc format)
        elif config.has_section("keys"):
            for url, key in config.items("keys"):
                if url.startswith(("http://", "https://")):
                    self.key = key.strip() or None
                    break


class WeblateSetup:
    """Create Weblate projects and categories via REST API."""

    def __init__(self, wconfig, verify=True):
        # Ensure base URL ends with /api
        url = wconfig.url.rstrip("/")
        if not url.endswith("/api"):
            url = url + "/api"
        self.api_base = url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # Only authenticate when a key is present. Weblate rejects an empty
        # or invalid token with HTTP 401, so for anonymous (read-only) use
        # we must omit the Authorization header rather than send "Token ".
        if getattr(wconfig, "key", None):
            self.headers["Authorization"] = "Token " + wconfig.key
        self.verify = verify

    def _api_url(self, path):
        return f"{self.api_base}/{path.lstrip('/')}"

    def _get(self, path):
        resp = requests.get(
            self._api_url(path),
            headers=self.headers,
            verify=self.verify,
        )
        return resp

    def _post(self, path, data):
        resp = requests.post(
            self._api_url(path),
            headers=self.headers,
            data=json.dumps(data),
            verify=self.verify,
        )
        return resp

    # -- Project ----------------------------------------------------------

    def get_project(self, slug):
        """Check if a project exists. Returns response."""
        return self._get(f"projects/{slug}/")

    # -- Category ---------------------------------------------------------

    def list_categories(self, project_slug):
        """List existing categories for a project."""
        resp = self._get(f"projects/{project_slug}/categories/")
        if resp.status_code == 200:
            return resp.json().get("results", [])
        return []

    # -- Component --------------------------------------------------------

    def get_category_url(self, project_slug, category_slug):
        """Get the API URL for a category."""
        categories = self.list_categories(project_slug)
        for cat in categories:
            if cat.get("slug") == category_slug:
                return cat.get("url")
        return None

    def list_components(self, project_slug):
        """List all components in a project (paginated)."""
        components = []
        path = f"projects/{project_slug}/components/"
        while path:
            resp = self._get(path)
            if resp.status_code != 200:
                break
            data = resp.json()
            components.extend(data.get("results", []))
            next_url = data.get("next")
            if next_url:
                # next_url is absolute, extract the path after /api/
                path = next_url.split("/api/", 1)[-1]
            else:
                path = None
        return components


def slugify_branch(branch):
    """Convert branch name to Weblate slug.

    e.g., stable/2026.01 -> stable-2026-01
    Only letters, numbers, underscores, and hyphens are allowed.
    """
    slug = branch.replace("/", "-")
    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", slug)
    return slug
