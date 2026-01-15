# Codeforces CLI [WORK IN PROGRESS]

A simple command line tool to move your competitive programming workflow to your terminal.

![image](https://i.imgur.com/ZpLElvF.gif)

### How to install?

#### 1. Install using pip
```
$ pip install -U codeforces
$ cf --help
```

#### 2. Install from source (using uv)
```
$ git clone https://github.com/Nirlep5252/codeforces-cli
$ cd ./codeforces-cli
$ uv sync
$ uv run cf --help
```

**Note:** Chrome browser is required for authentication.

#### Authentication Note

Due to Cloudflare protection on Codeforces, authentication requires opening a browser window once. When you run `cf config` or first use `cf submit`, a browser will open for you to login. After successful login, your session is saved and subsequent commands will work without opening the browser again (until the session expires).

#### Current commands:

`cf config` - save your username and problems-directory (opens browser for login) \
`cf contests` - list all the current or upcoming contests \
`cf contests {ID}` - view all the problems of an ongoing contest \
`cf parse {Contest ID} {Problem ID | Optional} {--lang | Optional}` - parse the problem and its test cases \
`cf run {FILE}` - check the test cases for the current problem (works based on current directory) \
`cf submit {FILE}` - submit the problem (requires config) (works based on current directory) \
`cf unsolved` - return the list of all your unsolved problems \
`cf edit {CONTEST ID}` - open the contest folder in the editor of choice (only 3 supported so far)

#### TODO commands:

`cf standings {Contest ID | Optional}` - show all the standings of an ongoing of finished contests \
`cf suggest` - suggest a problem based on your current rating

#### TODO features:

- [ ] Support all languages in run
- [ ] A problem recommendation system, maybe?
