# Peer to peer system with distributed index (P2P-DI)

## Run dev mode

Clone this repo : 

```bash
git clone git@github.ncsu.edu:pmgaikwa/p2p
```

Install virtualenv in your environment :

```bash
pip --user install virtualenv
```

Create virtualenv :

```bash
cd p2p
virtualenv --python=<path_to_python_3.7_executable> venv		# starts a virtualenv in "p2p" directory
```

Copy modules : 

```bash
cd p2p/deploy
./build.sh
```

Start virtualenv : 

```bash
cd p2p
source venv/bin/activate
```

Run tests :

```bash
cd p2p/tests/
python rs.py
python proto.py
```




