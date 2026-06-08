# ```linkedin-markdownificator```
Export your LinkedIn profile to Markdown. From there you can export it to PDF however you like.

>[!IMPORTANT]
> Without access to the API, this was developed using a ```selenium``` webdriver and manually downloading the source HTML for each page. This means that it can easily break if LinkedIn changes its interface.

## Basic usage
- Clone the repo
- Add your credentials to ```.env```
- Run ```python3 main.py```

## CLI options

```bash
python3 main.py --help
```

| Flag | Default | Description |
|------|---------|-------------|
| `--template` | `peppermint.md` | Jinja2 template to use |
| `--cached` | — | Skip scraping, use cached HTML |
| `--headless` | — | Run Chrome in headless mode |
| `--omit` | — | Sections to exclude from scraping (e.g. `--omit honors`) |
| `--json` | — | Export extracted data as JSON (e.g. `--json data/extracted.json`) |

## Testing

```bash
python3 -m pytest tests/ -v
```

## Lint & formatting

```bash
ruff check .
ruff format .
```

## Templates

There are currently two templates: ```default_template.md``` and ```peppermint.md```. Select one with ```--template```:

```bash
python3 main.py --template default_template.md
```

### ```peppermint```
Designed for Jekyll (uses [```minimal-mistakes```](https://github.com/mmistakes/minimal-mistakes)):
- [Live](https://rifusaki.co/CV/)
- [Markdown](https://github.com/rifusaki/linkedin-markdownificator/blob/main/examples/example-peppermint.md)
- [PDF](https://github.com/rifusaki/linkedin-markdownificator/blob/main/examples/example-peppermint.pdf)

### ```default_template```
- [Markdown](https://github.com/rifusaki/linkedin-markdownificator/blob/main/examples/example-default.md)
- [PDF](https://github.com/rifusaki/linkedin-markdownificator/blob/main/examples/example-default.pdf)

## FAQ
#### Just... why?
Mostly because updating both my LinkedIn profile and a separate CV sounds redundant. Tools like the now deprecated [LinkedIn2Md](https://github.com/fkztw/linkedin2md) only used the public profile which is quite incomplete. I wanted the full data.

#### Why not use the API?
Pretty much because, as far as I know, I can't. In order to get access to the Member Data Portability API, I need to have a legally registered company (see [the documentation](https://learn.microsoft.com/en-us/linkedin/dma/member-data-portability/member-data-portability-3rd-party/)). Or, as the access request form kindly puts it:

>  Please note that this product is only available for legal registered entities (e.g. LLC, Corporations, 501(c), etc.) and not individual developers.


