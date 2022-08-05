# Courseware/Professor-Student WebApp

## Installation:

1. Head to [this link](https://github.com/AhmadRafiee/Kubernetes_training_with_DockerMe/blob/main/vagrant/vagrant-and-packer.md) in order to get the vagrant, packer and virtualbox running.
2. Run the commands bellow in shell:

```shell
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. Don't forget to include your own `credentials.json` inside `./courseware/` in order for the mailing feature to work.

## Updates to come:

- Instructions to get the server up and running via `uvicorn` and `nginx` in a `virtual machine`.

- Don't forget share with your friends.
- Please give this project a `Star` in case you enjoyed it or it was useful for you.
