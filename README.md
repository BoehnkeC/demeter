Welcome to **Demeter**, a package for detecting burnt areas based on satellite imagery, following the methodology described by [UN-SPIDER](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio).

# Quickstart

## Workflow

The workflow of the algorithm is as follows:

- Define an AOI as a vector file, shapely Polygon or WKT.
- Define a start and ending date of the wildfire event.
- The algorithm automatically checks and downloads Sentinel-2 data from an AWS STAC catalog.
- In order to fully capture the event, the algorithm automatically re-assigns the start and end date to earlier and later dates before and after the event, based on the availability of data.
- The downloaded data is fed into a burnt area algorithm.

## Docker

Call the docker container with the following arguments:

```shell
docker run --rm -v /path/to/local/data/in/:/scratch/in/ -v /path/to/local/data/out/:/scratch/out/ demeter --aoi_data aoi_file.gpkg --start_date 2023-03-05 --end_date 2023-03-19
```

The directory `/path/to/local/data/in` must exist in the file system and may hold the AOI file. The directory `/path/to/local/data/out` will be created if not yet existing and stores downloaded Sentinel-2 imagery and the results in TIFF format.

The docker container was tested on Ubuntu 22.04.

## CLI

This package provides standalone CLI functionality.

```
usage: entrypoint.py [-h] --aoi_data AOI --out_dir OUT --start_date YYYY-MM-DD
                     --end_date YYYY-MM-DD [--cloud_cover CLOUD]

Fetch and apply Sentinel-2 data for burnt area mapping.

options:
  -h, --help            show this help message and exit
  --aoi_data AOI        AOI file with extension [GEOJSON, SHP, GPKG], AOI geometry as WKT,
                        Polygon or Multipolygon.
  --start_date YYYY-MM-DD
                        Begin of the event, as YYYY-MM-DD, like 2020-11-01
  --end_date YYYY-MM-DD
                        End of the event, as YYYY-MM-DD, like 2020-11-02
  --in_dir In           Path to input directory holding AOI file. Overrides Docker input.
  --out_dir OUT         Path to output directory. Overrides Docker output.
```

The CLI was tested on Ubuntu 22.04 and Windows 10.

## Results

#### Pre-fire NBR

<img src="docs/pre_nbr.png" width="300">

#### Post-fire NBR

<img src="docs/post_nbr.png" width="300">

#### NBR difference

<img src="docs/dnbr.png" width="300">

# Installation

Clone the repository.

```shell
git clone git@github.com:BoehnkeC/demeter.git
```

Build the docker container if on Ubuntu.

```shell
docker build -t demeter .
```

# Methodology

The algorithm applies the difference in Normalized Burn Ratio described by [UN-SPIDER](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio).

> The Normalized Burn Ratio (NBR) is an index designed to highlight burnt areas in large fire zones. The formula is similar to NDVI, except that the formula combines the use of both near infrared (NIR) and shortwave infrared (SWIR) wavelengths.



# Caveats

### Overpasses

Only download data that captures the AOI not only the data for the closest date.

### Present data

Check for data already downloaded saving computation time and limiting requests.

### Thresholding

In the current state, the results show continuous data. The results could be classified according to [UN-SPIDER](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio), despite the typo for not scaled Unburned.

![severity_level.PNG](docs/severity_level.PNG)

# Development

## Installing conda environment

```shell
git clone git@github.com:BoehnkeC/demeter.git
conda env create -f environment.yml
```

## pre-commit

Some development guardrails are enforced via [`pre-commit`](https://pre-commit.com/). This is to
ensure we follow similar code styles.

To install `pre-commit` (not necessary if you [installed the conda
environment](#Installation)):

```shell
conda/pip install pre-commit
```

To initialize all pre-commit hooks, run:

```shell
pre-commit install
```

To test whether `pre-commit` works:

```shell
pre-commit run --all-files
```

It will check all files tracked by git and apply the triggers set up in
[`.pre-commit-config.yaml`](.pre-commit-config.yaml). That is, it will run triggers, possibly
changing the contents of the file (e.g. `black` formatting). Once set up, `pre-commit` will run, as
the name implies, prior to each `git commit`. In its current config, it will format code with
`black` and `isort`, clean up `jupyter notebook` output cells, remove trailing whitespaces and will
block large files to be committed. If it fails, one has to re-stage the affected files (`git add` or
`git stage`), and re-commit.

# Why this name?

Demeter is the greek goddess of harvest, agriculture and, most importantly, _soil fertility_ of the earth. Wildfires not only burn vegetation but also alter soil characteristics and influence post-fire soil fertility.
