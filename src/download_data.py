"""
Reproducible acquisition of San Jose 311 Service Request Data.

Why a script instead of manual downloads: the portal issues signed, expiring
S3 redirect URLs per resource (not a stable direct link), so "just paste the
CSV link" breaks in a day. Resolving the redirect at run time is what makes
this reproducible for anyone who clones the repo.

Source: https://data.sanjoseca.gov/dataset/311-service-request-data
"""
import pathlib
import ssl
import sys
import urllib.request

import certifi

# macOS Python.org builds don't ship a CA bundle by default, so plain
# urlopen() fails cert verification. Point it at certifi's bundle explicitly
# rather than disabling verification (never disable TLS verification just to
# make a script run).
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class PortStrippingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    The portal's download endpoint 302s to a presigned S3 URL that spells
    out "s3.amazonaws.com:443" explicitly. AWS signs the request over the
    Host header as "s3.amazonaws.com" (no default port); urllib's redirect
    handler forwards the ":443" verbatim as the Host header, which no longer
    matches the signature and S3 returns 403. curl strips the default port
    before sending Host, which is why `curl -L` works but plain urllib
    doesn't. Stripping it here reproduces curl's behavior.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newurl = newurl.replace("s3.amazonaws.com:443", "s3.amazonaws.com")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(
    PortStrippingRedirectHandler,
    urllib.request.HTTPSHandler(context=SSL_CONTEXT),
)

RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"

# Resource IDs from the CKAN package_search API for package
# "5bd6605f-43fc-4ccc-b80b-3c15b5a02319" (311 Service Request Data).
# Pinned explicitly rather than "always grab latest N years" so the analysis
# is reproducible against a known snapshot even as new years are added.
RESOURCE_IDS = {
    2021: "4b0563f3-ed85-4889-8c39-05f160dbe0eb",
    2022: "0f26e09e-9e1f-4305-9d2d-fb5d8292ae8a",
    2023: "00b1c1ba-b83e-40a0-8260-e634c57e4fcc",
    2024: "ac55d3cd-b4fe-4f96-bf12-4ce3191c8bd4",
}

URL_TEMPLATE = (
    "https://data.sanjoseca.gov/dataset/5bd6605f-43fc-4ccc-b80b-3c15b5a02319"
    "/resource/{resource_id}/download/311-service-requests-{year}.csv"
)


def download_year(year: int, resource_id: str, dest_dir: pathlib.Path) -> pathlib.Path:
    dest = dest_dir / f"311-service-requests-{year}.csv"
    url = URL_TEMPLATE.format(resource_id=resource_id, year=year)
    req = urllib.request.Request(url, headers={"User-Agent": "sj311-analytics/1.0"})
    with _opener.open(req, timeout=90) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    return dest


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year, resource_id in RESOURCE_IDS.items():
        print(f"Downloading {year}...", file=sys.stderr)
        path = download_year(year, resource_id, RAW_DIR)
        size_mb = path.stat().st_size / 1_000_000
        print(f"  -> {path} ({size_mb:.1f} MB)", file=sys.stderr)


if __name__ == "__main__":
    main()
