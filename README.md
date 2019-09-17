# Peer to peer system with distributed index (P2P-DI)

## Run dev mode

Clone this repo : 

```bash
git clone git@github.ncsu.edu:pmgaikwa/p2p p2p

# switch to directory
cd p2p
```

Install virtualenv on your box :

```bash
pip --user install virtualenv
```

Create virtualenv :

```bash
# create virtualenv
virtualenv --python=<path_to_python_3.7_executable> venv		# starts a virtualenv in "p2p" directory
```

Start virtualenv : 

```bash
# start venv
source venv/bin/activate
```

Install :

```bash
python setup.py install
```

Run tests :

```bash
python setup.py test
```

Run Registration Server alone :

```bash
# switch to server sub-directory
cd ./p2p/server/

# run server
python rs.py
```


