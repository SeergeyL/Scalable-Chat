# Create models in Cassandra
create-models:
	sudo docker-compose exec cassandra cqlsh -f scripts/model.cql
