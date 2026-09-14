#!/usr/bin/env python3

import re
import urllib.request
from pathlib import Path

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

```
with urllib.request.urlopen(LINGUIST_URL) as response:
    data = response.read().decode("utf-8")

return yaml.safe_load(data)
```

def badge_url(name, colour, config):
style = config["badge"]["style"]
logo_colour = config["badge"]["logoColor"]
label_colour = config["badge"]["labelColor"]

```
label = name.replace("-", "--").replace(" ", "_")
encoded_name = name.replace("#", "%23")

return (
    f"https://img.shields.io/badge/"
    f"{encoded_name}-{colour.lstrip('#')}?"
    f"style={style}"
    f"&logo={name}"
    f"&logoColor={logo_colour}"
    f"&labelColor={label_colour}"
)
```

def find_language(name, linguist):
if name in linguist:
return linguist[name]

```
# Try aliases as a fallback.
name_lower = name.lower()

for language, data in linguist.items():
    aliases = data.get("aliases", []) or []

    if any(alias.lower() == name_lower for alias in aliases):
        return data

return None
```

def build_badges(config, linguist):
badges = []

```
for name in config["languages"]:
    language = find_language(name, linguist)

    if language is None:
        raise RuntimeError(f"'{name}' was not found in GitHub Linguist.")

    colour = language.get("color")

    if not colour:
        raise RuntimeError(f"'{name}' exists in GitHub Linguist but has no colour.")

    url = badge_url(name, colour, config)

    badges.append(
        f"[![{name}]({url})](https://github.com/search?q=language%3A"
        f"{name.replace('#', '%23')}&type=repositories)"
    )

    print(f"{name}: {colour}")

return "\n".join(badges)
```

def update_readme(badges):
content = README.read_text(encoding="utf-8")

```
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

updated, count = pattern.subn(replacement, content)

if count != 1:
    raise RuntimeError("Expected exactly one language badge section in README.md.")

README.write_text(updated, encoding="utf-8")
```

def main():
config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

```
linguist = load_linguist()
badges = build_badges(config, linguist)
update_readme(badges)

print("README.md updated successfully.")
```

if **name** == "**main**":
main()
