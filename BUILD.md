## Generating distribution archives

```shell
python3 -m pip install --upgrade build
```

```shell
python3 -m build
```

## Uploading the distribution archives

```shell
python3 -m pip install --upgrade twine
```

```shell
python3 -m twine upload --repository testpypi dist/*
```

## Installing the uploaded distribution from Test PyPI

```shell
pip install -i https://test.pypi.org/simple/ sri
```