## Codeforces CLI [WORK IN PROGRESS]

A simple command line tool to move your competitive programming workflow to your terminal.

#### Current commands:

`python main.py contests` - list all the current or upcoming contests \
`python main.py contests {ID}` - view all the problems of an ongoing contest \
`python main.py parse {Contest ID} {Problem ID | Optional}` - parse the problem and its test cases

#### TODO commands:

`python main.py run` - check the test cases for the current problem (works based on current directory) \
`python main.py config` - save your username, password, problems-directory \
`python main.py submit` - submit the problem (requires config) (works based on current directory) \
`python main.py standings` - show all the standings of an ongoing of finished contests 
