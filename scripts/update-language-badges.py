#!/usr/bin/env python3

import re
import urllib.request
from pathlib import Path
from urllib.parse import quote

import yaml


LINGUIST_URL = (
    "https://raw.githubusercontent.com/"
    "github-linguist/linguist/main/lib/linguist/languages.yml"
)

README = Path("README.md")
CONFIG = Path("language-badges.yml")

START_MARKER = "<!-- LANGUAGES:START -->"
END_MARKER = "<!-- LANGUAGES:END -->"


def load_linguist():
    print("Downloading current GitHub Linguist language definitions...")

    request = urllib.request.Request(
        LINGUIST_URL,
        headers={
            "User-Agent": "GitHub-Language-Badge-Updater"
        },
    )

    with urllib.request.urlopen(request) as response:
        return yaml.safe_load(
            response.read().decode("utf-8")
        )


def find_language(name, linguist):
    if name in linguist:
        return linguist[name]

    name_lower = name.lower()

    for language, data in linguist.items():
        aliases = data.get("aliases", []) or []

        if any(alias.lower() == name_lower for alias in aliases):
            return data

    return None

def build_badge(language, colour, badge_config):
    name = language["name"]
    logo = language["logo"]
    url = language["url"]

    style = badge_config["style"]
    logo_colour = badge_config["logoColor"]
    label_colour = badge_config["labelColor"]

    badge_label = name.replace("#", "%23")
    badge_message = colour.lstrip("#")

    if logo.startswith("data:image/"):
        logo_parameter = logo
    else:
        logo_parameter = quote(logo)

    badge_url = (
        f"https://img.shields.io/badge/"
        f"{badge_label}-{badge_message}"
        f"?style={quote(style)}"
        f"&logo={logo_parameter}"
        f"&logoColor={quote(logo_colour)}"
        f"&labelColor={quote(label_colour)}"
    )

    return f"[![{name}]({badge_url})]({url})"


def build_badges(config, linguist):
    badges = []

    for language in config["languages"]:
        name = language["name"]

        definition = find_language(name, linguist)

        if definition is None:
            raise RuntimeError(
                f"'{name}' was not found in GitHub Linguist."
            )

        colour = definition.get("color")

        if not colour:
            raise RuntimeError(
                f"'{name}' exists in GitHub Linguist but has no colour."
            )

        print(f"{name}: {colour}")

        badges.append(
            build_badge(
                language,
                colour,
                config["badge"],
            )
        )

    return "\n".join(badges)


def update_readme(badges):
    content = README.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START_MARKER)
        + r".*?"
        + re.escape(END_MARKER),
        re.DOTALL,
    )

    replacement = (
        f"{START_MARKER}\n"
        f"{badges}\n"
        f"{END_MARKER}"
    )

    updated, count = pattern.subn(
        replacement,
        content,
    )

    if count != 1:
        raise RuntimeError(
            "Expected exactly one language badge section "
            "in README.md."
        )

    README.write_text(
        updated,
        encoding="utf-8",
    )


def main():
    if not CONFIG.exists():
        raise RuntimeError(
            f"Configuration file not found: {CONFIG}"
        )

    if not README.exists():
        raise RuntimeError(
            f"README file not found: {README}"
        )

    config = yaml.safe_load(
        CONFIG.read_text(encoding="utf-8")
    )

    if not config.get("languages"):
        raise RuntimeError(
            "No languages configured in language-badges.yml."
        )

    linguist = load_linguist()
    badges = build_badges(config, linguist)
    update_readme(badges)

    print("README.md updated successfully.")


if __name__ == "__main__":
    main()
