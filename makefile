.PHONY:db
db:
		docker-compose -f docker-compose.db.yaml up -d

.PHONY:pkgs
pkgs:
		pip3 install -r requirements.txt