## Codeforces CLI [WORK IN PROGRESS]

A simple command line tool to move your competitive programming workflow to your terminal.

### How to install?

#### 1. Install using pip
```
$ pip install -U codeforces
$ cf --help
```

#### 2. Install from source
- Clone the repo
```
$ git clone https://github.com/Nirlep5252/codeforces-cli
```

- Install it
```
$ cd ./codeforces-cli
$ python3 -m pip install build
$ python3 -m build
$ python3 -m pip install dist/codeforces-0.0.1-py3-none-any.whl --force-reinstall
```

- Happy coding!
```
$ cf --help
```

#### Current commands:

`cf config` - save your username, password, problems-directory \
`cf contests` - list all the current or upcoming contests \
`cf contests {ID}` - view all the problems of an ongoing contest \
`cf parse {Contest ID} {Problem ID | Optional}` - parse the problem and its test cases \
`cf run {FILE}` - check the test cases for the current problem (works based on current directory) \
`cf submit {FILE}` - submit the problem (requires config) (works based on current directory)

#### TODO commands:

`cf standings {Contest ID | Optional}` - show all the standings of an ongoing of finished contests \
`cf suggest` - suggest a problem based on your current rating

#### TODO features:

- [ ] Support all languages in run and submit
- [ ] Watch submission status in real time
- [ ] Add a templating system
- [ ] A problem recommendation system, maybe?
