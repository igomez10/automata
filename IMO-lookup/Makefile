build:
	source .env
	docker build . \
	--tag imo-lookup \
	--build-arg _BASE_URL=${_BASE_URL} \
    --build-arg _AIRTABLE_API_KEY=${_AIRTABLE_API_KEY} \
    --build-arg _AIRTABLE_BASE_ID=${_AIRTABLE_BASE_ID} \

run:
	docker stop imo-lookup || true
	docker rm imo-lookup || true
	docker run \
	--name imo-lookup \
	--publish 8080:8080 \
	imo-lookup

test:
	make build
	make run &
	sleep 5
	curl 0.0.0.0:8080
	docker logs -f imo-lookup
