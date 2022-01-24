# Translation API

- /translate
- /glossary/remote-work
- /quality-estimation

## Production Build

Install Docker then...

```bash
docker-compose --build
```

## Development environment

```bash
conda update -y -n base -c defaults conda
conda create -y -n fastapienv 'python==3.8.8'
conda env update -n fastapienv -f environment.yml
conda activate fastapienv
```
