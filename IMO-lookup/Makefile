build:
	docker build . \
	--tag imo-lookup \
	--build-arg _BASE_URL=${_BASE_URL} \
    --build-arg _AIRTABLE_API_KEY=${_AIRTABLE_API_KEY} \
    --build-arg _AIRTABLE_BASE_ID=${_AIRTABLE_BASE_ID} \
	--build-arg PROJECT_ID=${PROJECT_ID} \
	--build-arg _SUB_PUB_TOPIC_NAME=${_SUB_PUB_TOPIC_NAME} \
	
run:
	docker stop imo-lookup || true
	docker rm imo-lookup || true
	docker run \
	--name imo-lookup \
	--publish 8080:8080 \
	-e GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}  \
	--volume ${GOOGLE_APPLICATION_CREDENTIALS}:${GOOGLE_APPLICATION_CREDENTIALS} \
	imo-lookup

test:
	make build
	make run &
	sleep 5
	curl 0.0.0.0:8080
	docker logs -f imo-lookup
